"""音声特徴分析エージェント"""

import os
from strands import Agent
from strands.models import BedrockModel
from typing import Dict

from .utils import parse_agent_response


# オレゴンリージョン（us-west-2）
AWS_REGION = "us-west-2"

# モデルID設定
# CLAUDE_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
CLAUDE_MODEL_ID = "global.anthropic.claude-haiku-4-5-20251001-v1:0"

SYSTEM_PROMPT = """あなたは音声特徴分析の専門家です。
与えられた書き起こしデータと音声特徴量から、発表者の話し方について分析してください。

分析観点:
1. 話すスピード: 速すぎず遅すぎない適切なペースか（日本語: 300-350文字/分が目安）
2. フィラーワード: 不要な口癖（「えー」「あのー」など）が多くないか
3. 間（ポーズ）: 適切な間が取れているか

フィードバックは具体的かつ建設的に。数値的な根拠も示してください。
日本語で出力してください。

【出力形式】
JSON形式で以下の構造で出力してください:
{
  "feedback": "音声特徴に関するフィードバック（段落形式）",
  "strengths": ["強み1", "強み2", ...],
  "improvements": ["改善点1", "改善点2", ...]
}
"""


class SpeechAnalyzer:
    """音声特徴分析エージェント."""

    def __init__(self):
        """初期化."""
        # model = BedrockModel(model_id=NOVA_LITE_MODEL_ID, region_name=AWS_REGION)  # 元のモデル
        model = BedrockModel(model_id=CLAUDE_MODEL_ID, region_name=AWS_REGION)  # 一時的にClaude使用
        self.agent = Agent(model=model, system_prompt=SYSTEM_PROMPT)

    def analyze_speech(self, transcription: Dict, audio_features: Dict) -> Dict:
        """
        音声特徴を分析

        Args:
            transcription: 書き起こし結果
            audio_features: 音声特徴量（話速、ポーズ等）

        Returns:
            dict: 分析結果
                {
                    "feedback": "分析結果テキスト",
                    "strengths": [...],
                    "improvements": [...],
                    "usage": {
                        "input_tokens": int,
                        "output_tokens": int
                    }
                }
        """
        # フィラーワードの整形
        filler_words = audio_features.get('filler_words', {})
        filler_summary = "\n".join(
            [f"  - {word}: {data['count']}回" for word, data in filler_words.items()]
        ) if filler_words else "  なし"

        # プロンプト構築
        prompt = f"""
以下の音声特徴量を分析してください。

【音声特徴量】
- 話速: {audio_features.get('speaking_rate', 0):.1f} 文字/分
- フィラーワード:
{filler_summary}
- ポーズ統計:
  - 総ポーズ数: {audio_features.get('pauses', {}).get('total', 0)}
  - 平均ポーズ時間: {audio_features.get('pauses', {}).get('avg_duration', 0):.2f}秒
  - 長すぎるポーズ: {len(audio_features.get('pauses', {}).get('long_pauses', []))}回

【書き起こしテキスト（抜粋）】
{transcription['text'][:500]}...

上記の情報をもとに、音声特徴についてフィードバックしてください。
"""

        # エージェント実行
        result = self.agent(prompt)

        # 結果をパースして使用量を追加
        fallback = {
            "feedback": result.message['content'][0]['text'],
            "strengths": [],
            "improvements": []
        }
        analysis = parse_agent_response(result, fallback_value=fallback)

        return analysis


def create_speech_analyzer() -> SpeechAnalyzer:
    """
    音声特徴分析エージェントを作成.

    Returns:
        SpeechAnalyzer: 音声特徴分析エージェント
    """
    return SpeechAnalyzer()


