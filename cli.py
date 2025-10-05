#!/usr/bin/env python3
"""CLI エントリーポイント（デモモード専用）."""

import sys
import argparse
from pathlib import Path

# デモモード専用のインポート
from presentation_feedback.demo import (
    transcribe_audio_demo as transcribe_audio,
    extract_audio_features_demo as extract_audio_features,
    create_speech_analyzer_demo as create_speech_analyzer,
    create_content_analyzer_demo as create_content_analyzer,
    create_orchestrator_agent_demo as create_orchestrator_agent,
)
from presentation_feedback.core import CostTracker


def main():
    """メイン処理（デモモード専用）."""
    parser = argparse.ArgumentParser(
        description="プレゼンテーション音声分析 - フィードバック生成（デモモード）"
    )
    parser.add_argument("audio_file", help="音声ファイルのパス（ダミー）")
    parser.add_argument(
        "--language", default="ja-JP", help="言語コード（デフォルト: ja-JP）"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🎭 プレゼンフィードバック分析（デモモード）")
    print("=" * 60)
    print("※ このCLIはデモ用です。ダミーデータで動作イメージを確認できます。")
    print("※ 本格的な分析はStreamlitアプリをご利用ください: uv run streamlit run app_streamlit.py")
    print("=" * 60)

    # コスト追跡開始
    tracker = CostTracker()

    try:
        # 1. 書き起こし
        print("\n[1/4] 音声を書き起こし中...")
        transcription = transcribe_audio(args.audio_file, args.language)
        tracker.add_transcribe_cost(transcription["duration"])
        print(f"✓ 完了 ({transcription['duration']:.1f}秒)")

        # 2. 音声特徴量抽出
        print("\n[2/4] 音声特徴量を抽出中...")
        audio_features = extract_audio_features(transcription)
        print(f"✓ 完了 (話速: {audio_features['speaking_rate']:.1f} 文字/分)")

        # 3. エージェント分析
        print("\n[3/4] AI分析中...")

        # 音声特徴分析エージェント
        print("  - 話し方を分析中...")
        speech_analyzer = create_speech_analyzer()
        speech_result = speech_analyzer.analyze_speech(transcription, audio_features)
        tracker.add_bedrock_cost("nova_lite", speech_result.get("input_tokens", 0), speech_result.get("output_tokens", 0))

        # 内容分析エージェント
        print("  - 内容を分析中...")
        content_analyzer = create_content_analyzer()
        content_result = content_analyzer.analyze_content(transcription)
        tracker.add_bedrock_cost("nova_lite", content_result.get("input_tokens", 0), content_result.get("output_tokens", 0))

        # 監督者エージェント
        print("  - 総合フィードバックを生成中...")
        orchestrator = create_orchestrator_agent()
        final_report = orchestrator.generate_feedback_report(speech_result, content_result)
        tracker.add_bedrock_cost("claude_sonnet", final_report.get("input_tokens", 0), final_report.get("output_tokens", 0))

        print("✓ AI分析完了")

        # 4. 結果表示
        print("\n" + "=" * 60)
        print("📊 分析結果")
        print("=" * 60)

        print(f"\n【総合サマリ】")
        print(final_report.get("summary", "（サマリなし）"))

        print(f"\n【✨ よかった点】")
        for i, strength in enumerate(final_report.get("strengths", []), 1):
            print(f"{i}. {strength.get('category', '')}: {strength.get('description', '')}")
            if strength.get('evidence'):
                print(f"   根拠: {strength['evidence']}")

        print(f"\n【💡 改善点】")
        for i, improvement in enumerate(final_report.get("improvements", []), 1):
            priority = improvement.get('priority', 'medium')
            priority_mark = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            print(f"{i}. {priority_mark} {improvement.get('category', '')}")
            print(f"   課題: {improvement.get('issue', '')}")
            print(f"   提案: {improvement.get('suggestion', '')}")

        # 5. コスト情報表示
        print("\n" + "=" * 60)
        print("💰 コスト情報")
        print("=" * 60)
        cost_info = tracker.get_summary()
        print(f"AWS Transcribe: ${cost_info['transcribe']['cost_usd']:.4f} ({cost_info['transcribe']['duration_sec']:.1f}秒)")
        print(f"Amazon Nova Lite: ${cost_info['nova_lite']['cost_usd']:.4f} (入力: {cost_info['nova_lite']['input_tokens']:,}トークン, 出力: {cost_info['nova_lite']['output_tokens']:,}トークン)")
        print(f"Claude Sonnet: ${cost_info['claude_sonnet']['cost_usd']:.4f} (入力: {cost_info['claude_sonnet']['input_tokens']:,}トークン, 出力: {cost_info['claude_sonnet']['output_tokens']:,}トークン)")
        print("-" * 60)
        print(f"合計: ${cost_info['total_cost_usd']:.4f}")

        print("\n" + "=" * 60)
        print("✅ 分析完了！")
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
