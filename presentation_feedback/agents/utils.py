"""エージェント共通ユーティリティ"""

import json
import re
from typing import Any, Dict, Optional


def extract_json_from_response(response_text: str) -> str:
    """
    レスポンステキストからJSONを抽出

    マークダウンのコードブロック（```json ... ```）がある場合は中身を取り出す

    Args:
        response_text: エージェントのレスポンステキスト

    Returns:
        str: 抽出されたJSON文字列
    """
    # マークダウンのコードブロックを除去（```json ... ``` の場合）
    json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return response_text


def extract_usage_metrics(result) -> Dict[str, int]:
    """
    エージェント実行結果からトークン使用量を抽出

    Args:
        result: エージェント実行結果（strands Agentの返り値）

    Returns:
        dict: {"input_tokens": int, "output_tokens": int}
    """
    usage = result.metrics.accumulated_usage
    return {
        "input_tokens": usage.get('inputTokens', 0),
        "output_tokens": usage.get('outputTokens', 0)
    }


def parse_agent_response(
    result,
    fallback_value: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    エージェント実行結果をパースしてJSON + 使用量を返す

    Args:
        result: エージェント実行結果（strands Agentの返り値）
        fallback_value: JSONパース失敗時のデフォルト値

    Returns:
        dict: パース済みレスポンス（usageフィールド付き）
    """
    # レスポンステキストを取得
    output_text = result.message['content'][0]['text']

    # JSONを抽出
    json_text = extract_json_from_response(output_text)

    # JSONをパース
    try:
        parsed_data = json.loads(json_text)
    except json.JSONDecodeError:
        # パース失敗時はフォールバックまたは生テキストを返す
        if fallback_value is not None:
            parsed_data = fallback_value
        else:
            parsed_data = {"raw_response": output_text}

    # トークン使用量を追加
    parsed_data["usage"] = extract_usage_metrics(result)

    return parsed_data
