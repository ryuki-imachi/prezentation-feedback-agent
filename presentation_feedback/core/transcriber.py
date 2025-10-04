"""AWS Transcribe連携モジュール."""

import boto3
import time
from typing import Dict


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
    # TODO: 実装
    # 1. S3にアップロード or ローカルファイル使用
    # 2. Transcriptionジョブ開始
    # 3. ジョブ完了を待機
    # 4. 結果を取得・パース

    raise NotImplementedError("transcribe_audio is not implemented yet")
