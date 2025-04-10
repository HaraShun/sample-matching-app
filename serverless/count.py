import json
import boto3
from datetime import datetime
from dateutil import tz

# AWSクライアントの初期化
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# S3バケットとファイル情報
source_bucket = "source-bucket"
output_bucket = "output-bucket"
sample_json_path = "primary/sample.json"
hoge_jsonl_path = "hoge.jsonl"

# SNSトピックARN
sns_topic_arn = "arn:aws:sns:ap-northeast-1:123456789012:YourTopicName"

def get_time_based_message():
    """実行時間帯に応じたメッセージを生成"""
    jst = tz.gettz('Asia/Tokyo')
    current_hour = datetime.now(tz=jst).hour
    
    if 0 <= current_hour < 12:
        return "『趣味』の集計結果です"
    elif 12 <= current_hour < 17:
        return "『食べ物、飲み物』の集計結果です"
    else:
        return "『キーワード』の集計結果です"

def download_and_load_json(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        print(f"S3読み込みエラー: {e}")
        return None

def download_and_load_jsonl(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8').splitlines()
        return [json.loads(line) for line in content if line.strip()]
    except Exception as e:
        print(f"S3読み込みエラー: {e}")
        return None

# データ処理
sample_data = download_and_load_json(output_bucket, sample_json_path)
hoge_data = download_and_load_jsonl(source_bucket, hoge_jsonl_path)

total_ids = 0
excluded_ids_count = 0
themes = set()
group_count = 0

if sample_data:
    for theme_data in sample_data:
        theme_name = theme_data.get("theme")
        groups = theme_data.get("group_list", [])
        
        # 総ID数カウント（重複含む）
        for group in groups:
            total_ids += len(group.get("id_list", []))
        
        # 切り捨てられたメンバー処理
        if theme_name == "切り捨てられたメンバー一覧":
            excluded_ids_count += sum(len(g.get("id_list", [])) for g in groups)
        else:
            themes.add(theme_name)
            group_count += len(groups)

remaining_ids = total_ids - excluded_ids_count
unique_themes_count = len(themes)

# マッチングユーザ数（hoge.jsonlの行数）
matching_users = len(hoge_data) if hoge_data else 0

# 現在時刻を取得
jst = tz.gettz('Asia/Tokyo')
current_time_str = datetime.now(tz=jst).strftime("%A, %B %d, %Y, %I:%M %p JST")

# 時間帯に応じたメッセージを生成
time_message = get_time_based_message()

# 結果生成
result = f"""
{time_message}

現在時刻: {current_time_str}

登場する総 ID 数（重複含む）: {total_ids}
「切り捨てられたメンバー一覧」内ID数: {excluded_ids_count}
「切り捨てられたメンバー一覧」を除いたID数: {remaining_ids}
作成された「theme」数: {unique_themes_count}
作成された「グループ」数: {group_count}
マッチング対象ユーザ数: {matching_users}
"""

# SNS通知
try:
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=result,
        Subject=time_message  # 時間帯メッセージを件名に挿入
    )
    print("通知送信済み")
except Exception as e:
    print(f"SNSエラー: {e}")
