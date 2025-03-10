import boto3
import json
import psycopg2
import numpy as np
from sklearn.cluster import KMeans
import ast
import os

# Bedrockクライアントの設定
bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-northeast-1')

# データベース接続
conn = psycopg2.connect(
    dbname=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT', '5432')  # デフォルト値を設定
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

    # プロンプトを変数として定義
    prompt_template = f"""
    Human: あなたはデータサイエンティストです。
    全社員のデータを閲覧しグループ分けできる権限を持っています。
    社員全員を趣味や好きな食べ物などの特徴をもとにグループに分類してください。

    分類基準:
    ・趣味、食べ物、出身地、特技で最も共通点の多い人をグループにしてください。
    ・最寄り駅は考慮しない。
    ・一つのグループは7人以下5人以上。
    ・同じ共通点で8人以上いる場合、7人以下5人以上のグループに分割して全員を入れてください。
    ・同じ名前のグループをそのグループに入る全員がもれなくは入れる数だけ作る。
    ・どのグループにも入らない人はそれだけで一つのグループにしてください。

    出力形式:
    ・各グループに共通項がわかる簡単なグループ名を付けてください。
    ・各グループのメンバー全員のIDをリスト形式で表示してください。

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
            "temperature": 1.0,
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