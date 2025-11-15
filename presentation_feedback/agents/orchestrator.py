"""監督者エージェント"""

import os
from strands import Agent
from strands.models import BedrockModel
from typing import Dict

# オレゴンリージョン
AWS_REGION = "us-west-2"

# デフォルトモデル（環境変数で上書き可能）
DEFAULT_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


SYSTEM_PROMPT = """あなたはプレゼンテーション指導の専門家です。
音声特徴分析と内容分析の結果を統合し、発表者に役立つフィードバックレポートを作成してください。

【レポート構成】
1. 総合サマリ（2-3文）
2. よかった点 Top 3-5
   - 具体的に何が良かったか
   - 数値的根拠があれば記載
3. 改善点 Top 3-5
   - 何が課題か
   - どう改善すればよいか（具体的な提案）
4. 詳細フィードバック

トーン: 建設的でポジティブ。批判的にならず、成長をサポートする姿勢で。
日本語で出力してください。

【出力形式】
JSON形式で以下の構造で出力してください:
{
  "summary": "総合サマリ",
  "strengths": [
    {"category": "カテゴリ", "description": "説明", "evidence": "根拠"},
    ...
  ],
  "improvements": [
    {"category": "カテゴリ", "issue": "問題点", "suggestion": "改善提案", "priority": "high/medium/low"},
    ...
  ],
  "detailed_feedback": "詳細なフィードバック（段落形式）"
}
"""


class OrchestratorAgent:
    """監督者エージェント."""

    def __init__(self):
        """初期化."""
        # 環境変数で明示的に指定されている場合はそれを使用、なければデフォルト
        model_id = os.getenv("ORCHESTRATOR_MODEL_ID", DEFAULT_MODEL_ID)
        print(f"使用モデル: {model_id}")

        model = BedrockModel(model_id=model_id, region_name=AWS_REGION)
        self.agent = Agent(model=model, system_prompt=SYSTEM_PROMPT)

    def generate_feedback_report(self, speech_result: Dict, content_result: Dict) -> Dict:
        """
        最終フィードバックレポートを生成.

        Args:
            speech_result: 音声特徴分析結果
            content_result: 内容分析結果

        Returns:
            dict: 最終レポート
                {
                    "summary": str,
                    "strengths": [...],
                    "improvements": [...],
                    "detailed_feedback": str,
                    "usage": {
                        "input_tokens": int,
                        "output_tokens": int
                    }
                }
        """
        import json

        # 分析結果を整形
        speech_summary = {
            "feedback": speech_result.get("feedback", ""),
            "strengths": speech_result.get("strengths", []),
            "improvements": speech_result.get("improvements", [])
        }

        content_summary = {
            "structure": content_result.get("structure", {}),
            "language": content_result.get("language", {}),
            "strengths": content_result.get("strengths", []),
            "improvements": content_result.get("improvements", [])
        }

        # プロンプト構築
        prompt = f"""
以下の分析結果を統合して、最終フィードバックレポートを作成してください。

【音声特徴分析】
{json.dumps(speech_summary, ensure_ascii=False, indent=2)}

【内容分析】
{json.dumps(content_summary, ensure_ascii=False, indent=2)}

上記の分析結果をもとに、総合的なフィードバックレポートを生成してください。
よかった点と改善点をそれぞれ3-5個に絞り込み、優先順位をつけてください。
"""

        # エージェント実行
        result = self.agent(prompt)

        # 結果を取得
        import re
        output_text = result.message['content'][0]['text']

        # マークダウンのコードブロックを除去（```json ... ``` の場合）
        json_match = re.search(r'```json\s*\n(.*?)\n```', output_text, re.DOTALL)
        if json_match:
            output_text = json_match.group(1)

        # 結果をパース
        try:
            report = json.loads(output_text)
        except json.JSONDecodeError:
            # JSONパース失敗時のフォールバック
            report = {
                "summary": output_text[:200],
                "strengths": [],
                "improvements": [],
                "detailed_feedback": output_text
            }

        # トークン使用量を追加
        usage = result.metrics.accumulated_usage
        report["usage"] = {
            "input_tokens": usage.get('inputTokens', 0),
            "output_tokens": usage.get('outputTokens', 0)
        }

        return report


def create_orchestrator_agent() -> OrchestratorAgent:
    """
    監督者エージェントを作成.

    Returns:
        OrchestratorAgent: 監督者エージェント
    """
    return OrchestratorAgent()
