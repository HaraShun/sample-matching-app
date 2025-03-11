import random
import ast
import boto3

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
    
    for group_name, ids in group_ids.items():
        random.shuffle(ids)  # メンバー ID をシャッフル
        secondary_groups = []
        for i in range(0, len(ids), 8):
            secondary_group = ids[i:i+8]
            secondary_groups.append(secondary_group)
        
        groups.append((group_name, secondary_groups))
    
    return groups

# 2次グループを表示し、テキストファイルに保存
def print_and_save_secondary_groups(groups):
    result = ""  # result 変数を定義
    for group_name, secondary_groups in groups:
        result += f"{group_name}:\n"
        for i, secondary_group in enumerate(secondary_groups):
            if len(secondary_group) >= 5:  # 5人以上の2次グループのみ表示
                result += f"2次グループ {i+1}: {secondary_group}\n"
        result += "\n"
    
    print(result)  # 結果をコンソールに表示
    
    # テキストファイルに保存
    with open("secondary_group_summary.txt", "w") as f:
        f.write(result)
    
    # S3 バケット「例）hara-datasource」にアップロード
    s3.upload_file("secondary_group_summary.txt", 'hara-datasource', "secondary_group_summary.txt")

# メイン処理
if __name__ == "__main__":
    file_name = "cluster_0_summary.txt"
    summary = read_summary_file(file_name)
    
    if summary:
        groups = regroup_ids(summary)
        print_and_save_secondary_groups(groups)
