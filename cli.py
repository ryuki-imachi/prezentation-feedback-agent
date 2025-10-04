#!/usr/bin/env python3
"""CLI エントリーポイント."""

import sys
import argparse
from pathlib import Path

from presentation_feedback.core import transcribe_audio, extract_audio_features, CostTracker
from presentation_feedback.agents import (
    create_speech_analyzer,
    create_content_analyzer,
    create_orchestrator_agent,
)


def main():
    """メイン処理."""
    parser = argparse.ArgumentParser(
        description="プレゼンテーション音声分析 - フィードバック生成"
    )
    parser.add_argument("audio_file", help="音声ファイルのパス")
    parser.add_argument(
        "--language", default="ja-JP", help="言語コード（デフォルト: ja-JP）"
    )
    args = parser.parse_args()

    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"エラー: ファイルが見つかりません: {audio_path}")
        sys.exit(1)

    print("=" * 60)
    print("プレゼンフィードバック分析")
    print("=" * 60)

    # コスト追跡開始
    tracker = CostTracker()

    try:
        # 1. 書き起こし
        print("\n[1/4] 音声を書き起こし中...")
        transcription = transcribe_audio(str(audio_path), args.language)
        tracker.add_transcribe_cost(transcription["duration"])
        print(f"✓ 完了 ({transcription['duration']:.1f}秒)")

        # 2. 音声特徴量抽出
        print("\n[2/4] 音声特徴量を抽出中...")
        audio_features = extract_audio_features(transcription)
        print(f"✓ 完了 (話速: {audio_features['speaking_rate']:.1f} 文字/分)")

        # 3. エージェント分析
        print("\n[3/4] AI分析中...")
        # TODO: エージェント実行
        # speech_result = analyze_speech_features(transcription, audio_features)
        # content_result = analyze_content(transcription)
        # final_report = generate_feedback_report(speech_result, content_result)
        print("⚠ エージェント分析は未実装")

        # 4. コスト情報表示
        print("\n[4/4] コスト情報")
        cost_info = tracker.get_summary()
        print(f"AWS Transcribe: ${cost_info['transcribe']['cost_usd']:.4f}")
        print(f"Amazon Nova Lite: ${cost_info['nova_lite']['cost_usd']:.4f}")
        print(f"Claude Sonnet: ${cost_info['claude_sonnet']['cost_usd']:.4f}")
        print("-" * 40)
        print(f"合計: ${cost_info['total_cost_usd']:.4f}")

        print("\n" + "=" * 60)
        print("分析完了！")
        print("=" * 60)

    except NotImplementedError as e:
        print(f"\n⚠ エラー: {e}")
        print("実装が完了していません。")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
