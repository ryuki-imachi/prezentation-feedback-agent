"""AWS Transcribe デモ実装（ダミーデータ）."""

from .data import get_demo_transcription


def transcribe_audio(audio_file_path: str, language_code: str = "ja-JP") -> dict:
    """
    デモ用の書き起こし関数（ダミーデータを返す）.

    Args:
        audio_file_path: 音声ファイルのパス（使用しない）
        language_code: 言語コード（使用しない）

    Returns:
        dict: ダミーの書き起こし結果
    """
    print(f"[DEMO] 音声ファイル '{audio_file_path}' をダミーデータで処理")
    return get_demo_transcription()
