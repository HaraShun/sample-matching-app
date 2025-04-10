import json

# Load the JSON data from 'sample.json'
try:
    with open('sample.json', 'r', encoding='utf-8') as file:
        sample_data = json.load(file)
except FileNotFoundError:
    print("Error: 'sample.json' file not found.")
    sample_data = None

# Load the JSONL data from 'hoge.jsonl'
try:
    with open('hoge.jsonl', 'r', encoding='utf-8') as file:
        hoge_data = [json.loads(line) for line in file if line.strip()]
except FileNotFoundError:
    print("Error: 'hoge.jsonl' file not found.")
    hoge_data = None

# Initializations for sample.json processing
all_ids = set()
excluded_ids = set()
themes = set()
group_count = 0

if sample_data:
    # Process sample.json
    for theme_data in sample_data:
        theme_name = theme_data.get("theme", None)
        group_list = theme_data.get("group_list", None)

        # Skip if "group_list" is not present
        if not group_list:
            continue

        # Handle "切り捨てられたメンバー一覧"
        if theme_name == "切り捨てられたメンバー一覧":
            for group in group_list:
                excluded_ids.update(group.get("id_list", []))

        # Process other themes
        else:
            themes.add(theme_name)
            group_count += len(group_list)  # Count groups

            for group in group_list:
                all_ids.update(group.get("id_list", []))

    # Calculate results for sample.json
    total_unique_ids = len(all_ids)  # Total unique IDs
    excluded_ids_count = len(excluded_ids)  # Total IDs in "切り捨てられたメンバー一覧"
    remaining_ids_count = total_unique_ids - excluded_ids_count  # Remaining IDs count
    unique_themes_count = len(themes)  # Number of unique themes

else:
    total_unique_ids = 0
    excluded_ids_count = 0
    remaining_ids_count = 0
    unique_themes_count = 0
    group_count = 0

# Count the number of rows (users) in hoge.jsonl
if hoge_data:
    matching_users_count = len(hoge_data)
else:
    matching_users_count = 0

# Display results
print("マッチング対象のユーザ数:", matching_users_count)
print("マッチング生成後に登場する総 ID 数:", total_unique_ids)
print("「切り捨てられたメンバー一覧」の ID 数を引いた総 ID 数:", remaining_ids_count)
print("作成された「theme」数:", unique_themes_count)
print("作成された「グループ」数:", group_count)
print("「切り捨てられたメンバー一覧」内に出現する総 ID 数:", excluded_ids_count)
