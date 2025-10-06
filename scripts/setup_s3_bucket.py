#!/usr/bin/env python3
"""S3バケット作成スクリプト."""

import os
import sys

import boto3
from botocore.exceptions import ClientError


def setup_s3_bucket(bucket_name: str, region: str = "us-west-2"):
    """
    Transcribe用のS3バケットを作成.

    Args:
        bucket_name: バケット名
        region: AWSリージョン
    """
    s3_client = boto3.client("s3", region_name=region)

    try:
        # バケットの存在確認
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✓ バケット '{bucket_name}' は既に存在します")
            return
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code != "404":
                raise

        # バケット作成
        if region == "us-east-1":
            # us-east-1の場合はLocationConstraintを指定しない
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )

        print(f"✓ バケット '{bucket_name}' を作成しました")

        # ライフサイクルポリシー設定（30日後に自動削除）
        lifecycle_policy = {
            "Rules": [
                {
                    "Id": "DeleteOldTranscriptionFiles",
                    "Status": "Enabled",
                    "Filter": {"Prefix": "input/"},
                    "Expiration": {"Days": 30},
                }
            ]
        }

        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name, LifecycleConfiguration=lifecycle_policy
        )

        print(f"✓ ライフサイクルポリシーを設定しました（30日後に自動削除）")

        # パブリックアクセスブロック設定（セキュリティ強化）
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )

        print(f"✓ パブリックアクセスブロックを設定しました")

    except ClientError as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 環境変数またはデフォルト値を使用
    bucket_name = os.getenv("TRANSCRIBE_S3_BUCKET", "presentation-feedback")
    region = os.getenv("AWS_REGION", "us-west-2")

    print(f"S3バケットをセットアップします:")
    print(f"  バケット名: {bucket_name}")
    print(f"  リージョン: {region}")
    print()

    setup_s3_bucket(bucket_name, region)

    print()
    print("セットアップ完了!")
    print(f"環境変数に以下を設定してください:")
    print(f"  export TRANSCRIBE_S3_BUCKET={bucket_name}")
    print(f"  export AWS_REGION={region}")
