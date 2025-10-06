"""内容分析エージェント - Amazon Nova Lite使用."""

import os
from strands import Agent
from strands.models import BedrockModel
from typing import Dict


# オレゴンリージョン（us-west-2）のNova Lite
AWS_REGION = "us-west-2"
NOVA_LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"

SYSTEM_PROMPT = """あなたはプレゼンテーション内容の分析専門家です。
書き起こしテキストから、発表の構成と言葉遣いを評価してください。

分析観点:
1. 構成: イントロ→本題→まとめの流れがあるか
   - イントロ: 最初の10%以内に導入・テーマ紹介があるか
   - まとめ: 最後の10%に結論・総括があるか
2. 論理性: 話の繋がりが自然か、トピック遷移がスムーズか
3. 言葉遣い: わかりやすい表現か、専門用語は適切か
4. 時間配分: イントロ・本題・まとめのバランスが取れているか

プレゼンテーションの「伝わりやすさ」を重視して評価してください。
日本語で出力してください。

【出力形式】
JSON形式で以下の構造で出力してください:
{
  "structure": {
    "has_intro": true/false,
    "has_conclusion": true/false,
    "feedback": "構成に関するフィードバック"
  },
  "language": {
    "clarity": "high/medium/low",
    "feedback": "言葉遣いに関するフィードバック"
  },
  "strengths": ["強み1", "強み2", ...],
  "improvements": ["改善点1", "改善点2", ...]
}
"""


class ContentAnalyzer:
    """内容分析エージェント."""

    def __init__(self):
        """初期化."""
        model = BedrockModel(model_id=NOVA_LITE_MODEL_ID, region_name=AWS_REGION)
        self.agent = Agent(model=model, system_prompt=SYSTEM_PROMPT)

    def analyze_content(self, transcription: Dict) -> Dict:
        """
        プレゼン内容を分析.

        Args:
            transcription: 書き起こし結果

        Returns:
            dict: 分析結果
                {
                    "structure": {...},
                    "language": {...},
                    "strengths": [...],
                    "improvements": [...],
                    "usage": {
                        "input_tokens": int,
                        "output_tokens": int
                    }
                }
        """
        # プロンプト構築
        prompt = f"""
以下のプレゼンテーション書き起こしを分析してください。

【総時間】
{transcription['duration']:.1f}秒 ({transcription['duration'] / 60:.1f}分)

【書き起こしテキスト】
{transcription['text']}

上記のプレゼンテーション内容について、構成・言葉遣い・論理性を評価してください。
"""

        # エージェント実行
        print("📝 内容を分析中...")
        result = self.agent(prompt)

        # 結果をパース
        import json
        try:
            analysis = json.loads(result.output)
        except json.JSONDecodeError:
            # JSONパース失敗時のフォールバック
            analysis = {
                "structure": {
                    "has_intro": True,
                    "has_conclusion": True,
                    "feedback": result.output[:200]
                },
                "language": {
                    "clarity": "medium",
                    "feedback": ""
                },
                "strengths": [],
                "improvements": []
            }

        # トークン使用量を追加
        analysis["usage"] = {
            "input_tokens": result.usage.input_tokens,
            "output_tokens": result.usage.output_tokens
        }

        print(f"✓ 内容分析完了 (入力: {result.usage.input_tokens}, 出力: {result.usage.output_tokens} トークン)")

        return analysis


def create_content_analyzer() -> ContentAnalyzer:
    """
    内容分析エージェントを作成.

    Returns:
        ContentAnalyzer: 内容分析エージェント
    """
    return ContentAnalyzer()
