"""コスト追跡モジュール."""

from typing import Dict


# 料金体系（2025年1月時点の参考値 - 実装時に最新値に更新）
PRICING = {
    "transcribe": {
        "per_second": 0.0004  # $0.024/分 = $0.0004/秒
    },
    "bedrock": {
        "nova_lite": {
            "input_per_1k": 0.00006,   # $0.06 per 1M tokens
            "output_per_1k": 0.00024   # $0.24 per 1M tokens
        },
        "claude_sonnet": {
            "input_per_1k": 0.003,     # $3.00 per 1M tokens (3.5 Sonnet参考)
            "output_per_1k": 0.015     # $15.00 per 1M tokens
        }
    }
}


class CostTracker:
    """AWS Transcribe と Bedrock のコスト追跡."""

    def __init__(self):
        """初期化."""
        self.costs = {
            "transcribe": 0.0,
            "nova_lite": 0.0,
            "claude_sonnet": 0.0
        }
        self.details = {
            "transcribe": [],
            "nova_lite": [],
            "claude_sonnet": []
        }

    def add_transcribe_cost(self, duration_seconds: float):
        """
        Transcribeのコストを追加.

        Args:
            duration_seconds: 処理時間（秒）
        """
        cost = duration_seconds * PRICING["transcribe"]["per_second"]
        self.costs["transcribe"] += cost
        self.details["transcribe"].append({
            "duration_sec": duration_seconds,
            "cost_usd": cost
        })

    def add_bedrock_cost(self, model: str, input_tokens: int, output_tokens: int):
        """
        Bedrockのコストを追加.

        Args:
            model: モデル名（"nova_lite" or "claude_sonnet"）
            input_tokens: 入力トークン数
            output_tokens: 出力トークン数
        """
        pricing = PRICING["bedrock"][model]
        input_cost = (input_tokens / 1000) * pricing["input_per_1k"]
        output_cost = (output_tokens / 1000) * pricing["output_per_1k"]
        total_cost = input_cost + output_cost

        self.costs[model] += total_cost
        self.details[model].append({
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": total_cost
        })

    def get_summary(self) -> Dict:
        """
        コストサマリを取得.

        Returns:
            dict: コスト情報
        """
        return {
            "transcribe": {
                "duration_sec": sum(d["duration_sec"] for d in self.details["transcribe"]),
                "cost_usd": round(self.costs["transcribe"], 4)
            },
            "nova_lite": {
                "input_tokens": sum(d["input_tokens"] for d in self.details["nova_lite"]),
                "output_tokens": sum(d["output_tokens"] for d in self.details["nova_lite"]),
                "cost_usd": round(self.costs["nova_lite"], 4)
            },
            "claude_sonnet": {
                "input_tokens": sum(d["input_tokens"] for d in self.details["claude_sonnet"]),
                "output_tokens": sum(d["output_tokens"] for d in self.details["claude_sonnet"]),
                "cost_usd": round(self.costs["claude_sonnet"], 4)
            },
            "total_cost_usd": round(sum(self.costs.values()), 4)
        }
