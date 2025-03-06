import boto3

# Bedrockクライアントの設定
bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-northeast-1')

# 利用可能なモデルIDを確認（オプション）
try:
    bedrock_models = boto3.client('bedrock', region_name='ap-northeast-1')
    models = bedrock_models.list_foundation_models()
    print("利用可能なモデル:")
    for model in models.get('modelSummaries', []):
        if 'claude' in model.get('modelId', '').lower():
            print(f"- {model.get('modelId')}")
except Exception as e:
    print(f"モデル一覧の取得に失敗: {e}")