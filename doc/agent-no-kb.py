aws bedrock-agent-runtime retrieve-and-generate \
  --session-id "session01" \
  --input '{"text": "MLB のドジャースの本拠地は？"}' \
  --retrieve-and-generate-configuration '{
    "type": "AGENT",
    "agent": {
      "agentId": "9T42WAYFKL",
      "agentAliasId": "3OBIYZOTZB"
    }
  }' \
  --region ap-northeast-1 \
  --output json

--------------------------------

import boto3

client = boto3.client("bedrock-agent-runtime", region_name="ap-northeast-1")

response_stream = client.invoke_agent(
    agentId="9T42WAYFKL",       # あなたの Agent ID
    agentAliasId="3OBIYZOTZB",          # エイリアス ID
    sessionId="session01",
    inputText="MLB のドジャースの本拠地は？"
)

for event in response_stream["completion"]:
    if "chunk" in event:
        print(event["chunk"]["bytes"].decode("utf-8"), end="")
    elif "trace" in event:
        print("\n[TRACE EVENT]", event["trace"])

#---------------------------------------------------

import boto3
from botocore.config import Config

# タイムアウト設定を追加
config = Config(
    read_timeout=300,  # 5分
    connect_timeout=60,  # 1分
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)

client = boto3.client(
    "bedrock-agent-runtime", 
    region_name="ap-northeast-1",
    config=config  # 設定を追加
)

response_stream = client.invoke_agent(
    agentId="9T42WAYFKL",
    agentAliasId="3OBIYZOTZB",
    sessionId="session01",
    inputText="MLB のドジャースの本拠地は？"
)

for event in response_stream["completion"]:
    if "chunk" in event:
        print(event["chunk"]["bytes"].decode("utf-8"), end="")
    elif "trace" in event:
        print("\n[TRACE EVENT]", event["trace"])
