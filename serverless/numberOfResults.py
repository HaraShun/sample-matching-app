import boto3
import json

def lambda_handler(event, context):

    # Bedrock Agentを初期化
    bedrock_agent = boto3.client(
        service_name='bedrock-agent-runtime',
        region_name='ap-northeast-1'  # 適切なリージョンに変更してください
    )

    """
    RetrieveAndGenerate APIを使用してKnowledge Baseからデータを取得し、
    大規模言語モデル（LLM）を使用して回答を生成します。
    これにより、単純な検索結果ではなく、自然言語による回答が得られます。
    """
    try:
        # RetrieveAndGenerateリクエストのパラメータ
        request_params = {
            'input': {
                'text': '2000名社員情報から特徴を鑑みてグルーピングして。ただし１グループの人数は 最小3人、最大8人までとして。'  # ユーザーの質問
            },
            'retrieveAndGenerateConfiguration': {
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': 'B2TTXCTYTP',  # Knowledge Base ID
                    'modelArn': 'arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0',  # 使用するモデル
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': '次の質問に対して、提供された情報のみを使用して回答してください。\n\n質問: {input}\n\nコンテキスト: $search_results$'
                        },
                        'inferenceConfig': {
                            'textInferenceConfig': {
                                'maxTokens': 8000
                            }
                        }
                    },
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': 100  # 検索で取得する結果の数
                        }
                    }
                }
            }
        }
        
        # RetrieveAndGenerate APIを呼び出し
        response = bedrock_agent.retrieve_and_generate(**request_params)
        
        # 生成された回答を表示
        print("生成された回答:")
        print(response['output']['text'])
        
        # 検索された参照情報を表示
        print("\n参照された情報:")
        for i, citation in enumerate(response['citations']):
            print(f"\n引用 {i+1}:")
            print(f"コンテンツ: {citation['retrievedReferences'][0]['content']['text']}")
            print(f"ソース: {citation['retrievedReferences'][0]['location']['s3Location']['uri']}")
            
        return response
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return None
