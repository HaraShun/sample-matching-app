import json
import boto3

# AWS クライアントの初期化
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# S3 バケットとファイル情報
source_bucket = "source-bucket"
output_bucket = "output-bucket"
sample_json_path = "primary/sample.json"
hoge_jsonl_path = "hoge.jsonl"

# SNS トピック ARN (事前に作成済みのものを指定)
sns_topic_arn = "arn:aws:sns:ap-northeast-1:123456789012:YourTopicName"

# S3 からファイルをダウンロードして読み込む関数
def download_and_load_json(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        print(f"Error loading JSON from S3: {e}")
        return None

def download_and_load_jsonl(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8').splitlines()
        return [json.loads(line) for line in content if line.strip()]
    except Exception as e:
        print(f"Error loading JSONL from S3: {e}")
        return None

# sample.json の処理
sample_data = download_and_load_json(output_bucket, sample_json_path)

total_ids_count = 0
excluded_ids_count = 0

if sample_data:
    for theme_data in sample_data:
        group_list = theme_data.get("group_list", [])
        
        # 総 ID 数をカウント
        for group in group_list:
            total_ids_count += len(group.get("id_list", []))
        
        # 「切り捨てられたメンバー一覧」内の ID 数をカウント
        if theme_data.get("theme") == "切り捨てられたメンバー一覧":
            for group in group_list:
                excluded_ids_count += len(group.get("id_list", []))

remaining_ids_count = total_ids_count - excluded_ids_count

# hoge.jsonl の処理
hoge_data = download_and_load_jsonl(source_bucket, hoge_jsonl_path)

if hoge_data:
    matching_users_count = len(hoge_data)
else:
    matching_users_count = 0

# 結果の表示
results_message = (
    f"登場する総 ID 数 (重複削除なし): {total_ids_count}\n"
    f"「切り捨てられたメンバー一覧」内に出現する ID 数 (重複削除なし): {excluded_ids_count}\n"
    f"「切り捨てられたメンバー一覧」の ID 数を引いた ID 数 (重複削除なし): {remaining_ids_count}\n"
    f"マッチング対象のユーザ数: {matching_users_count}"
)

print(results_message)

# SNS による結果通知
try:
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=results_message,
        Subject="データ処理結果通知"
    )
    print("SNS 通知が送信されました。")
except Exception as e:
    print(f"SNS 通知の送信中にエラーが発生しました: {e}")
