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

all_ids = set()
excluded_ids = set()
themes = set()
group_count = 0

if sample_data:
    for theme_data in sample_data:
        theme_name = theme_data.get("theme", None)
        group_list = theme_data.get("group_list", None)

        if not group_list:
            continue

        if theme_name == "切り捨てられたメンバー一覧":
            for group in group_list:
                excluded_ids.update(group.get("id_list", []))
        else:
            themes.add(theme_name)
            group_count += len(group_list)
            for group in group_list:
                all_ids.update(group.get("id_list", []))

    total_unique_ids = len(all_ids)
    excluded_ids_count = len(excluded_ids)
    remaining_ids_count = total_unique_ids - excluded_ids_count
    unique_themes_count = len(themes)

else:
    total_unique_ids, excluded_ids_count, remaining_ids_count, unique_themes_count, group_count = 0, 0, 0, 0, 0

# hoge.jsonl の処理
hoge_data = download_and_load_jsonl(source_bucket, hoge_jsonl_path)

if hoge_data:
    matching_users_count = len(hoge_data)
else:
    matching_users_count = 0

# 結果の表示
results_message = (
    f"登場する総 ID 数: {total_unique_ids}\n"
    f"「切り捨てられたメンバー一覧」の ID 数を引いた ID 数: {remaining_ids_count}\n"
    f"作成された「theme」数: {unique_themes_count}\n"
    f"作成された「グループ」数: {group_count}\n"
    f"「切り捨てられたメンバー一覧」内に出現する総 ID 数: {excluded_ids_count}\n"
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
