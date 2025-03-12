import boto3
import json
import logging

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrock Agentクライアントの初期化
client = boto3.client('bedrock-agent')

def lambda_handler(event, context):
    try:
        # Knowledge Base IDとData Source IDを指定
        knowledge_base_id = 'hoge'  # 対象のKnowledge Base ID
        data_source_id = 'fuga'    # 対象のData Source ID

        # 同期処理を開始
        logger.info(f"Starting ingestion job for Knowledge Base: {knowledge_base_id}, Data Source: {data_source_id}")
        response = client.start_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id
        )

        # レスポンスをログに出力
        logger.info(f"Ingestion job started successfully: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Ingestion job started successfully', 'response': response})
        }
    except Exception as e:
        logger.error(f"Error starting ingestion job: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
