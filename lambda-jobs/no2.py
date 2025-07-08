import boto3
import botocore

BUCKET_NAME = "hoge"
OBJECT_KEY = "go.txt"

s3 = boto3.client("s3")

def check_file_exists(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise  # その他のエラーは再スロー

def delete_file(bucket, key):
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        print(f"{key} を削除しました。")
    except Exception as e:
        print(f"{key} の削除中にエラーが発生しました: {e}")

def main():
    # ファイル存在チェック
    if not check_file_exists(BUCKET_NAME, OBJECT_KEY):
        raise FileNotFoundError(f"S3バケット '{BUCKET_NAME}' に '{OBJECT_KEY}' が存在しません。処理を中止します。")

    try:
        # メイン処理
        print("Hello, world")

    finally:
        # 最後に go.txt を削除
        delete_file(BUCKET_NAME, OBJECT_KEY)

if __name__ == "__main__":
    main()
