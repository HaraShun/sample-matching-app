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
n_clusters = 5  # クラスター数は適宜調整してください
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(embeddings)

# クラスターごとのユーザー特性の分析
for cluster in range(n_clusters):
    cluster_users = [users[i] for i in range(len(users)) if cluster_labels[i] == cluster]
    cluster_chunks = " ".join([user[2] for user in cluster_users])
    
    # Claude 3 Haikuを使用してクラスター特性の要約
    response = bedrock.converse(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": f"Human: あなたはデータサイエンティストです。全社員のデータを閲覧しグループ分けできる権限を持っています。社員全員を趣味や好きな食べ物などの特徴をもとに、以下の条件で7人以下5人以上のグループに分類してください。・まず最寄り駅で正確に分けてしてください。・最も共通点の多い人同士をグループ化してください。・すべての人を必ずどこかのグループに分類してください。グループ分けの結果は以下の形式で出力してください。・各グループに共通項がわかる簡単なグループ名を付けてください。・各グループのメンバー全員のIDをリスト形式で表示してください。\n\n{cluster_chunks}\n\nAssistant:"
                    }
                ]
            }
        ],
        inferenceConfig={
            "temperature": 0.7,
            "topP": 0.95,
            "maxTokens": 4096 # haiku の Max 値
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