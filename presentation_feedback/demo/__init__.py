"""デモ用モジュール（ダミーデータ・ダミー実装）."""

from .data import (
    get_demo_transcription,
    get_demo_audio_features,
    get_demo_speech_analysis,
    get_demo_content_analysis,
    get_demo_final_report,
)
from .transcriber import transcribe_audio as transcribe_audio_demo
from .audio_features import extract_audio_features as extract_audio_features_demo
from .agents import (
    create_speech_analyzer as create_speech_analyzer_demo,
    create_content_analyzer as create_content_analyzer_demo,
    create_orchestrator_agent as create_orchestrator_agent_demo,
)

__all__ = [
    "get_demo_transcription",
    "get_demo_audio_features",
    "get_demo_speech_analysis",
    "get_demo_content_analysis",
    "get_demo_final_report",
    "transcribe_audio_demo",
    "extract_audio_features_demo",
    "create_speech_analyzer_demo",
    "create_content_analyzer_demo",
    "create_orchestrator_agent_demo",
]
