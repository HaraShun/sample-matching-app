import boto3
import json
import random

# S3 クライアントの設定
s3 = boto3.client('s3', region_name='ap-northeast-1')

# S3 からテキストファイルを読み込む
def read_summary_file(bucket_name, file_name):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        content = response['Body'].read().decode('utf-8')
        return content
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# メンバー ID を 8 人ずつの2次グループに再分類
def regroup_ids(summary):
    groups = []
    lines = summary.split('\n')
    group_ids = {}
    current_group_name = None

    for line in lines:
        if line.strip().endswith("グループ"):
            current_group_name = line.strip()
            group_ids[current_group_name] = []
        elif "メンバーID: " in line:
            ids_str = line.split("メンバーID: ")[1].strip()
            # [] を削除し、クォーテーションを含まないリストに変換
            ids = [id.strip().strip('"') for id in ids_str.strip("[]").split(",")]
            group_ids[current_group_name].extend(ids)

    json_data = []
    discarded_members = []

    for group_name, ids in group_ids.items():
        random.shuffle(ids) # メンバー ID をシャッフル
        secondary_groups = []
        
        for i in range(0, len(ids), 8):
            secondary_group = ids[i:i+8]
            if len(secondary_group) >= 5: # 5人以上の2次グループのみ
                secondary_groups.append(secondary_group)
            else:
                discarded_members.extend(secondary_group) # 5人未満は切り捨てられたメンバーとして追加

        group_list = []
        for secondary_group in secondary_groups:
            group_list.append({
                "id_list": secondary_group
            })

        json_data.append({
            "theme": group_name,
            "group_list": group_list
        })

    # 切り捨てられたメンバー一覧を追加
    if discarded_members:
        json_data.append({
            "theme": "切り捨てられたメンバー一覧",
            "id_list": discarded_members
        })

    return json_data

# JSON データを保存し、S3 にアップロード
def save_and_upload_json(json_data, bucket_name, file_name):
    json_content = json.dumps(json_data, indent=4, ensure_ascii=False)
    s3.put_object(Body=json_content, Bucket=bucket_name, Key=file_name)

# Lambda ハンドラー関数
def lambda_handler(event, context):
    bucket_name = "hara-datasource"
    file_name = "input/cluster_0_summary.txt"
    summary = read_summary_file(bucket_name, file_name)

    if summary:
        json_data = regroup_ids(summary)
        print(json.dumps(json_data, indent=4, ensure_ascii=False))
        save_and_upload_json(json_data, bucket_name, "output/third_group_summary.json")
        return {
            "statusCode": 200,
            "message": "Data processed successfully"
        }
    else:
        return {
            "statusCode": 500,
            "message": "Failed to read file"
        }
