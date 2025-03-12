import random
import ast
import boto3
import json

# S3 クライアントの設定
s3 = boto3.client('s3', region_name='ap-northeast-1')

# テキストファイルを読み込む
def read_summary_file(file_name):
    try:
        with open(file_name, 'r') as f:
            content = f.read()
            return content
    except FileNotFoundError:
        print(f"File {file_name} not found.")
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
            ids = line.split("メンバーID: ")[1].strip()
            ids = ast.literal_eval(ids)
            group_ids[current_group_name].extend(ids)
    
    json_data = []
    for group_name, ids in group_ids.items():
        random.shuffle(ids)  # メンバー ID をシャッフル
        secondary_groups = []
        for i in range(0, len(ids), 8):
            secondary_group = ids[i:i+8]
            if len(secondary_group) >= 5:  # 5人以上の2次グループのみ
                secondary_groups.append(secondary_group)
        
        group_list = []
        for i, secondary_group in enumerate(secondary_groups):
            group_list.append({
                "group_id": i+1,
                "id_list": secondary_group
            })
        
        json_data.append({
            "theme": group_name,
            "group_list": group_list
        })
    
    return json_data

# JSON データを保存し、S3 にアップロード
def save_and_upload_json(json_data):
    with open("secondary_group_summary.json", "w") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
    
    # S3 バケット「例）hara-datasource」にアップロード
    s3.upload_file("secondary_group_summary.json", 'hara-datasource', "secondary_group_summary.json")

# メイン処理
if __name__ == "__main__":
    file_name = "cluster_0_summary.txt"
    summary = read_summary_file(file_name)
    
    if summary:
        json_data = regroup_ids(summary)
        print(json.dumps(json_data, indent=4, ensure_ascii=False))
        save_and_upload_json(json_data)
