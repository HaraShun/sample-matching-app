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
                'text': '2000名社員情報から特徴を鑑みてグルーピングして。ただし1グループの人数は 最小3人、最大8人までとしてください。そして必ずどこかのグループに属させてください。グループのメンバーを列挙してください。どのような特徴でグルーピングしたのかも述べてください。'  # ユーザーの質問
            },
            'retrieveAndGenerateConfiguration': {
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': 'B2TTXCTYTP',  # Knowledge Base ID
                    'modelArn': 'arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0',  # 使用するモデル
                    # 'modelArn': 'arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0',  # 使用するモデル
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': '次の質問に対して、提供された情報のみを使用して回答してください。\n\n質問: {input}\n\nコンテキスト: $search_results$'
                        },
                        'inferenceConfig': {
                            'textInferenceConfig': {
                                'maxTokens': 8192
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
        
        # レスポンスの構造を安全に処理する
        print("\n参照された情報:")
        if 'citations' in response and response['citations']:
            for i, citation in enumerate(response['citations']):
                print(f"\n引用 {i+1}:")
                
                # retrievedReferencesが存在し、空でないことを確認
                if ('retrievedReferences' in citation and 
                    citation['retrievedReferences'] and 
                    len(citation['retrievedReferences']) > 0):
                    
                    ref = citation['retrievedReferences'][0]
                    
                    # contentとtextが存在することを確認
                    if 'content' in ref and 'text' in ref['content']:
                        print(f"コンテンツ: {ref['content']['text']}")
                    else:
                        print("コンテンツ情報がありません")
                    
                    # locationとs3Locationが存在することを確認
                    if ('location' in ref and 
                        's3Location' in ref['location'] and 
                        'uri' in ref['location']['s3Location']):
                        print(f"ソース: {ref['location']['s3Location']['uri']}")
                    else:
                        print("ソース情報がありません")
                else:
                    print("この引用には参照情報がありません")
        else:
            print("引用情報がレスポンスに含まれていません")
        
        # デバッグ用: レスポンス全体の構造を確認（必要に応じてコメント解除）
        # print("\nレスポンス全体の構造:")
        # print(json.dumps(response, default=str, indent=2))
            
        return response
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        print(f"エラーの詳細: {e.__class__.__name__}")
        import traceback
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'error_type': e.__class__.__name__
            })
        }