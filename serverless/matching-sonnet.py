import boto3
import json
import psycopg2
import numpy as np
from sklearn.cluster import KMeans
import ast

# Bedrockクライアントの設定
bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-northeast-1')

# データベース接続
conn = psycopg2.connect(
    dbname="xx",
    user="xx",
    password="xx",
    host="xx.ap-northeast-1.rds.amazonaws.com",
    port="5432"
)

# ユーザーデータの取得
cur = conn.cursor()
cur.execute("SELECT id, embedding, chunks FROM bedrock_integration.bedrock_knowledge_base")
users = cur.fetchall()

# embeddings配列の作成
embeddings = np.array([ast.literal_eval(user[1]) for user in users])

# K-meansクラスタリングの実行
n_clusters = 1  # クラスター数は適宜調整してください
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(embeddings)

# クラスターごとのユーザー特性の分析
for cluster in range(n_clusters):
    cluster_users = [users[i] for i in range(len(users)) if cluster_labels[i] == cluster]
    cluster_chunks = " ".join([user[2] for user in cluster_users])
    
    # Claude 3.5 Sonnet を使用してクラスター特性の要約
    response = bedrock.converse(
        modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": f"Human: あなたはデータサイエンティストです。全社員のデータを閲覧しグループ分けできる権限を持っています。以下の条件を踏まえて、社員全員を趣味や好きな食べ物などの特徴をもとに、7人以下5人以上のグループに分類してください。\n\n条件:\n1.特徴:社員は趣味、好きな食べ物、特技などの特徴を持っています。\n2.グループサイズ:各グループは7名以下、5名以上としてください。\n3.分類基準:\n・趣味、食べ物、特技で最も共通点の多い人をグループ化してください。\n・同じ共通点で8人以上いる場合、7人以下5人以上のグループを複数作ってください。\n・どのグループにも入らない人はそれだけで一つのグループにしてください。\n・すべての人を必ずグループに分類してください。\n4.対象:社員全員\n5.出力形式:\n・各グループに共通項がわかる簡単なグループ名を付けてください。\n・各グループのメンバー全員のIDをリスト形式で表示してください。\n\n{cluster_chunks}\n\nAssistant:"
                    }
                ]
            }
        ],
        inferenceConfig={
            "temperature": 0,
            # 【 温度パラメータ 】
            # 生成される応答のランダム性を制御します
            # 0に設定すると、非常に決定的で再現性の高い応答が生成されます
            # 値が低いほど予測可能で一貫性のある出力になり、高いほど多様でクリエイティブな出力になります

            # "topP": 0.95,
            # 【 トップP/核サンプリング 】
            # 確率の累積分布からのトークン選択を制御します
            # 0.95に設定すると、確率の累積が95%に達するまでの最も可能性の高いトークンのみが考慮されます
            # 多様性とクオリティのバランスを取るのに役立ちます

            "maxTokens": 8192 # haiku の Max 値 4096, Sonnet 3.5 の Max 値 8192
        }
    )
    
    # レスポンスから回答を取得
    summary = response['output']['message']['content'][0]['text']
    
    print(f"Cluster {cluster} 特性:")
    print(summary.strip())
    print("---")

# データベース接続のクローズ
cur.close()
conn.close()