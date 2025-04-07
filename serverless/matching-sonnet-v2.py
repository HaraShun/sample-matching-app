import boto3
import json
import psycopg2
import numpy as np
from sklearn.cluster import KMeans
import ast
import os

def lambda_handler(event, context):
    # Bedrockクライアントの設定
    bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-northeast-1')
    
    # S3 クライアントの設定
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    
    # ------------------------------------------------------------------
    
    # Secrets Managerからデータベース接続情報を取得する関数
    def get_database_secret():
        secret_name = "BedrockUserSecret-jjRJjSUUmI5w" # Secrets Managerに保存したシークレット名
        region_name = "ap-northeast-1" # シークレットが保存されているリージョン
        
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
    
    # ------------------------------------------------------------------
    
    # ユーザーデータの取得
    cur = conn.cursor()
    cur.execute("SELECT id, embedding, chunks FROM bedrock_integration.bedrock_knowledge_base")
    users = cur.fetchall()
    
    # embeddings配列の作成
    embeddings = np.array([ast.literal_eval(user[1]) for user in users])
    
    # K-meansクラスタリングの実行
    n_clusters = 3 # クラスター数は適宜調整してください
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(embeddings)
    
    # クラスターごとのユーザー特性の分析
    all_results = []  # すべてのクラスター結果を保存するリスト
    
    for cluster in range(n_clusters):
        cluster_users = [users[i] for i in range(len(users)) if cluster_labels[i] == cluster]
        cluster_chunks = " ".join([user[2] for user in cluster_users])
        
        # プロンプトを変数として定義
        prompt_template = f"""
        H: あなたはデータ分析の専門家です。
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
                "maxTokens": 8192
            }
        )
        
        # レスポンスから回答を取得
        summary = response['output']['message']['content'][0]['text']
        print(f"Cluster {cluster} 特性:")
        print(summary.strip())
        print("---")
        
        # 結果をリストに追加
        all_results.append(f"## Cluster {cluster} 特性:\n{summary.strip()}\n\n---\n\n")
    
    # すべての結果を1つのファイルにまとめる
    combined_results = "# クラスター分析結果\n\n" + "".join(all_results)
    
    # 1つのファイルに保存
    with open("/tmp/combined_grouping_results.txt", "w") as f:
        f.write(combined_results)
    
    # S3 バケットに1つのファイルとしてアップロード
    s3.upload_file("/tmp/combined_grouping_results.txt", 'hara-datasource', "combined_grouping_results.txt")
    
    # データベース接続のクローズ
    cur.close()
    conn.close()
