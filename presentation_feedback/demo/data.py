"""デモ用のダミーデータ生成."""


def get_demo_transcription() -> dict:
    """デモ用の書き起こしデータを返す."""
    return {
        "text": (
            "皆さん、こんにちは。本日はAIを活用したプレゼンテーション分析システムについてご紹介します。"
            "えー、まず最初に、このシステムの概要についてお話しします。"
            "このシステムは、音声ファイルをアップロードするだけで、話し方や内容について詳細なフィードバックを提供します。"
            "あのー、具体的には、話すスピード、フィラーワード、プレゼンの構成などを分析します。"
            "次に、技術スタックについてご説明します。"
            "AWS TranscribeとAmazon Bedrockを活用しており、マルチエージェントシステムで多角的な分析を実現しています。"
            "えー、最後に、実際の活用例についてお話しします。"
            "このシステムを使うことで、プレゼンテーションスキルの向上に役立てることができます。"
            "以上で説明を終わります。ご清聴ありがとうございました。"
        ),
        "segments": [
            {
                "text": "皆さん、こんにちは。本日はAIを活用したプレゼンテーション分析システムについてご紹介します。",
                "start_time": 0.0,
                "end_time": 6.5,
                "confidence": 0.98
            },
            {
                "text": "えー、まず最初に、このシステムの概要についてお話しします。",
                "start_time": 7.0,
                "end_time": 11.2,
                "confidence": 0.95
            },
            {
                "text": "このシステムは、音声ファイルをアップロードするだけで、話し方や内容について詳細なフィードバックを提供します。",
                "start_time": 11.5,
                "end_time": 18.3,
                "confidence": 0.97
            },
            {
                "text": "あのー、具体的には、話すスピード、フィラーワード、プレゼンの構成などを分析します。",
                "start_time": 19.0,
                "end_time": 24.8,
                "confidence": 0.96
            },
            {
                "text": "次に、技術スタックについてご説明します。",
                "start_time": 25.2,
                "end_time": 28.5,
                "confidence": 0.98
            },
            {
                "text": "AWS TranscribeとAmazon Bedrockを活用しており、マルチエージェントシステムで多角的な分析を実現しています。",
                "start_time": 29.0,
                "end_time": 36.2,
                "confidence": 0.97
            },
            {
                "text": "えー、最後に、実際の活用例についてお話しします。",
                "start_time": 37.0,
                "end_time": 41.0,
                "confidence": 0.96
            },
            {
                "text": "このシステムを使うことで、プレゼンテーションスキルの向上に役立てることができます。",
                "start_time": 41.5,
                "end_time": 47.2,
                "confidence": 0.98
            },
            {
                "text": "以上で説明を終わります。ご清聴ありがとうございました。",
                "start_time": 47.8,
                "end_time": 51.5,
                "confidence": 0.99
            },
        ],
        "duration": 51.5
    }


def get_demo_audio_features() -> dict:
    """デモ用の音声特徴量データを返す."""
    return {
        "speaking_rate": 325.4,
        "filler_words": [
            {"word": "えー", "count": 3, "timestamps": [7.0, 37.0, 37.5]},
            {"word": "あのー", "count": 1, "timestamps": [19.0]},
        ],
        "pauses": {
            "total": 8,
            "avg_duration": 0.4,
            "long_pauses": []
        }
    }


def get_demo_speech_analysis() -> dict:
    """デモ用の話し方分析結果を返す."""
    return {
        "analysis": {
            "speaking_rate": {
                "score": 0.85,
                "feedback": "話すスピードは適切です（325文字/分）。日本語プレゼンの標準的な速度である300-350文字/分の範囲内に収まっています。"
            },
            "filler_words": {
                "score": 0.6,
                "feedback": "フィラーワード「えー」が3回、「あのー」が1回検出されました。約51秒の発表で4回は若干多めです。意識的に減らすか、適切な間に置き換えることを推奨します。"
            },
            "pauses": {
                "score": 0.9,
                "feedback": "適切な間が取れています。長すぎるポーズはなく、聞きやすいリズムです。"
            }
        },
        "input_tokens": 850,
        "output_tokens": 320
    }


def get_demo_content_analysis() -> dict:
    """デモ用の内容分析結果を返す."""
    return {
        "structure": {
            "has_intro": True,
            "has_conclusion": True,
            "topic_transitions": ["まず最初に", "次に", "最後に"],
            "logical_flow_score": 0.9,
            "feedback": "導入・本題・まとめの構成がしっかりしており、トピック遷移も明確です。"
        },
        "language_quality": {
            "clarity_score": 0.85,
            "jargon_usage": ["AI", "AWS Transcribe", "Amazon Bedrock", "マルチエージェントシステム"],
            "repetitions": [],
            "feedback": "専門用語の使用は適切で、わかりやすい説明がなされています。"
        },
        "time_allocation": {
            "intro_duration": 11.2,
            "main_duration": 30.3,
            "conclusion_duration": 10.0,
            "balance_feedback": "イントロ、本題、まとめの時間配分が適切です。"
        },
        "input_tokens": 920,
        "output_tokens": 380
    }


def get_demo_final_report() -> dict:
    """デモ用の最終フィードバックレポートを返す."""
    return {
        "summary": "全体的に構成がしっかりしており、適切な話速で発表されています。フィラーワードが若干多いため、意識的に減らすことでより洗練されたプレゼンになるでしょう。",
        "strengths": [
            {
                "category": "プレゼン構成",
                "description": "導入・本題・まとめの三部構成が明確で、トピック遷移が自然です。「まず最初に」「次に」「最後に」といった接続表現を効果的に使っています。",
                "evidence": "構成スコア: 0.9/1.0"
            },
            {
                "category": "話すスピード",
                "description": "325文字/分という適切な速度で話されています。聞き手が理解しやすいペースです。",
                "evidence": "325文字/分（標準: 300-350文字/分）"
            },
            {
                "category": "専門用語の説明",
                "description": "技術用語を使いつつも、わかりやすい説明を心がけています。",
                "evidence": "言葉遣いスコア: 0.85/1.0"
            }
        ],
        "improvements": [
            {
                "category": "フィラーワード",
                "issue": "「えー」が3回、「あのー」が1回と、51秒の発表にしては若干多めです。",
                "suggestion": "発話前に一呼吸置くか、フィラーワードの代わりに短い間を取ることで、より洗練された印象を与えることができます。特に重要なポイントの前は、意図的に間を作ることで聞き手の注意を引くことができます。",
                "priority": "medium"
            },
            {
                "category": "時間配分",
                "issue": "全体で51秒と短めです。内容が豊富なため、もう少し時間をかけても良いでしょう。",
                "suggestion": "各セクションで具体例や詳細を追加することで、聞き手の理解を深めることができます。特に活用例については、実際のユースケースを1-2個紹介すると効果的です。",
                "priority": "low"
            }
        ],
        "detailed_feedback": {
            "speech_feedback": "話し方は全体的に安定しており、適切なペースで発表されています。フィラーワードの使用頻度を減らすことで、さらにプロフェッショナルな印象を与えることができます。",
            "content_feedback": "構成が論理的で、トピック遷移がスムーズです。専門用語の使用も適切で、聞き手に配慮した説明がなされています。",
            "overall_impression": "全体として完成度の高いプレゼンテーションです。構成力と話速のバランスが取れており、聞きやすい発表になっています。フィラーワードを意識的に減らすことで、より説得力のあるプレゼンになるでしょう。"
        },
        "input_tokens": 1500,
        "output_tokens": 650
    }
