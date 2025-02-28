import boto3
import json
import os

bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))
s3 = boto3.client("s3")

# Claude のモデル（Haiku なら claude-3-haiku-20240307）
MODEL_ID = "anthropic.claude-v2:1"

def get_json_from_s3(bucket, key):
    """ S3 から JSON ファイルを取得 """
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        print(f"S3 Error: {str(e)}")
        return None

def chunk_list(data, chunk_size):
    """ リストを chunk_size ごとに分割 """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def invoke_claude(employee_chunk):
    """ Claude にデータを送信してレスポンスを取得 """
    prompt = f"""
    \n\nHuman: You are a data processing assistant. 
    Your task is to group employees into logical clusters based on their department, role, and skills.
    Please return the result in JSON format.

    Here is the employee data:
    {json.dumps(employee_chunk)}

    \n\nAssistant:
    """.strip()

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 8000})
    )

    result = json.loads(response["body"].read())
    return result.get("completion", "No response")

def lambda_handler(event, context):
    try:
        s3_bucket = event.get("s3_bucket")
        s3_key = event.get("s3_key")

        if not s3_bucket or not s3_key:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing s3_bucket or s3_key"})}

        employee_data = get_json_from_s3(s3_bucket, s3_key)
        if not employee_data:
            return {"statusCode": 500, "body": json.dumps({"error": "Failed to load JSON from S3"})}

        # データを 500 件ごとに分割して処理
        chunk_size = 500
        results = []
        for chunk in chunk_list(employee_data, chunk_size):
            result = invoke_claude(chunk)
            results.append(result)

        return {
            "statusCode": 200,
            "body": json.dumps({"results": results})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
