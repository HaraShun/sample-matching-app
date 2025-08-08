import json
import requests
import boto3
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Bedrock AgentからのリクエストをLiteLLMに転送するLambda関数
    """
    
    # LiteLLMのエンドポイント
    LITELLM_ENDPOINT = "https://litellm.jp/v1/chat/completions"
    
    try:
        # Bedrock Agentからのイベントをログ出力（デバッグ用）
        print(f"Received event: {json.dumps(event, ensure_ascii=False)}")
        
        # Bedrock Agentからの入力を取得
        # イベント構造は実際のBedrock Agentの設定によって異なる場合があります
        agent_input = event.get('inputText', '')
        session_id = event.get('sessionId', '')
        
        # LiteLLM用のリクエストペイロードを構築
        litellm_payload = {
            "model": "gpt-3.5-turbo",  # 使用したいモデルを指定
            "messages": [
                {
                    "role": "user",
                    "content": agent_input
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # LiteLLMにリクエストを送信
        headers = {
            "Content-Type": "application/json",
            # 必要に応じてAPIキーを追加
            # "Authorization": f"Bearer {os.environ.get('LITELLM_API_KEY')}"
        }
        
        response = requests.post(
            LITELLM_ENDPOINT,
            json=litellm_payload,
            headers=headers,
            timeout=30
        )
        
        # レスポンスの確認
        response.raise_for_status()
        litellm_response = response.json()
        
        # LiteLLMからのレスポンスを取得
        if 'choices' in litellm_response and len(litellm_response['choices']) > 0:
            ai_response = litellm_response['choices'][0]['message']['content']
        else:
            ai_response = "申し訳ございませんが、応答を生成できませんでした。"
        
        # Bedrock Agent用のレスポンス形式に変換
        bedrock_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "litellm_action_group",
                "function": "send_to_litellm",
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": ai_response
                        }
                    }
                }
            },
            "sessionAttributes": {
                "sessionId": session_id
            }
        }
        
        print(f"Sending response: {json.dumps(bedrock_response, ensure_ascii=False)}")
        return bedrock_response
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        error_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "litellm_action_group", 
                "function": "send_to_litellm",
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": f"エラーが発生しました: {str(e)}"
                        }
                    }
                }
            }
        }
        return error_response
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        error_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "litellm_action_group",
                "function": "send_to_litellm", 
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": f"予期しないエラーが発生しました: {str(e)}"
                        }
                    }
                }
            }
        }
        return error_response


# 代替案: より詳細なエラーハンドリングとログ機能付きバージョン
def enhanced_lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    拡張版: より詳細なログとエラーハンドリング
    """
    
    # CloudWatch Logsにログを記録
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    LITELLM_ENDPOINT = "https://litellm.jp/v1/chat/completions"
    
    try:
        logger.info(f"Lambda invoked with event: {json.dumps(event, ensure_ascii=False)}")
        
        # 入力の検証
        if 'inputText' not in event:
            raise ValueError("inputText not found in event")
            
        agent_input = event['inputText']
        session_id = event.get('sessionId', 'unknown')
        
        # 空の入力チェック
        if not agent_input.strip():
            raise ValueError("Empty input text provided")
        
        # LiteLLMリクエストの準備
        litellm_payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system", 
                    "content": "あなたは親切で知識豊富なAIアシスタントです。"
                },
                {
                    "role": "user",
                    "content": agent_input
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"Sending request to LiteLLM: {json.dumps(litellm_payload, ensure_ascii=False)}")
        
        # LiteLLMにリクエスト送信
        response = requests.post(
            LITELLM_ENDPOINT,
            json=litellm_payload,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"LiteLLM response status: {response.status_code}")
        
        response.raise_for_status()
        litellm_response = response.json()
        
        logger.info(f"LiteLLM response: {json.dumps(litellm_response, ensure_ascii=False)}")
        
        # レスポンス解析
        ai_response = litellm_response['choices'][0]['message']['content']
        
        # Bedrock Agent形式のレスポンス
        bedrock_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "litellm_action_group",
                "function": "send_to_litellm",
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": ai_response
                        }
                    }
                }
            },
            "sessionAttributes": {
                "sessionId": session_id,
                "timestamp": context.aws_request_id
            }
        }
        
        logger.info("Successfully processed request")
        return bedrock_response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        
        error_response = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "litellm_action_group",
                "function": "send_to_litellm",
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {
                            "body": f"処理中にエラーが発生しました。管理者にお問い合わせください。（エラーID: {context.aws_request_id}）"
                        }
                    }
                }
            }
        }
        return error_response