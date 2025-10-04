"""音声特徴量の抽出."""

from typing import Dict, List


def calculate_speaking_rate(segments: List[Dict]) -> float:
    """
    話速を計算（文字/分）.

    Args:
        segments: 書き起こしセグメントのリスト

    Returns:
        float: 文字/分
    """
    total_chars = sum(len(seg["text"]) for seg in segments)
    total_time = sum(seg["end_time"] - seg["start_time"] for seg in segments) / 60
    return total_chars / total_time if total_time > 0 else 0.0


def calculate_pause_stats(segments: List[Dict]) -> Dict:
    """
    ポーズ（間）の統計情報を計算.

    Args:
        segments: 書き起こしセグメントのリスト

    Returns:
        dict: {
            "total": ポーズ総数,
            "avg_duration": 平均ポーズ時間,
            "long_pauses": [{"time": 時刻, "duration": 長さ}, ...]
        }
    """
    pauses = []
    long_pauses = []

    for i in range(len(segments) - 1):
        pause_duration = segments[i + 1]["start_time"] - segments[i]["end_time"]
        if pause_duration >= 0.5:  # 0.5秒以上をポーズと認定
            pauses.append(pause_duration)
            if pause_duration >= 3.0:  # 3秒以上を長すぎるポーズ
                long_pauses.append({
                    "time": segments[i]["end_time"],
                    "duration": pause_duration
                })

    avg = sum(pauses) / len(pauses) if pauses else 0.0
    return {
        "total": len(pauses),
        "avg_duration": avg,
        "long_pauses": long_pauses
    }


def extract_audio_features(transcription: Dict) -> Dict:
    """
    音声特徴量をまとめて抽出.

    Args:
        transcription: transcribe_audio()の返り値

    Returns:
        dict: {
            "speaking_rate": 話速（文字/分）,
            "pauses": ポーズ統計
        }
    """
    segments = transcription["segments"]
    return {
        "speaking_rate": calculate_speaking_rate(segments),
        "pauses": calculate_pause_stats(segments)
    }
