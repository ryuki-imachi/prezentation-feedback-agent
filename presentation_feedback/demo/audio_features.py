"""音声特徴量抽出 デモ実装（ダミーデータ）."""

from .data import get_demo_audio_features


def extract_audio_features(transcription: dict) -> dict:
    """
    デモ用の音声特徴量抽出関数（ダミーデータを返す）.

    Args:
        transcription: 書き起こし結果（使用しない）

    Returns:
        dict: ダミーの音声特徴量
    """
    print("[DEMO] 音声特徴量をダミーデータで生成")
    return get_demo_audio_features()
