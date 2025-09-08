from strands import Agent
from strands.models import BedrockModel
import boto3
import json
import uuid
import os
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む（もし存在すれば）
load_dotenv()

class BedrockAgentCaller:
    """Bedrock Agent を呼び出すためのヘルパークラス"""
    
    def __init__(self, agent_id: str, alias_id: str, region: str = "ap-northeast-1"):
        self.agent_id = agent_id
        self.alias_id = alias_id
        self.region = region
        self.client = boto3.client('bedrock-agent-runtime', region_name=region)
        
    def invoke(self, query: str, session_id: str = None) -> str:
        """Bedrock Agent を呼び出す"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        try:
            print(f"[DEBUG] Bedrock Agent を呼び出しています...")
            print(f"[DEBUG] Agent ID: {self.agent_id}, Alias ID: {self.alias_id}")
            
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.alias_id,
                sessionId=session_id,
                inputText=query
            )
            
            # ストリーミングレスポンスを処理
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
            
            print(f"[DEBUG] Bedrock Agent のレスポンス取得成功")
            return result
            
        except Exception as e:
            print(f"[ERROR] Bedrock Agent 呼び出しエラー: {str(e)}")
            return None

# 環境変数から Bedrock Agent の設定を読み取る
BEDROCK_AGENT_ID = os.getenv('BEDROCK_AGENT_ID', '9T42WAYFKL')
BEDROCK_AGENT_ALIAS_ID = os.getenv('BEDROCK_AGENT_ALIAS_ID', 'W5JNH4IVHR')
BEDROCK_REGION = os.getenv('BEDROCK_REGION', 'ap-northeast-1')

# Strands Agent の設定も環境変数から読み取り可能に
STRANDS_MODEL_ID = os.getenv('STRANDS_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
STRANDS_REGION = os.getenv('STRANDS_REGION', 'ap-northeast-1')

# 設定値を表示（デバッグ用）
print(f"[CONFIG] Bedrock Agent ID: {BEDROCK_AGENT_ID}")
print(f"[CONFIG] Bedrock Agent Alias ID: {BEDROCK_AGENT_ALIAS_ID}")
print(f"[CONFIG] Bedrock Region: {BEDROCK_REGION}")
print(f"[CONFIG] Strands Model ID: {STRANDS_MODEL_ID}")
print(f"[CONFIG] Strands Region: {STRANDS_REGION}")

# Bedrock Agent 呼び出し用のインスタンスを作成
bedrock_agent_caller = BedrockAgentCaller(
    agent_id=BEDROCK_AGENT_ID,
    alias_id=BEDROCK_AGENT_ALIAS_ID,
    region=BEDROCK_REGION
)

# Strands Agent を作成（Claude 3 Haiku を使用）
strands_agent = Agent(
    model=BedrockModel(
        model_id=STRANDS_MODEL_ID,
        region=STRANDS_REGION
    )
)

def call_with_bedrock_agent(query: str) -> str:
    """
    必要に応じて Bedrock Agent を呼び出しながら回答する
    """
    # 特定のキーワードチェック
    use_bedrock = any(keyword in query for keyword in ["詳細", "専門的", "最新", "リアルタイム", "Bedrock Agent"])
    
    if use_bedrock:
        print(f"\n[INFO] Bedrock Agent を使用します")
        
        # Bedrock Agent を呼び出す
        bedrock_response = bedrock_agent_caller.invoke(query)
        
        if bedrock_response:
            # Strands Agent に Bedrock Agent の回答を含めて処理させる
            prompt = f"""
以下の情報に基づいて、ユーザーの質問に答えてください。

ユーザーの質問: {query}

Bedrock Agent からの情報:
{bedrock_response}

この情報を参考に、分かりやすく回答してください。
"""
            response = strands_agent(prompt)
        else:
            # Bedrock Agent の呼び出しに失敗した場合
            response = strands_agent(f"{query}\n\n（注：Bedrock Agent への接続に問題が発生したため、私の知識のみで回答します）")
    else:
        # 通常の Strands Agent の処理
        print(f"\n[INFO] Strands Agent のみで回答します")
        response = strands_agent(query)
    
    return response

# 使用例
if __name__ == "__main__":
    print("\n" + "="*50 + "\n")
    
    print("=== テスト1: 通常の質問 ===")
    response1 = call_with_bedrock_agent("Strandsってどういう意味？")
    print(response1)
    
    print("\n" + "="*50 + "\n")
    
    print("=== テスト2: Bedrock Agent を明示的に使う ===")
    response2 = call_with_bedrock_agent("Bedrock Agent を使って、「MLB のマリナーズの本拠地」を教えて")
    print(response2)
    
    print("\n" + "="*50 + "\n")
    
    # テスト用エイリアスも環境変数から読み取り可能
    TEST_ALIAS_ID = os.getenv('BEDROCK_AGENT_TEST_ALIAS_ID', 'TSTALIASID')
    
    print("=== テスト3: テストエイリアスを使用 ===")
    test_caller = BedrockAgentCaller(
        agent_id=BEDROCK_AGENT_ID,
        alias_id=TEST_ALIAS_ID,  # テスト用エイリアス
        region=BEDROCK_REGION
    )
    test_response = test_caller.invoke("Hello, Bedrock Agent!")
    if test_response:
        print(f"テストエイリアスのレスポンス: {test_response}")