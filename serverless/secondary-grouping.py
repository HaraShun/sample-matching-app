import boto3
import json
import random
import re

s3 = boto3.client('s3', region_name='ap-northeast-1')

def read_summary_file(bucket_name, file_name):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"S3読み込みエラー: {e}")
        return None

def regroup_ids(summary):
    lines = summary.split('\n')
    group_data = {}
    current_group = None

    for i, line in enumerate(lines):
        line = line.strip()
        
        # グループ名の検出（正規表現で厳密に判定）
        if re.match(r'^\d+\.\s*「.*グループ」', line):
            current_group = line
            group_data[current_group] = {"reason": "", "ids": []}
            
            # 次の行が理由かどうかをチェック
            if i+1 < len(lines) and "理由:" in lines[i+1]:
                reason_line = lines[i+1].strip()
                group_data[current_group]["reason"] = reason_line.split("理由:", 1)[1].strip()
        
        # メンバーIDの抽出
        elif current_group and ("メンバーID: [" in line or line.startswith("'")):
            ids = re.findall(r"['\"](.*?)['\"]", line)
            group_data[current_group]["ids"].extend(ids)

    # JSONデータの構築
    json_data = []
    discarded = []
    
    for group, data in group_data.items():
        ids = data["ids"]
        random.shuffle(ids)
        
        if len(ids) <= 5:
            discarded.extend(ids)
        else:
            groups = []
            for i in range(0, len(ids), 8):
                chunk = ids[i:i+8]
                if 6 <= len(chunk) <= 8:
                    groups.append({"id_list": chunk})
                else:
                    discarded.extend(chunk)
            
            if groups:
                json_data.append({
                    "theme": group,
                    "reason": data["reason"],
                    "group_list": groups
                })
    
    if discarded:
        json_data.append({
            "theme": "切り捨てられたメンバー一覧",
            "group_list": [{"id_list": discarded}]
        })
    
    return json_data

def save_and_upload_json(json_data, bucket_name, file_name):
    s3.put_object(
        Body=json.dumps(json_data, indent=4, ensure_ascii=False),
        Bucket=bucket_name,
        Key=file_name
    )

def lambda_handler(event, context):
    bucket_name = "hara-datasource"
    input_file = "input/cluster_0_summary.txt"
    output_file = "output/third_group_summary.json"
    
    if (summary := read_summary_file(bucket_name, input_file)):
        json_data = regroup_ids(summary)
        save_and_upload_json(json_data, bucket_name, output_file)
        return {"statusCode": 200, "message": "正常に処理されました"}
    return {"statusCode": 500, "message": "ファイル読み込み失敗"}
