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

# メンバー ID を再分類
def regroup_ids(summary):
    lines = summary.split('\n')
    group_ids = {}
    group_reasons = {}  # グループごとの理由を保存
    current_group_name = None
    current_reason = ""
    # ID収集の状態を追跡
    collecting_ids = False
    current_ids = []

    for i, line in enumerate(lines):
        # グループ名行を検出
        if line.strip() and "グループ" in line:
            # 前のグループのIDと理由を保存（存在する場合）
            if current_group_name and current_ids:
                group_ids[current_group_name] = current_ids
                group_reasons[current_group_name] = current_reason
            # 新しいグループの開始
            current_group_name = line.strip()
            current_ids = []
            collecting_ids = False
            current_reason = ""
            # 次の行が理由の場合、取得
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("理由:"):
                current_reason = lines[i + 1].strip()[3:].strip()
        # ID行の開始を検出
        elif "メンバーID: [" in line:
            collecting_ids = True
            # 同じ行にIDがある場合は処理
            id_part = line.split("メンバーID: [")[1].strip()
            if id_part and id_part != "]":
                # カンマで区切られたIDを処理
                ids = [id.strip().strip('"').strip("'") for id in id_part.rstrip("]").split(",")]
                current_ids.extend([id for id in ids if id])
        # ID収集中の行を処理
        elif collecting_ids:
            # "]" だけの行を検出して収集終了
            if line.strip() == "]":
                collecting_ids = False
            else:
                # IDを抽出
                line = line.strip()
                if line:
                    # 末尾の "]" を削除
                    if line.endswith("]"):
                        line = line[:-1]
                    # カンマで区切られたIDを処理
                    ids = [id.strip().strip('"').strip("'") for id in line.split(",")]
                    current_ids.extend([id for id in ids if id])

    # 最後のグループのIDと理由を保存
    if current_group_name and current_ids:
        group_ids[current_group_name] = current_ids
        group_reasons[current_group_name] = current_reason

    # 結果のJSONデータ構造
    json_data = []
    discarded_members = []

    # グループの再編成
    for group_name, ids in group_ids.items():
        random.shuffle(ids) # メンバー ID をシャッフル
        reason = group_reasons.get(group_name, "")
        if len(ids) <= 5: # 5人以下は切り捨てられたメンバーとして追加
            discarded_members.extend(ids)
        elif len(ids) <= 8: # 6人以上8人以下はそのまま
            json_data.append({
                "theme": group_name,
                "reason": reason,  # 理由を追加
                "group_list": [{"id_list": ids}]
            })
        else: # 9人以上は8人ずつのグループに分ける
            secondary_groups = []
            for i in range(0, len(ids), 8):
                secondary_group = ids[i:i+8]
                # グループサイズをチェック
                if len(secondary_group) <= 5 and i + 8 >= len(ids):
                    # 最後のグループが5人以下なら切り捨てる
                    discarded_members.extend(secondary_group)
                else:
                    secondary_groups.append({"id_list": secondary_group})
            if secondary_groups: # 空でない場合のみ追加
                json_data.append({
                    "theme": group_name,
                    "reason": reason,  # 理由を追加
                    "group_list": secondary_groups
                })

    # 切り捨てられたメンバー一覧を追加
    if discarded_members:
        json_data.append({
            "theme": "切り捨てられたメンバー一覧",
            "group_list": [{"id_list": discarded_members}]
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
