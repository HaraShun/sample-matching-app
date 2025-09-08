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
