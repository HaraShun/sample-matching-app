import json

# 外部JSONファイルを読み込む
with open('data.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# グループ数をカウント
group_count = len(json_data)
print(f"グループ数: {group_count}")

# ID数をカウント
id_count = 0
for group in json_data:
    for item in group["group_list"]:
        id_count += len(item["id_lsit"])

print(f"ID数: {id_count}")
