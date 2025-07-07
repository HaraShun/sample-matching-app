import json

# JSONファイルの内容とファイル名
json_data = {"message": "Hello I`m No1"}
json_filename = "file_no1.json"

# テキストファイルの内容とファイル名
text_data = "No2_ok_to_start"
text_filename = "file_no2.txt"

# JSONファイルの作成
with open(json_filename, "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=2)

# テキストファイルの作成
with open(text_filename, "w", encoding="utf-8") as text_file:
    text_file.write(text_data)

print("両方のファイルを生成しました。")
