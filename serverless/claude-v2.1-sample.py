# knowledge_base_id = 'B2TTXCTYTP' # ナレッジベースIDを指定
# model_arn = 'arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
# ap-northeast-1
# ----------------------------------------------------

import boto3
import json
import os

# Bedrock クライアントの作成
bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))

def lambda_handler(event, context):
    try:
        # 社員情報（リクエストボディから取得、なければデフォルトデータ）
        employee_data = event.get("employee_data", [
            {"name": "Alice", "department": "Engineering", "role": "Software Engineer", "skills": ["Python", "AWS"]},
            {"name": "Bob", "department": "Engineering", "role": "DevOps Engineer", "skills": ["Terraform", "Kubernetes"]},
            {"name": "Charlie", "department": "HR", "role": "Recruiter", "skills": ["Interviewing", "HR Policies"]}
        ])

        # Claude のプロンプト
        prompt = f"""
        \n\nHuman: What is Alice's department?
        Please return the result in JSON format.

        Here is the employee data:
        {json.dumps(employee_data)}

        \n\nAssistant:
        """.strip()

        # モデルへのリクエスト
        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2:1",  # Claude v2 モデルを指定
            body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 1000})
        )

        # 結果を取得
        result = json.loads(response["body"].read())

        return {
            "statusCode": 200,
            "body": json.dumps({"completion": result.get("completion", "No response")})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
