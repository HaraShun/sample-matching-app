import boto3
import json

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
knowledge_base_id = 'B2TTXCTYTP'
model_arn = 'arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'

def lambda_handler(event, context):
    person_name = event.get('queryStringParameters', {}).get('name')
    
    if not person_name:
        return {
            'statusCode': 400,
            'body': json.dumps('Please provide a name parameter')
        }
    
    prompt = f"""
    {person_name}さんの情報を元に、簡潔な自己紹介文を一人称で書いてください。
    存在しない情報は含めず、与えられた情報のみを使用してください。
    """
    
    try:
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
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
