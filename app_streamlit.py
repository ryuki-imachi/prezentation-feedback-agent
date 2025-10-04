"""Streamlit Webアプリ エントリーポイント."""

import streamlit as st
import tempfile
from pathlib import Path

from presentation_feedback.core import transcribe_audio, extract_audio_features, CostTracker


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
            progress_bar.progress(25)
            # transcription = transcribe_audio(audio_path)
            # tracker.add_transcribe_cost(transcription["duration"])

            # 2. 音声特徴量抽出
            status_text.text("📈 音声特徴量を抽出中...")
            progress_bar.progress(50)
            # audio_features = extract_audio_features(transcription)

            # 3. AI分析
            status_text.text("🤖 AI分析中...")
            progress_bar.progress(75)
            # TODO: エージェント実行

            # 4. 完了
            progress_bar.progress(100)
            status_text.text("✅ 分析完了！")

            st.success("分析が完了しました！")

            # 結果表示（仮）
            st.subheader("📊 よかった点")
            st.info("⚠ エージェント分析は未実装です")

            st.subheader("💡 改善点")
            st.info("⚠ エージェント分析は未実装です")

            # コスト情報
            st.subheader("💰 コスト情報")
            cost_info = tracker.get_summary()
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Transcribe", f"${cost_info['transcribe']['cost_usd']:.4f}")
            col2.metric("Nova Lite", f"${cost_info['nova_lite']['cost_usd']:.4f}")
            col3.metric("Claude", f"${cost_info['claude_sonnet']['cost_usd']:.4f}")
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
