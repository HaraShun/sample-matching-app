import boto3
import botocore
import traceback

BUCKET_NAME = "hoge"
KEY = "file_no2.txt"

s3 = boto3.client("s3")

def read_file_from_s3(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8').strip()
        return content
    except botocore.exceptions.ClientError as e:
        print(f"ファイル取得エラー: {e}")
        return None

def write_file_to_s3(bucket, key, content):
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=content.encode('utf-8'))
        print(f"{key} を更新しました: {content}")
    except Exception as e:
        print(f"ファイル更新エラー: {e}")

def main():
    flag = read_file_from_s3(BUCKET_NAME, KEY)
    
    if flag != "No2_ok_to_start":
        print("処理開始条件が満たされていません。終了します。")
        return

    try:
        # ▼▼▼ ここに実行したい処理を書く ▼▼▼
        print("処理を開始します...")
        # --- 模擬処理 (成功する処理) ---
        result = sum(range(100))  # ここを任意の処理に置き換えてください
        print(f"処理結果: {result}")
        # ▲▲▲ ここまで ▲▲▲

        # 成功したらファイル更新
        write_file_to_s3(BUCKET_NAME, KEY, "No2_completed_successfully")

    except Exception as e:
        print("処理中にエラーが発生しました。")
        traceback.print_exc()
        write_file_to_s3(BUCKET_NAME, KEY, "No2_failed")

if __name__ == "__main__":
    main()
