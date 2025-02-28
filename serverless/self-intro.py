import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
knowledge_base_id = 'B2TTXCTYTP'
model_arn = 'arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Check if the event is already a dict containing 'name'
        if isinstance(event, dict) and 'name' in event:
            person_name = event['name']
        else:
            # クエリパラメータとしてnameを指定する場合
            # person_name = event.get('queryStringParameters', {}).get('name')

            # If not, try to parse the body as JSON
            body = json.loads(event.get('body', '{}')) # JSONリクエストBodyをパース
            person_name = body.get('name')             # リクエストBodyからnameを取得する

        if not person_name:
            return {
                'statusCode': 400,
                'body': json.dumps('Please provide a name in the request')
            }
        
        prompt = f"""
        {person_name}さんの情報を元に、簡潔な自己紹介文を一人称で書いてください。
        存在しない情報は含めず、与えられた情報のみを使用してください。
        """
        
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': prompt,
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': knowledge_base_id,
                    'modelArn': model_arn
                }
            }
        )
        
        generated_text = response['output']['text']
        
        return {
            'statusCode': 200,
            'body': json.dumps(generated_text)
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid JSON in request body')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
