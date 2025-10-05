"""監督者エージェント - Claude Sonnet使用（クォータ対応フォールバック）."""

import os
import boto3
from botocore.exceptions import ClientError
from strands import Agent
from strands.models import BedrockModel
from typing import Dict

# オレゴンリージョン
AWS_REGION = "us-west-2"


def get_claude_model_with_fallback() -> str:
    """
    クォータエラー対応のClaudeモデル選択.

    優先順位順に試行し、利用可能な最高性能モデルを返す

    Returns:
        str: 利用可能なモデルID
    """
    # 優先順位順のモデルリスト
    model_candidates = [
        "us.anthropic.claude-sonnet-4-5-20250929-v1:0",  # Claude 4.5 Sonnet
        "us.anthropic.claude-sonnet-4-20250514-v1:0",     # Claude 4 Sonnet
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0",   # Claude 3.7 Sonnet
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0",   # Claude 3.5 Sonnet
    ]

    bedrock = boto3.client('bedrock-runtime', region_name=AWS_REGION)

    for model_id in model_candidates:
        try:
            # 簡単なテストリクエストで利用可能性を確認
            response = bedrock.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": [{"text": "test"}]}],
                inferenceConfig={"maxTokens": 10}
            )
            print(f"✓ 使用モデル: {model_id}")
            return model_id

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == 'ThrottlingException':
                print(f"⚠ {model_id}: クォータ制限のため次のモデルを試行")
                continue

            elif error_code == 'ResourceNotFoundException':
                print(f"⚠ {model_id}: モデルが利用不可のため次のモデルを試行")
                continue

            else:
                print(f"⚠ {model_id}: エラー ({error_code}) - 次のモデルを試行")
                continue

    # すべて失敗した場合のフォールバック
    fallback_model = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    print(f"⚠ すべてのモデルが利用不可。フォールバック: {fallback_model}")
    return fallback_model


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
        # 環境変数で明示的に指定されている場合はそれを使用
        model_id = os.getenv("ORCHESTRATOR_MODEL_ID")

        if model_id:
            print(f"環境変数で指定されたモデルを使用: {model_id}")
        else:
            # 自動選択（フォールバック機能付き）
            model_id = get_claude_model_with_fallback()

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
        """
        # プロンプト構築
        prompt = f"""
以下の分析結果を統合して、最終フィードバックレポートを作成してください。

【音声特徴分析】
{speech_result}

【内容分析】
{content_result}

上記の分析結果をもとに、総合的なフィードバックレポートを生成してください。
"""

        # TODO: エージェント実行とトークン数取得
        # result = self.agent(prompt)
        # return result

        raise NotImplementedError("generate_feedback_report is not implemented yet")


def create_orchestrator_agent() -> OrchestratorAgent:
    """
    監督者エージェントを作成.

    Returns:
        OrchestratorAgent: 監督者エージェント
    """
    return OrchestratorAgent()
