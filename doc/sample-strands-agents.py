from strands import Agent
from strands.models import BedrockModel

# 東京リージョン用のモデルIDを使用
agent = Agent(
    model=BedrockModel(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",  # 東京リージョンで利用可能なモデル
        region="ap-northeast-1"
    )
)

agent("Strandsってどういう意味？")