"""AWS Transcribe連携モジュール."""

import os
import time
import uuid
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError


# 環境変数またはデフォルト設定
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
S3_BUCKET = os.getenv("TRANSCRIBE_S3_BUCKET", "presentation-feedback")
S3_PREFIX = "input/"


def _upload_to_s3(audio_file_path: str, s3_client, bucket: str, key: str) -> str:
    """
    音声ファイルをS3にアップロード.

    Args:
        audio_file_path: ローカル音声ファイルパス
        s3_client: boto3 S3クライアント
        bucket: S3バケット名
        key: S3オブジェクトキー

    Returns:
        str: S3 URI (s3://bucket/key)
    """
    try:
        s3_client.upload_file(audio_file_path, bucket, key)
        s3_uri = f"s3://{bucket}/{key}"
        print(f"✓ S3にアップロード完了: {s3_uri}")
        return s3_uri
    except ClientError as e:
        raise RuntimeError(f"S3アップロードエラー: {e}") from e


def _start_transcription_job(
    transcribe_client,
    job_name: str,
    s3_uri: str,
    language_code: str,
) -> None:
    """
    AWS Transcriptionジョブを開始.

    Args:
        transcribe_client: boto3 Transcribeクライアント
        job_name: ジョブ名
        s3_uri: 音声ファイルのS3 URI
        language_code: 言語コード
    """
    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            MediaFormat="mp3",  # 拡張子から自動判定も可能
            LanguageCode=language_code,
            Settings={
                "ShowSpeakerLabels": False,  # Phase 1では話者分離なし
                "MaxSpeakerLabels": 1,
            },
        )
        print(f"✓ Transcriptionジョブ開始: {job_name}")
    except ClientError as e:
        raise RuntimeError(f"Transcriptionジョブ開始エラー: {e}") from e


def _wait_for_job_completion(transcribe_client, job_name: str) -> Dict:
    """
    Transcriptionジョブの完了を待機.

    Args:
        transcribe_client: boto3 Transcribeクライアント
        job_name: ジョブ名

    Returns:
        dict: ジョブステータス情報
    """
    print("⏳ 書き起こし処理中...", end="", flush=True)
    while True:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        status = response["TranscriptionJob"]["TranscriptionJobStatus"]

        if status == "COMPLETED":
            print(" 完了!")
            return response["TranscriptionJob"]
        elif status == "FAILED":
            failure_reason = response["TranscriptionJob"].get(
                "FailureReason", "不明なエラー"
            )
            raise RuntimeError(f"Transcription失敗: {failure_reason}")

        print(".", end="", flush=True)
        time.sleep(5)


def _parse_transcription_result(job_result: Dict) -> Dict:
    """
    Transcription結果をパースして必要な形式に変換.

    Args:
        job_result: AWS Transcribeのジョブ結果

    Returns:
        dict: パース済み書き起こし結果
    """
    import requests

    # 結果JSONのURLを取得
    transcript_uri = job_result["Transcript"]["TranscriptFileUri"]
    response = requests.get(transcript_uri)
    response.raise_for_status()
    transcript_data = response.json()

    # 全文テキスト
    full_text = transcript_data["results"]["transcripts"][0]["transcript"]

    # セグメント情報を抽出
    segments = []
    items = transcript_data["results"]["items"]

    current_segment = {"text": "", "start_time": None, "end_time": None}

    for item in items:
        if item["type"] == "pronunciation":
            word = item["alternatives"][0]["content"]
            start_time = float(item["start_time"])
            end_time = float(item["end_time"])
            confidence = float(item["alternatives"][0]["confidence"])

            # セグメント開始
            if current_segment["start_time"] is None:
                current_segment["start_time"] = start_time

            current_segment["text"] += word
            current_segment["end_time"] = end_time
            current_segment["confidence"] = confidence

        elif item["type"] == "punctuation":
            # 句読点は直前の単語に追加
            current_segment["text"] += item["alternatives"][0]["content"]

            # 句読点でセグメント区切り
            if current_segment["text"]:
                segments.append(current_segment.copy())
                current_segment = {
                    "text": "",
                    "start_time": None,
                    "end_time": None,
                }

    # 最後のセグメントを追加
    if current_segment["text"]:
        segments.append(current_segment)

    # 総時間を計算
    duration = float(segments[-1]["end_time"]) if segments else 0.0

    return {
        "text": full_text,
        "segments": segments,
        "duration": duration,
    }


def transcribe_audio(audio_file_path: str, language_code: str = "ja-JP") -> Dict:
    """
    AWS Transcribeで音声を書き起こし.

    Args:
        audio_file_path: 音声ファイルのパス
        language_code: 言語コード（ja-JP, en-US等）

    Returns:
        dict: 書き起こし結果
            {
                "text": "全文書き起こしテキスト",
                "segments": [
                    {
                        "text": "セグメントのテキスト",
                        "start_time": 0.0,
                        "end_time": 5.2,
                        "confidence": 0.98
                    },
                    ...
                ],
                "duration": 512.5  # 総時間（秒）
            }
    """
    # クライアント初期化
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    transcribe_client = boto3.client("transcribe", region_name=AWS_REGION)

    # ジョブ名生成（ユニーク）
    job_name = f"presentation-feedback-{uuid.uuid4().hex[:8]}"

    # S3キー生成
    file_name = Path(audio_file_path).name
    s3_key = f"{S3_PREFIX}{job_name}/{file_name}"

    # 1. S3にアップロード
    s3_uri = _upload_to_s3(audio_file_path, s3_client, S3_BUCKET, s3_key)

    # 2. Transcriptionジョブ開始
    _start_transcription_job(transcribe_client, job_name, s3_uri, language_code)

    # 3. ジョブ完了を待機
    job_result = _wait_for_job_completion(transcribe_client, job_name)

    # 4. 結果を取得・パース
    result = _parse_transcription_result(job_result)

    print(f"✓ 書き起こし完了: {len(result['segments'])}セグメント, {result['duration']:.1f}秒")

    return result
