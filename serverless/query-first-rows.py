import psycopg2
import os

# 接続
conn = None
try:

    # データベース接続
    conn = psycopg2.connect(
        dbname=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT', '5432')  # デフォルト値を設定
    )

    cur = conn.cursor()

    # クエリを実行
    cur.execute("SELECT chunks FROM bedrock_integration.bedrock_knowledge_base LIMIT 1")

    # 結果を取得
    rows = cur.fetchall()

    # 結果を表示
    for row in rows:
        print(row)

except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    # 接続を閉じる
    if conn is not None:
        cur.close()
        conn.close()
