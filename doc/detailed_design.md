# Phase 1 詳細設計

## アーキテクチャ

```
prezentation_feedback_agent/
├── cli.py                     # CLIエントリーポイント
├── app_streamlit.py           # Streamlitアプリ
├── presentation_feedback/
│   ├── __init__.py
│   ├── core/                  # コア処理ロジック
│   │   ├── __init__.py
│   │   ├── transcriber.py     # AWS Transcribe連携
│   │   ├── audio_features.py  # 音声特徴量の抽出（話速、フィラーワード計算）
│   │   └── cost_tracker.py    # コスト追跡
│   └── agents/                # エージェント
│       ├── __init__.py
│       ├── speech_analyzer.py     # 音声特徴分析エージェント
│       ├── content_analyzer.py    # 内容分析エージェント
│       └── orchestrator.py        # 監督者エージェント
└── tests/
    └── ...
```

**設計方針**:
- `core/`: データ処理・計算ロジック（AWS API、数値計算など）
- `agents/`: Strandsエージェント（Bedrock LLMを使った定性分析）

**使用するLLM**:
- 音声特徴分析エージェント: **Amazon Nova Lite** (コスト効率重視)
- 内容分析エージェント: **Amazon Nova Lite** (コスト効率重視)
- 監督者エージェント: **Claude（最新の高性能モデル）** (高品質な統合判断)
  - 優先順位: Claude 4.5 Sonnet → Claude 4 Sonnet → Claude 3.7 Sonnet → Claude 3.5 Sonnet

## データ構造

MVPでは複雑なデータクラスは使わず、辞書やシンプルなクラスで受け渡しします。
必要に応じて各ファイル内で定義。

### 主要なデータ構造（例）

```python
# 書き起こし結果（transcriber.pyが返す）
{
    "text": "全文書き起こしテキスト",
    "segments": [
        {
            "text": "セグメントのテキスト",
            "start_time": 0.0,
            "end_time": 5.2,
            "confidence": 0.98
        },
        ...
    ],
    "duration": 512.5  # 総時間（秒）
}

# 音声特徴量（audio_features.pyが返す）
{
    "speaking_rate": 320.5,  # 文字/分
    "filler_words": {
        "えー": {"count": 15, "timestamps": [10.2, 25.3, ...]},
        "あのー": {"count": 8, "timestamps": [...]},
        ...
    },
    "pauses": {
        "total": 42,
        "avg_duration": 1.2,
        "long_pauses": [{"time": 120.5, "duration": 4.2}, ...]
    }
}

# 最終レポート（orchestrator.pyが返す）
{
    "summary": "総合サマリ",
    "strengths": [
        {"category": "話すスピード", "description": "...", "evidence": "320文字/分"},
        ...
    ],
    "improvements": [
        {"category": "フィラーワード", "issue": "...", "suggestion": "...", "priority": "high"},
        ...
    ],
    "cost_info": {
        "transcribe": {"duration_sec": 512.5, "cost_usd": 0.51},
        "nova_lite": {"input_tokens": 5000, "output_tokens": 1200, "cost_usd": 0.02},
        "claude_sonnet": {"input_tokens": 3000, "output_tokens": 800, "cost_usd": 0.12},
        "total_cost_usd": 0.65
    }
}
```

## コア処理ロジック実装

### 1. transcriber.py

**責務**: AWS Transcribeを使った音声書き起こし

**主要関数**:
```python
def transcribe_audio(audio_file_path: str, language_code: str = "ja-JP") -> dict:
    """
    AWS Transcribeで音声を書き起こし

    Args:
        audio_file_path: 音声ファイルのパス
        language_code: 言語コード（ja-JP, en-US等）

    Returns:
        dict: 書き起こし結果
            {
                "text": "全文",
                "segments": [{"text": "...", "start_time": 0.0, "end_time": 5.2, ...}],
                "duration": 512.5
            }
    """
    # 1. S3にアップロード or ローカルファイル使用
    # 2. Transcriptionジョブ開始
    # 3. ジョブ完了を待機
    # 4. 結果を取得・パース
    pass
```

### 2. audio_features.py

**責務**: 音声特徴量の計算（話速、フィラーワード、ポーズ）

**主要関数**:

```python
def calculate_speaking_rate(segments: list) -> float:
    """
    話速を計算（文字/分）

    ロジック:
    1. 全セグメントの文字数をカウント
    2. 総発話時間を計算（ポーズ除く）
    3. 文字/分 = 文字数 / (総発話時間 / 60)

    基準:
    - 日本語の標準的なプレゼン速度: 300-350文字/分
    - 英語の場合: 140-160 words/min

    Returns:
        float: 文字/分（日本語）またはwords/分（英語）
    """
    total_chars = sum(len(seg.text) for seg in segments)
    total_time = sum(seg.end_time - seg.start_time for seg in segments) / 60
    return total_chars / total_time if total_time > 0 else 0.0

def detect_filler_words(segments: List[Segment]) -> List[FillerWordSummary]:
    """
    フィラーワードを検出・集計

    対象ワード:
    - 日本語: 「えー」「あー」「あのー」「その」「ええと」「まあ」
    - 英語: "uh", "um", "like", "you know", "so"

    検出方法:
    - 正規表現マッチング
    - タイムスタンプ付きで記録
    - ワードごとに集計

    Returns:
        List[FillerWordSummary]: フィラーワードの集計結果
    """
    import re

    filler_patterns = {
        'えー': r'えー+',
        'あー': r'あー+',
        'あのー': r'あのー+',
        'その': r'その',
        'ええと': r'ええと',
        'まあ': r'まあ',
    }

    # 実装例（簡略版）
    results = {}
    for seg in segments:
        for word, pattern in filler_patterns.items():
            matches = re.findall(pattern, seg.text)
            if matches:
                if word not in results:
                    results[word] = {'count': 0, 'timestamps': []}
                results[word]['count'] += len(matches)
                results[word]['timestamps'].append(seg.start_time)

    return [
        FillerWordSummary(word=word, count=data['count'], timestamps=data['timestamps'])
        for word, data in results.items()
    ]

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

    Returns:
        PauseAnalysis: ポーズ分析結果
    """
    pauses = []
    long_pauses = []

    for i in range(len(segments) - 1):
        pause_duration = segments[i + 1].start_time - segments[i].end_time
        if pause_duration >= 0.5:
            pause = Pause(start_time=segments[i].end_time, duration=pause_duration)
            pauses.append(pause)
            if pause_duration >= 3.0:
                long_pauses.append(pause)

    avg_pause = sum(p.duration for p in pauses) / len(pauses) if pauses else 0.0

    return PauseAnalysis(
        total_pauses=len(pauses),
        avg_pause_duration=avg_pause,
        long_pauses=long_pauses
    )
```

**システムプロンプト**:
```
あなたは音声特徴分析の専門家です。
与えられた書き起こしデータと音声特徴量から、発表者の話し方について分析してください。

分析観点:
1. 話すスピード: 速すぎず遅すぎない適切なペースか（日本語: 300-350文字/分が目安）
2. フィラーワード: 不要な口癖が多くないか
3. 間（ポーズ）: 適切な間が取れているか

フィードバックは具体的かつ建設的に。数値的な根拠も示してください。
日本語で出力してください。
```

### 内容分析エージェント

**ファイル**: `presentation_feedback/agents/content_analyzer.py`

**入力**: `TranscriptionResult`
**出力**: `ContentAnalysis`

**実装の責務**:
1. Claude APIを使ってテキスト内容を分析
2. 構成・言葉遣い・時間配分を評価

**システムプロンプト**:
```
あなたはプレゼンテーション内容の分析専門家です。
書き起こしテキストから、発表の構成と言葉遣いを評価してください。

分析観点:
1. 構成: イントロ→本題→まとめの流れがあるか
   - イントロ: 最初の10%以内に導入・テーマ紹介があるか
   - まとめ: 最後の10%に結論・総括があるか
2. 論理性: 話の繋がりが自然か、トピック遷移がスムーズか
3. 言葉遣い: わかりやすい表現か、専門用語は適切か
4. 時間配分: イントロ・本題・まとめのバランスが取れているか

プレゼンテーションの「伝わりやすさ」を重視して評価してください。
日本語で出力してください。

【出力形式】
JSON形式で以下の構造で出力してください:
{
  "structure": {
    "has_intro": true/false,
    "has_conclusion": true/false,
    "topic_transitions": ["次に", "続いて", ...],
    "logical_flow_score": 0.0-1.0,
    "feedback": "..."
  },
  "language_quality": {
    "clarity_score": 0.0-1.0,
    "jargon_usage": ["専門用語1", ...],
    "repetitions": ["繰り返し表現1", ...],
    "feedback": "..."
  },
  "time_allocation": {
    "intro_duration": 秒,
    "main_duration": 秒,
    "conclusion_duration": 秒,
    "balance_feedback": "..."
  }
}
```

### 監督者エージェント

**ファイル**: `presentation_feedback/agents/orchestrator.py`

**入力**: `SpeechFeatures`, `ContentAnalysis`
**出力**: `FeedbackReport`

**実装の責務**:
1. 各分析結果を統合
2. よかった点・改善点を優先順位付けして抽出
3. 最終レポートを生成

**システムプロンプト**:
```
あなたはプレゼンテーション指導の専門家です。
音声特徴分析と内容分析の結果を統合し、発表者に役立つフィードバックレポートを作成してください。

【入力データ】
音声特徴:
- 話速: {speaking_rate} 文字/分
- フィラーワード: {filler_words}
- ポーズ分析: {pause_analysis}

内容分析:
- 構成: {structure}
- 言葉遣い: {language_quality}
- 時間配分: {time_allocation}

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
  "summary": "...",
  "strengths": [
    {"category": "...", "description": "...", "evidence": "..."},
    ...
  ],
  "improvements": [
    {"category": "...", "issue": "...", "suggestion": "...", "priority": "high/medium/low"},
    ...
  ],
  "detailed_feedback": {
    "speech_feedback": "...",
    "content_feedback": "...",
    "overall_impression": "..."
  }
}
```

## 実装スケジュール

### Week 1: 基盤実装
- [ ] プロジェクト構造の作成
- [ ] データモデル定義（`models/data_models.py`）
- [ ] AWS Transcribe連携実装（`transcription/transcriber.py`）
- [ ] 音声特徴量抽出の基本ロジック（`analysis/audio_features.py`）

### Week 2: エージェント実装
- [ ] 音声特徴分析エージェント（`agents/speech_analyzer.py`）
- [ ] 内容分析エージェント（`agents/content_analyzer.py`）
- [ ] 単体テスト作成

### Week 3: 統合・テスト
- [ ] 監督者エージェント（`agents/orchestrator.py`）
- [ ] CLIエントリーポイント（`cli.py`）
- [ ] エンドツーエンドのテスト
- [ ] サンプル音声でのデバッグ

### Week 4: UI・改善
- [ ] Streamlitアプリ実装（`app_streamlit.py`）
- [ ] フィードバックの質向上（プロンプト調整）
- [ ] エラーハンドリング強化
- [ ] README・使い方ドキュメント

## 技術的な考慮事項

### AWS Transcribe 連携

**非同期処理**:
```python
import boto3
import time

def transcribe_audio(audio_file_path: str, language_code: str = "ja-JP") -> TranscriptionResult:
    """
    AWS Transcribeで音声を書き起こし

    Args:
        audio_file_path: 音声ファイルのパス
        language_code: 言語コード（ja-JP, en-US等）

    Returns:
        TranscriptionResult: 書き起こし結果
    """
    transcribe = boto3.client('transcribe')

    # 1. S3にアップロード（または presigned URL 使用）
    # 2. Transcriptionジョブ開始
    # 3. ジョブ完了を待機
    # 4. 結果を取得・パース

    # 実装詳細は transcription/transcriber.py に記載
```

### エラーハンドリング

- AWS API エラー
- 音声ファイル形式の不正
- 書き起こし失敗
- エージェント実行エラー

### パフォーマンス最適化

- 並列処理: 音声特徴分析と内容分析を並列実行
- キャッシュ: 書き起こし結果のキャッシュ（同じファイルの再分析時）

## コスト追跡機能

### cost_tracker.py

**責務**: AWS Transcribe と Bedrock の利用コストを追跡・計算

**料金体系（2025年1月時点の参考値）**:
```python
PRICING = {
    "transcribe": {
        "per_second": 0.0004  # $0.024/分 = $0.0004/秒
    },
    "bedrock": {
        "nova_lite": {
            "input_per_1k": 0.00006,   # $0.06 per 1M tokens
            "output_per_1k": 0.00024   # $0.24 per 1M tokens
        },
        "claude_sonnet_3_5": {
            "input_per_1k": 0.003,     # $3.00 per 1M tokens
            "output_per_1k": 0.015     # $15.00 per 1M tokens
        }
    }
}
```

**主要クラス**:
```python
class CostTracker:
    """コスト追跡"""
    
    def __init__(self):
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
        """Transcribeのコストを追加"""
        cost = duration_seconds * PRICING["transcribe"]["per_second"]
        self.costs["transcribe"] += cost
        self.details["transcribe"].append({
            "duration_sec": duration_seconds,
            "cost_usd": cost
        })
    
    def add_bedrock_cost(self, model: str, input_tokens: int, output_tokens: int):
        """Bedrockのコストを追加"""
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
    
    def get_summary(self) -> dict:
        """コストサマリを取得"""
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
```

**使用例**:
```python
# メインの処理フロー
from presentation_feedback.core.cost_tracker import CostTracker

tracker = CostTracker()

# 1. 書き起こし
transcription = transcribe_audio(audio_path)
tracker.add_transcribe_cost(transcription["duration"])

# 2. エージェント実行（各エージェントからトークン数を返してもらう）
speech_result = speech_analyzer.analyze(transcription)
tracker.add_bedrock_cost("nova_lite", speech_result["input_tokens"], speech_result["output_tokens"])

content_result = content_analyzer.analyze(transcription)
tracker.add_bedrock_cost("nova_lite", content_result["input_tokens"], content_result["output_tokens"])

final_report = orchestrator.generate_report(speech_result, content_result)
tracker.add_bedrock_cost("claude_sonnet", final_report["input_tokens"], final_report["output_tokens"])

# 3. コスト情報を最終レポートに追加
final_report["cost_info"] = tracker.get_summary()
```

**CLI出力例**:
```
=== コスト情報 ===
AWS Transcribe: $0.51 (512.5秒)
Amazon Nova Lite: $0.02 (入力: 5,000トークン, 出力: 1,200トークン)
Claude 3.5 Sonnet: $0.12 (入力: 3,000トークン, 出力: 800トークン)
---
合計: $0.65
```

**Streamlit出力例**:
```python
st.subheader("💰 コスト情報")
cost = report["cost_info"]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Transcribe", f"${cost['transcribe']['cost_usd']}")
col2.metric("Nova Lite", f"${cost['nova_lite']['cost_usd']}")
col3.metric("Claude", f"${cost['claude_sonnet']['cost_usd']}")
col4.metric("合計", f"${cost['total_cost_usd']}", delta=None)
```


## モデル選択ロジック

### 監督者エージェントのモデル選択（クォータ対応フォールバック）

**設計思想**:
- 最高性能のモデルを優先的に使用
- クォータ制限や利用不可の場合、1段階性能の低いモデルに自動フォールバック
- 実行時にどのモデルが使用されたかをログ出力

**優先順位**（クロスリージョン推論プロファイル使用）:
1. Claude 4.5 Sonnet (`us.anthropic.claude-sonnet-4-5-*`) - 最高性能
2. Claude 4 Sonnet (`us.anthropic.claude-sonnet-4-*`)
3. Claude 3.7 Sonnet (`us.anthropic.claude-3-7-sonnet-*`)
4. Claude 3.5 Sonnet (`us.anthropic.claude-3-5-sonnet-*`) - フォールバック

**実装例**:
```python
import boto3
from botocore.exceptions import ClientError

def get_claude_model_with_fallback() -> str:
    """
    クォータエラー対応のClaudeモデル選択
    
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
    
    bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
    
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
                # クォータ超過 - 次のモデルにフォールバック
                print(f"⚠ {model_id}: クォータ制限のため次のモデルを試行")
                continue
                
            elif error_code == 'ResourceNotFoundException':
                # モデルが存在しない - 次のモデルにフォールバック
                print(f"⚠ {model_id}: モデルが利用不可のため次のモデルを試行")
                continue
                
            else:
                # その他のエラー
                print(f"⚠ {model_id}: エラー ({error_code}) - 次のモデルを試行")
                continue
    
    # すべて失敗した場合のフォールバック
    fallback_model = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    print(f"⚠ すべてのモデルが利用不可。フォールバック: {fallback_model}")
    return fallback_model


def create_orchestrator_agent():
    """監督者エージェントを作成"""
    from strands import Agent
    
    # 環境変数で明示的に指定されている場合はそれを使用
    model_id = os.getenv("ORCHESTRATOR_MODEL_ID")
    
    if model_id:
        print(f"環境変数で指定されたモデルを使用: {model_id}")
    else:
        # 自動選択（フォールバック機能付き）
        model_id = get_claude_model_with_fallback()
    
    return Agent(
        model=model_id,
        system_prompt="あなたはプレゼンテーション指導の専門家です..."
    )
```

**使用例**:
```python
# orchestrator.py
orchestrator = create_orchestrator_agent()
# 出力例: ✓ 使用モデル: us.anthropic.claude-sonnet-4-5-20250929-v1:0

# クォータ制限時の出力例:
# ⚠ us.anthropic.claude-sonnet-4-5-20250929-v1:0: クォータ制限のため次のモデルを試行
# ⚠ us.anthropic.claude-sonnet-4-20250514-v1:0: クォータ制限のため次のモデルを試行
# ✓ 使用モデル: us.anthropic.claude-3-7-sonnet-20250219-v1:0
```

**環境変数での固定指定**:
```bash
# .env
# 特定のモデルを使いたい場合（フォールバック無効）
ORCHESTRATOR_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Nova Liteのモデル指定**:
```python
# Nova Lite は固定（フォールバック不要）
NOVA_LITE_MODEL = "us.amazon.nova-lite-v1:0"

speech_analyzer = Agent(
    model=NOVA_LITE_MODEL,
    system_prompt="..."
)
```

**利点**:
- クォータ制限に自動対応
- 段階的にダウングレードして可用性を確保
- 使用モデルを明示的にログ出力
- 環境変数で固定モデルも指定可能
