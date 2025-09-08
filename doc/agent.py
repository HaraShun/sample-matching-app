#    agentId="9T42WAYFKL",       # あなたの Agent ID
#    agentAliasId="3OBIYZOTZB",          # エイリアス ID
#    sessionId="session01",
#    inputText="MLB のドジャースの本拠地は？"

import boto3
import json

# Bedrock Agent Runtime クライアントを作成
client = boto3.client("bedrock-agent-runtime", region_name="ap-northeast-1")

# ユーザー入力
user_input = "MLB のタイガースの本拠地は？"

# ユーザー入力を拡張
wrapped_input = (
    "不確かでも推測して答えてください。正確でない場合は「正確ではありませんが」と前置きしてください。\n"
    f"質問: {user_input}"
)

# エージェント呼び出し
response = client.invoke_agent(
    agentId="9T42WAYFKL",       # あなたの Agent ID
    agentAliasId="3OBIYZOTZB",          # エイリアス ID
    sessionId="session01",
    inputText=wrapped_input
)

# 出力を整形して表示
for event in response["completion"]:
    if "chunk" in event:
        print(event["chunk"]["bytes"].decode("utf-8"), end="")
    elif "internalServerException" in event:
        print(f"Error: {event['internalServerException']['message']}")
    elif "validationException" in event:
        print(f"Validation Error: {event['validationException']['message']}")
    elif "throttlingException" in event:
        print(f"Throttling Error: {event['throttlingException']['message']}")
    elif "serviceUnavailableException" in event:
        print(f"Service Unavailable: {event['serviceUnavailableException']['message']}")
