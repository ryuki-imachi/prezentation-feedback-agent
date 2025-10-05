# Prezentation Feedback Agent

プレゼンテーション音声を分析し、発表の仕方について多角的なフィードバックを提供するマルチエージェントシステム。

## 概要

AWS Transcribe と Amazon Bedrock (Claude) を活用して、プレゼンテーション音声を自動分析します。

### Phase 1: 音声ベース分析
- 音声ファイル（MP3, WAV, M4A等）を入力
- 話すスピード、フィラーワード、構成、言葉遣いを分析
- よかった点・改善点をフィードバック

## セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集してAWS認証情報を設定
```

### 2. 依存関係のインストール

```bash
uv sync
```

### 3. AWS認証

```bash
aws sso login --profile your-profile
```

## 使い方

### Streamlit Web版（推奨）

本格的な分析はStreamlit Webアプリをご利用ください。

```bash
uv run streamlit run app_streamlit.py
```

ブラウザで http://localhost:8501 にアクセスし、音声ファイルをアップロードして分析を開始します。

### CLI版（デモ専用）

CLIはデモ用です。ダミーデータで動作イメージを確認できます。

```bash
uv run cli.py samples/sample_presentation.mp3
```

**出力例:**
- ✨ よかった点: 構成、話速、専門用語の説明など
- 💡 改善点: フィラーワード、時間配分など（優先度付き）
- 💰 コスト情報: AWS Transcribe、Amazon Bedrock の利用料金

## アーキテクチャ

詳細は [DESIGN.md](DESIGN.md) を参照してください。

### マルチエージェント構成
1. **音声特徴分析エージェント**: 話速、フィラーワード、間の分析
2. **内容分析エージェント**: 構成、言葉遣い、論理性の分析
3. **監督者エージェント**: 統合レポート生成

## ライセンス

MIT
