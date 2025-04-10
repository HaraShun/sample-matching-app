import json

# JSON ファイルを読み込む
try:
    with open('sample.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)
except FileNotFoundError:
    print("Error: 'sample.json' ファイルが見つかりません。正しいパスを確認してください。")
    exit()

# 初期化
all_ids = set()
excluded_ids = set()
themes = set()
group_count = 0

# JSON データ内の各テーマを処理
for theme_data in json_data:
    theme_name = theme_data.get("theme", None)
    group_list = theme_data.get("group_list", None)
    
    # "group_list" が存在しない場合はスキップ
    if not group_list:
        continue
    
    # 切り捨てられたメンバー一覧の場合の処理
    if theme_name == "切り捨てられたメンバー一覧":
        for group in group_list:
            excluded_ids.update(group.get("id_list", []))
    
    # 他のテーマの場合の処理
    else:
        themes.add(theme_name)
        group_count += len(group_list)  # グループ数をカウント
        
        for group in group_list:
            all_ids.update(group.get("id_list", []))

# カウント結果
total_unique_ids = len(all_ids)  # 登場する総 ID 数
excluded_ids_count = len(excluded_ids)  # 「切り捨てられたメンバー一覧」内の総 ID 数
remaining_ids_count = total_unique_ids - excluded_ids_count  # 「切り捨てられたメンバー一覧」の ID 数を引いた数
unique_themes_count = len(themes)  # 作成された「theme」数

# 結果を表示
print("登場する総 ID 数:", total_unique_ids)
print("「切り捨てられたメンバー一覧」の ID 数を引いた ID 数:", remaining_ids_count)
print("作成された「theme」数:", unique_themes_count)
print("作成された「グループ」数:", group_count)
print("「切り捨てられたメンバー一覧」内に出現する総 ID 数:", excluded_ids_count)
