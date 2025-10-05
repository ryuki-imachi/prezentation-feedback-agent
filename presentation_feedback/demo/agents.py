"""エージェント デモ実装（ダミーデータ）."""

from typing import Dict
from .data import (
    get_demo_speech_analysis,
    get_demo_content_analysis,
    get_demo_final_report,
)


class SpeechAnalyzerDemo:
    """話し方分析エージェント（デモ）."""

    def analyze_speech(self, transcription: Dict, audio_features: Dict) -> Dict:
        """
        音声特徴を分析（ダミーデータを返す）.

        Args:
            transcription: 書き起こし結果（使用しない）
            audio_features: 音声特徴量（使用しない）

        Returns:
            dict: ダミーの分析結果
        """
        print("[DEMO] 話し方を分析中（ダミーデータ）...")
        return get_demo_speech_analysis()


class ContentAnalyzerDemo:
    """内容分析エージェント（デモ）."""

    def analyze_content(self, transcription: Dict) -> Dict:
        """
        プレゼン内容を分析（ダミーデータを返す）.

        Args:
            transcription: 書き起こし結果（使用しない）

        Returns:
            dict: ダミーの分析結果
        """
        print("[DEMO] 内容を分析中（ダミーデータ）...")
        return get_demo_content_analysis()


class OrchestratorAgentDemo:
    """監督者エージェント（デモ）."""

    def generate_feedback_report(self, speech_result: Dict, content_result: Dict) -> Dict:
        """
        最終フィードバックレポートを生成（ダミーデータを返す）.

        Args:
            speech_result: 話し方分析結果（使用しない）
            content_result: 内容分析結果（使用しない）

        Returns:
            dict: ダミーの最終レポート
        """
        print("[DEMO] 総合フィードバックを生成中（ダミーデータ）...")
        return get_demo_final_report()


def create_speech_analyzer() -> SpeechAnalyzerDemo:
    """話し方分析エージェント（デモ）を作成."""
    return SpeechAnalyzerDemo()


def create_content_analyzer() -> ContentAnalyzerDemo:
    """内容分析エージェント（デモ）を作成."""
    return ContentAnalyzerDemo()


def create_orchestrator_agent() -> OrchestratorAgentDemo:
    """監督者エージェント（デモ）を作成."""
    return OrchestratorAgentDemo()
