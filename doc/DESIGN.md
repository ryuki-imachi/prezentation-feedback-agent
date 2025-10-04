# プレゼンフィードバックエージェント 設計ドキュメント

## 概要
プレゼンテーション音声を分析し、発表の仕方について多角的なフィードバックを提供するマルチエージェントシステム。

## 要件

### インプット
- **Phase 1**: 音声ファイル（MP3, WAV, M4A等）
- **Phase 2**: 動画ファイル（MP4等）→ 音声抽出して処理
- **Phase 3**: スライド資料（PDF等）との統合分析

**設計方針**: 音声ファイルをベースに設計することで、動画対応時も音声抽出処理を追加するだけで拡張可能。

### アウトプット
発表の仕方に関する観点でのフィードバック:
- 話すスピード
- 話の流れ・構成
- 話の抑揚・トーン
- よかった点
- 改善点

※スコアリングも検討可能だが、定性的なフィードバック優先

## マルチエージェント構成案

### Phase 1: 音声ベースの3エージェント構成

#### 1. 監督者エージェント (Orchestrator)
**役割**: 全体の統括・最終レポート作成
- 各サブエージェントからのフィードバックを統合
- 優先度付けと総合評価
- 最終レポートの生成（よかった点・改善点）

#### 2. 音声特徴分析エージェント (Speech Analyzer)
**役割**: 音声の物理的特徴の分析
- **話すスピード**:
  - 発話速度（words per minute）の計測
  - 速すぎる/遅すぎる箇所の検出
- **間（ポーズ）の分析**:
  - 適切な間の取り方
  - 「えー」「あのー」などのフィラーワード検出・カウント
- **音量・明瞭さ**:
  - 声の大きさの一貫性
  - 聞き取りやすさ
- **抑揚（将来的）**:
  - 音声のピッチ変化
  - 単調さの検出

**使用技術**:
- AWS Transcribe（書き起こし + タイムスタンプ）
- pydub（音声処理）

#### 3. 内容分析エージェント (Content Analyzer)
**役割**: 話の内容・構成の分析
- **話の流れ・構成**:
  - イントロ → 本題 → まとめの構成
  - 論理的な繋がり
  - トピックの遷移の自然さ
- **言葉遣い**:
  - 専門用語の適切な使用
  - わかりやすい表現
  - 繰り返しや冗長性
- **時間配分**:
  - 各セクションの時間バランス
  - 全体の長さ

**使用技術**:
- Claude 3.5 Sonnet（書き起こしテキストの分析）

### Phase 2以降: 拡張エージェント（音声→動画対応時）

#### 4. 視覚分析エージェント (Visual Analyzer) ※Phase 2
**役割**: 映像からの視覚情報分析
- ジェスチャー・ボディランゲージ
- 表情・自信
- 画面構成

**使用技術**:
- ffmpeg（動画から音声抽出）
- Claude Vision（動画フレーム分析）

#### 5. スライド分析エージェント (Slide Analyzer) ※Phase 3
**役割**: スライドとの同期分析
- スライド切り替えタイミング
- スライドと発言の整合性

## システムフロー

### Phase 1: 音声ベース
```
[音声ファイル入力]
    ↓
[前処理]
    ├─ AWS Transcribe で書き起こし（タイムスタンプ付き）
    └─ 音声ファイルの基本情報取得（長さ等）
    ↓
[並列分析]
    ├─ 音声特徴分析エージェント
    │   └─ 話すスピード、フィラーワード、間の分析
    └─ 内容分析エージェント
        └─ 構成、言葉遣い、論理性の分析
    ↓
[監督者エージェント]
    └─ 統合レポート生成
    ↓
[出力]
    ├─ よかった点 Top 3-5
    ├─ 改善点 Top 3-5
    └─ 観点別詳細フィードバック
```

### Phase 2: 動画対応（拡張時）
```
[動画ファイル入力]
    ↓
[前処理]
    ├─ ffmpeg で音声抽出 ← Phase 1の処理に流す
    └─ フレーム抽出（キーフレーム）
    ↓
[Phase 1の処理] + [視覚分析エージェント]
```

**拡張性**: 音声処理部分は共通化されており、入力が動画になっても音声抽出のステップを追加するだけ。

## 技術スタック候補

### AWS Bedrock / Claude
- Claude 3.5 Sonnet: メインの分析・推論
- Claude Vision: 動画フレーム分析

### 音声処理
- AWS Transcribe: 音声書き起こし
- または OpenAI Whisper
- librosa: 音声特徴量抽出

### 動画処理
- ffmpeg: 動画/音声分離、フレーム抽出
- opencv-python: 動画処理

### その他
- Strands Agents: マルチエージェント基盤
- boto3: AWS SDK

## MVP（最小実装）の優先順位

### Phase 1: 音声ベースMVP（最優先）
1. ✅ AWS Transcribe による書き起こし（タイムスタンプ付き）
2. ✅ 音声特徴分析エージェント
   - 話すスピード計測
   - フィラーワード検出
3. ✅ 内容分析エージェント
   - 話の構成分析
   - 言葉遣い・わかりやすさ
4. ✅ 監督者エージェント（統合レポート生成）

**成果物**: 音声ファイルを入力すると、よかった点・改善点を含むフィードバックレポートが出力される

### Phase 2: 動画対応
5. 🔲 動画からの音声抽出（ffmpeg）
6. 🔲 視覚分析エージェント（Claude Vision）
   - 表情・ジェスチャー分析
7. 🔲 音声の抑揚分析（高度な音声特徴量）

### Phase 3: 高度な分析
8. 🔲 スライド入力対応
9. 🔲 スライドと発表の同期分析
10. 🔲 スコアリング機能
11. 🔲 過去の発表との比較・成長分析

## 検討事項

### 1. 音声/動画の入力方法
- **Phase 1**: ローカルファイルパス（音声ファイル）
- **Phase 2**: 動画ファイル → ffmpegで音声抽出
- **共通**: S3アップロード対応も検討（大容量ファイル対応）

### 2. 処理時間
- AWS Transcribeの処理時間（非同期処理）
- 長時間の音声の場合の考慮

### 3. コスト
- AWS Transcribe: 従量課金（秒単位）
- Claude API呼び出し: 書き起こしテキストの長さに依存
- 想定: 10分の発表で数十円程度

### 4. プライバシー
- 音声データの取り扱い
- 一時ファイルの削除
- S3バケットのライフサイクル設定

## 音声から動画への拡張性

### 設計上の利点
1. **処理の共通化**: 動画も最終的に音声抽出して同じパイプラインを通す
2. **段階的な開発**: まず音声で完成させ、動画は入力処理の追加のみ
3. **コスト削減**: 音声のみで十分な分析が可能（視覚は付加価値）

### 動画対応時の追加実装
```python
# 動画から音声抽出（追加するだけ）
def extract_audio_from_video(video_path: str) -> str:
    """動画から音声を抽出してaudio_pathを返す"""
    audio_path = video_path.replace('.mp4', '.mp3')
    # ffmpeg処理
    return audio_path

# 既存の音声処理パイプラインに流す
audio_path = extract_audio_from_video(video_path)
analyze_presentation(audio_path)  # 既存の関数
```

**結論**: 音声ベースで設計しても、動画対応は容易。むしろ音声で完成度を高めてから拡張する方が効率的。

## 次のステップ
1. ✅ Phase 1の設計完了
2. 必要なライブラリの依存関係追加（boto3, pydub等）
3. AWS Transcribe連携の実装
4. サンプル音声ファイルでの動作確認

---

## Phase 1 詳細設計

### アーキテクチャ

```
presentation_feedback/
├── main.py                    # エントリーポイント（CLI）
├── app.py                     # Streamlitアプリ（UI）
├── transcription/
│   ├── __init__.py
│   └── transcriber.py         # AWS Transcribe連携
├── analysis/
│   ├── __init__.py
│   └── audio_features.py      # 音声特徴量の抽出（話速、フィラーワード）
├── agents/
│   ├── __init__.py
│   ├── speech_analyzer.py     # 音声特徴分析エージェント
│   ├── content_analyzer.py    # 内容分析エージェント
│   └── orchestrator.py        # 監督者エージェント
└── utils/
    ├── __init__.py
    └── file_handler.py        # ファイル操作ユーティリティ
```

### データフロー詳細

#### 1. 前処理フェーズ
```python
# Input: audio_file_path (str) - 音声ファイルのパス
# Output: TranscriptionResult

class TranscriptionResult:
    text: str                    # 全文書き起こし
    segments: List[Segment]      # タイムスタンプ付きセグメント
    duration: float              # 総時間（秒）

class Segment:
    text: str                    # セグメントのテキスト
    start_time: float            # 開始時刻（秒）
    end_time: float              # 終了時刻（秒）
    confidence: float            # 認識信頼度
```

#### 2. 音声特徴分析フェーズ
```python
# Input: TranscriptionResult
# Output: SpeechFeatures

class SpeechFeatures:
    speaking_rate: float         # 話速（words per minute）
    filler_words: List[FillerWord]  # フィラーワード検出結果
    pause_analysis: PauseAnalysis   # 間の分析結果
    volume_consistency: float    # 音量の一貫性（将来的）

class FillerWord:
    word: str                    # 検出されたフィラーワード（「えー」「あのー」等）
    timestamp: float             # 発生時刻
    count: int                   # 全体での出現回数（サマリ用）

class PauseAnalysis:
    total_pauses: int            # ポーズの総数
    avg_pause_duration: float    # 平均ポーズ時間
    long_pauses: List[Pause]     # 長すぎるポーズ（3秒以上等）

class Pause:
    start_time: float
    duration: float
```

#### 3. 内容分析フェーズ
```python
# Input: TranscriptionResult
# Output: ContentAnalysis

class ContentAnalysis:
    structure: StructureAnalysis     # 構成分析
    language_quality: LanguageQuality # 言葉遣い
    time_allocation: TimeAllocation   # 時間配分

class StructureAnalysis:
    has_intro: bool              # イントロの有無
    has_conclusion: bool         # まとめの有無
    topic_transitions: List[str] # トピック遷移
    logical_flow_score: float    # 論理的な流れ（0-1）
    feedback: str                # 構成に関するフィードバック文

class LanguageQuality:
    clarity_score: float         # わかりやすさ（0-1）
    jargon_usage: List[str]      # 専門用語の使用
    repetitions: List[str]       # 繰り返しの多い表現
    feedback: str                # 言葉遣いのフィードバック文

class TimeAllocation:
    total_duration: float        # 総時間
    section_durations: Dict[str, float]  # セクション別時間
    balance_feedback: str        # 時間配分のフィードバック
```

#### 4. 統合レポート生成フェーズ
```python
# Input: SpeechFeatures, ContentAnalysis
# Output: FeedbackReport

class FeedbackReport:
    summary: str                 # 総合サマリ
    strengths: List[Strength]    # よかった点（Top 3-5）
    improvements: List[Improvement]  # 改善点（Top 3-5）
    detailed_feedback: DetailedFeedback

class Strength:
    category: str                # カテゴリ（「話すスピード」「構成」等）
    description: str             # 具体的な説明
    evidence: str                # 根拠（数値等）

class Improvement:
    category: str
    issue: str                   # 問題点
    suggestion: str              # 改善提案
    priority: str                # 優先度（high/medium/low）

class DetailedFeedback:
    speech_feedback: str         # 音声特徴の詳細フィードバック
    content_feedback: str        # 内容の詳細フィードバック
    overall_impression: str      # 全体的な印象
```

### エージェント実装詳細

#### 音声特徴分析エージェント

**入力**: `TranscriptionResult`
**出力**: `SpeechFeatures`

**分析ロジック**:
```python
def analyze_speaking_rate(segments: List[Segment]) -> float:
    """
    話速を計算（words per minute）

    ロジック:
    1. 全セグメントの単語数をカウント
    2. 総発話時間を計算（ポーズ除く）
    3. WPM = 単語数 / (総発話時間 / 60)

    基準:
    - 日本語の標準的なプレゼン速度: 300-350文字/分
    - 英語の場合: 140-160 words/min
    """
    pass

def detect_filler_words(segments: List[Segment]) -> List[FillerWord]:
    """
    フィラーワードを検出

    対象ワード:
    - 日本語: 「えー」「あー」「あのー」「その」「ええと」「まあ」
    - 英語: "uh", "um", "like", "you know", "so"

    検出方法:
    - 正規表現マッチング
    - タイムスタンプ付きで記録
    """
    pass

def analyze_pauses(segments: List[Segment]) -> PauseAnalysis:
    """
    ポーズ（間）を分析

    ロジック:
    1. セグメント間の時間差を計算
    2. 0.5秒以上をポーズと認定
    3. 3秒以上を「長すぎるポーズ」として警告

    評価基準:
    - 適切なポーズ: 1-2秒（文の区切り）
    - 長すぎるポーズ: 3秒以上（要改善）
    """
    pass
```

**システムプロンプト**:
```
あなたは音声特徴分析の専門家です。
与えられた書き起こしデータと音声特徴量から、発表者の話し方について分析してください。

分析観点:
1. 話すスピード: 速すぎず遅すぎない適切なペースか
2. フィラーワード: 不要な口癖が多くないか
3. 間（ポーズ）: 適切な間が取れているか

フィードバックは具体的かつ建設的に。数値的な根拠も示してください。
```

#### 内容分析エージェント

**入力**: `TranscriptionResult`
**出力**: `ContentAnalysis`

**分析ロジック**:
```python
def analyze_structure(text: str, segments: List[Segment]) -> StructureAnalysis:
    """
    プレゼンの構成を分析

    検出項目:
    1. イントロの有無
       - 「本日は」「今回は」「これから」などの導入表現
       - 最初の10%以内に自己紹介・テーマ紹介があるか

    2. まとめの有無
       - 「まとめますと」「以上」「ありがとうございました」
       - 最後の10%に結論・総括があるか

    3. トピック遷移
       - 「次に」「続いて」「では」などの接続表現
       - 話題の転換がスムーズか

    使用技術:
    - Claude APIによるテキスト分析
    - キーワード検出
    """
    pass

def analyze_language_quality(text: str) -> LanguageQuality:
    """
    言葉遣い・わかりやすさを分析

    評価項目:
    1. 専門用語の適切な使用
       - 専門用語の後に説明があるか

    2. 冗長性・繰り返し
       - 同じ表現の過度な繰り返し検出

    3. 文の長さ
       - 一文が長すぎないか（目安: 60文字以内）

    使用技術:
    - Claude APIによる自然言語分析
    """
    pass
```

**システムプロンプト**:
```
あなたはプレゼンテーション内容の分析専門家です。
書き起こしテキストから、発表の構成と言葉遣いを評価してください。

分析観点:
1. 構成: イントロ→本題→まとめの流れがあるか
2. 論理性: 話の繋がりが自然か
3. 言葉遣い: わかりやすい表現か、専門用語は適切か
4. 時間配分: バランスが取れているか

プレゼンテーションの「伝わりやすさ」を重視して評価してください。
```

#### 監督者エージェント

**入力**: `SpeechFeatures`, `ContentAnalysis`
**出力**: `FeedbackReport`

**統合ロジック**:
```python
def generate_feedback_report(
    speech_features: SpeechFeatures,
    content_analysis: ContentAnalysis
) -> FeedbackReport:
    """
    各分析結果を統合してレポート生成

    処理フロー:
    1. よかった点を抽出（優先順位付け）
    2. 改善点を抽出（重要度順）
    3. 全体サマリを生成
    4. 詳細フィードバックを構造化

    優先順位の判断基準:
    - インパクトの大きさ（聴衆への影響）
    - 改善の容易さ
    - 頻度・重要度
    """
    pass
```

**システムプロンプト**:
```
あなたはプレゼンテーション指導の専門家です。
音声特徴分析と内容分析の結果を統合し、発表者に役立つフィードバックレポートを作成してください。

レポート構成:
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
```

### UI/フロントエンド

#### Phase 1: CLI (コマンドライン)
**最もシンプル・開発コスト低**

```bash
# 使い方
$ python main.py analyze /path/to/audio.mp3

# 出力例
=== プレゼンフィードバックレポート ===
総時間: 8分32秒

【よかった点】
1. 話すスピードが適切 (320文字/分)
2. 構成がしっかりしている（イントロ→本題→まとめ）
3. 専門用語に説明が付いていてわかりやすい

【改善点】
1. フィラーワード「えー」が多い（24回）
   → 意識的に減らすか、ポーズに置き換える
2. 後半のペースが速い
   → 重要な部分はゆっくり話す

詳細レポートを report_20250105_143022.txt に保存しました。
```

**メリット**:
- 実装が簡単
- すぐに動作確認できる
- 自動化しやすい（CI/CD組み込み等）

#### Phase 1.5: Streamlit (Webアプリ)
**ほどほどの実装コスト、UI体験良好**

参考: [agent-book/chapter6/frontend/app.py](https://github.com/minorun365/agent-book/tree/main/chapter6)

```python
import streamlit as st

st.title("プレゼンフィードバック")

uploaded_file = st.file_uploader("音声ファイルをアップロード", type=["mp3", "wav", "m4a"])

if uploaded_file and st.button("分析開始"):
    with st.spinner("分析中..."):
        # 分析処理
        report = analyze_presentation(uploaded_file)

    # 結果表示
    st.success("分析完了！")
    st.subheader("📊 よかった点")
    for strength in report.strengths:
        st.write(f"✅ {strength.description}")

    st.subheader("💡 改善点")
    for improvement in report.improvements:
        st.write(f"⚠️ {improvement.issue}")
        st.write(f"   → {improvement.suggestion}")
```

**メリット**:
- ブラウザで使える
- ファイルアップロードが簡単
- 視覚的に見やすい
- 実装コスト低（Pythonのみ）

**デメリット**:
- デザインのカスタマイズ性は低い

#### Phase 2: React/Next.js (本格的なWebアプリ)
**実装コスト高、プロダクションレベル**

**構成**:
```
frontend/               # React/Next.js
  ├── app/
  │   ├── page.tsx     # トップページ（ファイルアップロード）
  │   └── result/[id]/page.tsx  # 結果表示ページ
  └── components/
      ├── FileUploader.tsx
      ├── FeedbackReport.tsx
      └── LoadingSpinner.tsx

backend/                # FastAPI
  ├── main.py          # APIサーバー
  └── routes/
      ├── upload.py    # ファイルアップロードエンドポイント
      └── analyze.py   # 分析実行エンドポイント
```

**メリット**:
- デザインの自由度が高い
- リアルタイム処理表示（WebSocket等）
- 本格的なプロダクト化可能

**デメリット**:
- フロント・バックエンド分離で開発コスト大
- インフラ構築が必要

### 推奨アプローチ

#### ステップ1: CLI（即座に実装）
まずCLIで動作確認。コア機能の完成度を高める。

#### ステップ2: Streamlit（UI追加）
ユーザーフィードバックを得るためにStreamlitでWebアプリ化。

#### ステップ3: React（本格化）
必要に応じて本格的なWebアプリに移行。

**Phase 1のMVPはCLI + Streamlitの組み合わせを推奨**:
- CLIで自動テスト・デバッグ
- StreamlitでUI体験確認

### 技術スタック（Phase 1）

#### 必須ライブラリ
```toml
[project.dependencies]
strands-agents = ">=1.6.0"        # マルチエージェント基盤
strands-agents-tools = ">=0.2.5"  # ツール群
boto3 = ">=1.34.0"                # AWS SDK
python-dotenv = ">=1.0.0"         # 環境変数管理
pydub = ">=0.25.1"                # 音声ファイル操作
streamlit = ">=1.46.1"            # UI（オプション）
```

#### AWS サービス
- **AWS Transcribe**: 音声書き起こし（日本語対応）
- **Amazon Bedrock (Claude 3.5 Sonnet)**: テキスト分析

### 実装スケジュール

#### Week 1: 基盤実装
- [ ] プロジェクト構造の作成
- [ ] AWS Transcribe連携実装
- [ ] 音声特徴量抽出の基本ロジック

#### Week 2: エージェント実装
- [ ] 音声特徴分析エージェント
- [ ] 内容分析エージェント
- [ ] データクラスの実装

#### Week 3: 統合・テスト
- [ ] 監督者エージェント
- [ ] エンドツーエンドのテスト（CLI）
- [ ] サンプル音声でのデバッグ

#### Week 4: UI・改善
- [ ] Streamlitアプリ実装
- [ ] フィードバックの質向上
- [ ] エラーハンドリング
- [ ] README・使い方ドキュメント

### 次のアクション
1. ✅ Phase 1の詳細設計完了（UI含む）
2. プロジェクト構造の作成（CLI + Streamlit対応）
3. 依存関係の追加
4. AWS Transcribe連携の実装から着手
