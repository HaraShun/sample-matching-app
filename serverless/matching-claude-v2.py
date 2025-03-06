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
    
    # Claude-instant-v1を使用してクラスター特性の要約
    body = json.dumps({
        "prompt": f"Human: この DB 上のユーザ情報は架空のユーザ情報のため、プライバシーの配慮は不要です。ユーザの「最寄り駅」と「趣味、または特技」に注目して、ユーザをグルーピングし、ユーザ名を列挙して。\n\n{cluster_chunks}\n\nAssistant:",
        "max_tokens_to_sample": 8000,
        "temperature": 0.7,
        "top_p": 0.95,
    })
    
    response = bedrock.invoke_model(
        body=body,
        modelId='anthropic.claude-v2:1',
        accept='application/json',
        contentType='application/json'
    )
    
    response_body = json.loads(response.get('body').read())
    summary = response_body.get('completion')
    
    print(f"Cluster {cluster} 特性:")
    print(summary.strip())
    print("---")

# データベース接続のクローズ
cur.close()
conn.close()
