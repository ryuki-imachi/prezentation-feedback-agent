"""Streamlit Webアプリ エントリーポイント."""

import streamlit as st
import tempfile
from pathlib import Path

from presentation_feedback.core import transcribe_audio, extract_audio_features, CostTracker
from presentation_feedback.agents import (
    create_speech_analyzer,
    create_content_analyzer,
    create_orchestrator_agent,
)


st.set_page_config(
    page_title="プレゼンフィードバック",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 プレゼンフィードバック")
st.markdown("音声ファイルをアップロードして、プレゼンテーションのフィードバックを取得")

# ファイルアップロード
uploaded_file = st.file_uploader(
    "音声ファイルをアップロード",
    type=["mp3", "wav", "m4a", "ogg"],
    help="プレゼンテーション音声ファイルを選択してください"
)

if uploaded_file:
    # 音声プレイヤー
    st.audio(uploaded_file)

    # 分析開始ボタン
    if st.button("📊 分析開始", type="primary"):
        # 一時ファイルとして保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            audio_path = tmp_file.name

        # コスト追跡
        tracker = CostTracker()

        try:
            # プログレス表示
            progress_bar = st.progress(0)
            status_text = st.empty()

            # 1. 書き起こし
            status_text.text("🎙️ 音声を書き起こし中...")
            progress_bar.progress(10)
            transcription = transcribe_audio(audio_path)
            tracker.add_transcribe_cost(transcription["duration"])

            # 2. 音声特徴量抽出
            status_text.text("📈 音声特徴量を抽出中...")
            progress_bar.progress(25)
            audio_features = extract_audio_features(transcription)

            # 3. AI分析
            status_text.text("🤖 話し方を分析中...")
            progress_bar.progress(40)
            speech_analyzer = create_speech_analyzer()
            speech_result = speech_analyzer.analyze_speech(transcription, audio_features)
            speech_usage = speech_result.get("usage", {})
            tracker.add_bedrock_cost("nova_lite", speech_usage.get("input_tokens", 0), speech_usage.get("output_tokens", 0))

            status_text.text("🤖 内容を分析中...")
            progress_bar.progress(60)
            content_analyzer = create_content_analyzer()
            content_result = content_analyzer.analyze_content(transcription)
            content_usage = content_result.get("usage", {})
            tracker.add_bedrock_cost("nova_lite", content_usage.get("input_tokens", 0), content_usage.get("output_tokens", 0))

            status_text.text("🤖 総合フィードバックを生成中...")
            progress_bar.progress(80)
            orchestrator = create_orchestrator_agent()
            final_report = orchestrator.generate_feedback_report(speech_result, content_result)
            orchestrator_usage = final_report.get("usage", {})
            tracker.add_bedrock_cost("claude_sonnet", orchestrator_usage.get("input_tokens", 0), orchestrator_usage.get("output_tokens", 0))

            # 4. 完了
            progress_bar.progress(100)
            status_text.text("✅ 分析完了！")

            st.success("分析が完了しました！")

            # 結果表示
            st.markdown("---")

            # 総合サマリ
            st.subheader("📝 総合サマリ")
            st.write(final_report.get("summary", "（サマリなし）"))

            # よかった点
            st.subheader("✨ よかった点")
            for i, strength in enumerate(final_report.get("strengths", []), 1):
                with st.expander(f"{i}. {strength.get('category', '')}", expanded=True):
                    st.write(strength.get('description', ''))
                    if strength.get('evidence'):
                        st.caption(f"📊 根拠: {strength['evidence']}")

            # 改善点
            st.subheader("💡 改善点")
            for i, improvement in enumerate(final_report.get("improvements", []), 1):
                priority = improvement.get('priority', 'medium')
                priority_map = {
                    "high": ("🔴", "error"),
                    "medium": ("🟡", "warning"),
                    "low": ("🟢", "info")
                }
                priority_mark, priority_type = priority_map.get(priority, ("🟡", "warning"))

                with st.expander(f"{i}. {priority_mark} {improvement.get('category', '')}", expanded=True):
                    st.write(f"**課題:** {improvement.get('issue', '')}")
                    st.write(f"**提案:** {improvement.get('suggestion', '')}")

            # 詳細フィードバック
            with st.expander("📄 詳細フィードバック"):
                detailed = final_report.get("detailed_feedback", {})
                if detailed.get("speech_feedback"):
                    st.markdown("**話し方について:**")
                    st.write(detailed["speech_feedback"])
                if detailed.get("content_feedback"):
                    st.markdown("**内容について:**")
                    st.write(detailed["content_feedback"])
                if detailed.get("overall_impression"):
                    st.markdown("**総合所感:**")
                    st.write(detailed["overall_impression"])

            # コスト情報
            st.markdown("---")
            st.subheader("💰 コスト情報")
            cost_info = tracker.get_summary()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Transcribe", f"${cost_info['transcribe']['cost_usd']:.4f}",
                       help=f"{cost_info['transcribe']['duration_sec']:.1f}秒")
            col2.metric("Nova Lite", f"${cost_info['nova_lite']['cost_usd']:.4f}",
                       help=f"入力: {cost_info['nova_lite']['input_tokens']:,}トークン\n出力: {cost_info['nova_lite']['output_tokens']:,}トークン")
            col3.metric("Claude", f"${cost_info['claude_sonnet']['cost_usd']:.4f}",
                       help=f"入力: {cost_info['claude_sonnet']['input_tokens']:,}トークン\n出力: {cost_info['claude_sonnet']['output_tokens']:,}トークン")
            col4.metric("合計", f"${cost_info['total_cost_usd']:.4f}")

        except NotImplementedError as e:
            st.error(f"⚠ エラー: {e}")
            st.info("実装が完了していません。")
        except Exception as e:
            st.error(f"❌ エラー: {e}")
        finally:
            # 一時ファイル削除
            Path(audio_path).unlink(missing_ok=True)

else:
    st.info("👆 音声ファイルをアップロードしてください")

# サイドバー
with st.sidebar:
    st.header("ℹ️ 使い方")
    st.markdown("""
    1. プレゼン音声ファイルをアップロード
    2. 「分析開始」ボタンをクリック
    3. フィードバックを確認

    **対応形式**: MP3, WAV, M4A, OGG
    """)

    st.header("📝 分析内容")
    st.markdown("""
    - 話すスピード
    - フィラーワード
    - プレゼンの構成
    - 言葉遣い
    - よかった点・改善点
    """)
