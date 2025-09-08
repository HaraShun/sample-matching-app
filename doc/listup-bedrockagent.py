import boto3
import json

def check_bedrock_agent():
    """Bedrock Agent の状態を確認"""
    
    # 複数のリージョンで確認
    regions = ['ap-northeast-1', 'us-east-1', 'us-west-2']
    
    for region in regions:
        print(f"\n=== リージョン: {region} ===")
        try:
            # Bedrock Agent クライアント（管理用）
            client = boto3.client('bedrock-agent', region_name=region)
            
            # エージェント一覧を取得
            response = client.list_agents()
            
            if response['agentSummaries']:
                print("見つかったエージェント:")
                for agent in response['agentSummaries']:
                    print(f"  - ID: {agent['agentId']}")
                    print(f"    名前: {agent['agentName']}")
                    print(f"    状態: {agent['agentStatus']}")
                    
                    # エイリアスを確認
                    try:
                        aliases = client.list_agent_aliases(agentId=agent['agentId'])
                        if aliases['agentAliasSummaries']:
                            print("    エイリアス:")
                            for alias in aliases['agentAliasSummaries']:
                                print(f"      - ID: {alias['agentAliasId']}")
                                print(f"        名前: {alias['agentAliasName']}")
                    except:
                        pass
            else:
                print("エージェントが見つかりません")
                
        except Exception as e:
            print(f"エラー: {str(e)}")

if __name__ == "__main__":
    check_bedrock_agent()