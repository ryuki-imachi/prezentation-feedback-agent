# Prezentation Feedback Agent

プレゼンテーション音声を分析し、発表の仕方について多角的なフィードバックを提供するマルチエージェントシステム。

## 概要

AWS Transcribe と Amazon Bedrock (Claude) を活用して、プレゼンテーション音声を自動分析します。

- 音声ファイル（MP3, WAV, M4A等）を入力
- 話すスピード、フィラーワード、構成、言葉遣いを分析
- よかった点・改善点をフィードバック

## セットアップ

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. AWS認証

```bash
# SSOログイン
aws sso login --profile your-aws-profile

# 環境変数設定（重要）
export AWS_PROFILE=your-aws-profile
```

### 3. 環境変数の設定（オプション）

`.env.example` を参考に `.env` ファイルを作成してください。

```bash
cp .env.example .env
# .envファイルを編集して設定を調整
```

## 使い方

### Streamlit Web版（推奨）

本格的な分析はStreamlit Webアプリをご利用ください。

```bash
# AWS_PROFILEを設定してから実行（重要）
export AWS_PROFILE=your-aws-profile
uv run streamlit run app_streamlit.py
```

ブラウザで http://localhost:8501 にアクセスし、音声ファイルをアップロードして分析を開始します。

### CLI版（デモ専用）

CLIはデモ用です。ダミーデータで動作イメージを確認できます。

```bash
uv run cli.py samples/sample_presentation.mp3
```

## アーキテクチャ

詳細は [doc/basic_design.md](doc/basic_design.md) を参照してください。

### マルチエージェント構成
1. **音声特徴分析エージェント**: 話速、フィラーワード、間の分析
2. **内容分析エージェント**: 構成、言葉遣い、論理性の分析
3. **監督者エージェント**: 統合レポート生成
