import boto3
import logging
import json

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class GetIntroduction:
    """他己紹介取得"""
    def __init__(self, prompt):
        self.BEDROCK = boto3.client('bedrock-runtime')
        self.MODEL_ID = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
        self.prompt = prompt

    def get_introduction(self):
        """他己紹介生成・返却"""
        try:
            # Bedrockに送信するリクエストボディを作成
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "messages": [
                    {
                        "role": "user",
                        "content": self.prompt
                    }
                ],
                "temperature": 0,
                "top_p": 1
            })

            # Bedrockにリクエストを送信
            response = self.BEDROCK.invoke_model(
                modelId=self.MODEL_ID,
                body=body
            )
            
            # レスポンスから生成されたテキストを抽出
            response_body = json.loads(response['body'].read().decode('utf-8'))
            introduction = response_body['content'][0]['text']

            return introduction
        except Exception as e:
            logger.error(f"他己紹介の生成に失敗しました: {str(e)}", exc_info=True)
            raise Exception(f"他己紹介の生成に失敗しました: {str(e)}")
