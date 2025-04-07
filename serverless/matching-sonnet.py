import boto3
import json
import psycopg2
import numpy as np
from sklearn.cluster import KMeans
import ast
import os

# Bedrockクライアントの設定
bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-northeast-1')

# S3 クライアントの設定
s3 = boto3.client('s3', region_name='ap-northeast-1')

# Secrets Managerからデータベース接続情報を取得する関数
def get_database_secret():
    secret_name = "your-database-secret-name"  # Secrets Managerに保存したシークレット名
    region_name = "ap-northeast-1"  # シークレットが保存されているリージョン
    
    # Secrets Managerクライアントの作成
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        # シークレット値の取得
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        
        # シークレット文字列の取得とJSONへの変換
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise

# データベース接続
def connect_to_database():
    # Secrets Managerからデータベース接続情報を取得
    db_credentials = get_database_secret()
    
    # 接続情報の取得
    dbname = db_credentials.get('dbname')
    user = db_credentials.get('username')
    password = db_credentials.get('password')
    host = db_credentials.get('host')
    port = db_credentials.get('port', '5432')
    
    # データベース接続
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    
    return conn

# メイン処理
conn = connect_to_database()

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

    # プロンプトを変数として定義
    prompt_template = f"""
    Human: あなたはデータ分析の専門家です。
        全社員のデータを閲覧しグループ分けできる権限を持っています。
        社員全員を最寄り駅でグループ分けし、さらに下記ルールでグループ分けしてください。

    グループ分けのルール:
    ・「キーワード」でグルーピングする。
    ・各グループの人数は6人以上100人以下とする。
    ・1人1つのグループに所属する。
    ・グループ名は直感的にわかりやすくする。

    出力形式:
    ・各グループのグループ名を表示する。
    ・出力するグループ名は必ず最後にグループをつける。
    ・各グループのメンバー全員のIDをリスト形式で表示する。
    ・各グループは、"メンバーID: []" の形式で出力する
    ・マッチング理由を説明する１文を追加する。

    {cluster_chunks}

    Assistant:
    """

    # 「Human:」: ユーザー（人間）からの入力や指示を示します。この部分には、AIがどのようなタスクを実行するかを指示する文が含まれます。
    # 「{cluster_chunks}」: クラスター分類されたデータの特徴や情報を表します。この部分は、実際にはデータベースから取得した情報を埋め込むためのプレースホルダーです。
    # 「Assistant:」: AIアシスタントが応答する部分を示します。AIは「Human:」で与えられた指示に基づいて、ここで回答を生成します。
    # この構造は、AIモデルが人間の指示に基づいて特定のタスクを実行し、結果を返すためのフレームワークです。


    # Claude 3.5 Sonnet を使用してクラスター特性の要約
    response = bedrock.converse(
        modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt_template
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

    # テキストファイルに保存
    with open(f"/tmp/cluster_{cluster}_grouping_result.txt", "w") as f:
        f.write(summary.strip())

    # S3 バケット「例）hara-datasource」にアップロード
    s3.upload_file(f"/tmp/cluster_{cluster}_grouping_result.txt", 'hara-datasource', f"cluster_{cluster}_grouping_result.txt")

# ------------------------------------------------------------------

# コサイン類似度による評価を追加
def evaluate_clustering_cosine(embeddings, cluster_labels):
    unique_clusters = set(cluster_labels)
    avg_similarities = []
    
    for cluster in unique_clusters:
        # クラスター内のデータポイントを取得
        cluster_points = embeddings[cluster_labels == cluster]
        
        # クラスター内のすべてのペア間のコサイン類似度を計算
        if len(cluster_points) > 1:
            from sklearn.metrics.pairwise import cosine_similarity
            similarity_matrix = cosine_similarity(cluster_points)
            # 対角要素(自分自身との類似度=1)を除外
            similarities = similarity_matrix[np.triu_indices(len(similarity_matrix), k=1)]
            avg_similarities.append(np.mean(similarities))
    
    return np.mean(avg_similarities) if avg_similarities else 0

# クラスタリング評価の実行
average_similarity = evaluate_clustering_cosine(embeddings, cluster_labels)
print(f"Average cosine similarity within clusters: {average_similarity}")

# 評価結果をS3にアップロード
with open("/tmp/clustering_evaluation.txt", "w") as f:
    f.write(f"Average cosine similarity within clusters: {average_similarity}")

s3.upload_file("/tmp/clustering_evaluation.txt", 'hara-datasource', "clustering_evaluation.txt")

# ------------------------------------------------------------------

# データベース接続のクローズ
cur.close()
conn.close()