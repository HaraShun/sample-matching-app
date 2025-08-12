# Dockerを使用してLambdaレイヤーを作成（最も確実な方法）

```
FROM amazonlinux:2

# 必要なパッケージをインストール
RUN yum update -y && \
    yum install -y python3 python3-pip zip && \
    yum clean all

# 作業ディレクトリを作成
WORKDIR /opt

# pythonディレクトリを作成
RUN mkdir python

# requestsをインストール
RUN pip3 install requests -t python/

# 不要ファイルを削除
RUN find python/ -type d -name "__pycache__" -exec rm -rf {} + || true && \
    find python/ -name "*.pyc" -delete || true && \
    find python/ -name "*.pyo" -delete || true

# ZIPファイルを作成
RUN zip -r requests-layer.zip python/

CMD ["echo", "Layer created successfully"]
```


# 3. Dockerイメージをビルド
docker build -t lambda-layer-builder .

# 4. コンテナを実行してZIPファイルを取得
docker run --name layer-container lambda-layer-builder
docker cp layer-container:/opt/requests-layer.zip ./

# 5. コンテナを削除
docker rm layer-container

# 6. AWS CLIでレイヤーを作成
aws lambda publish-layer-version \
    --layer-name requests-layer \
    --description "Requests library for Python 3.13 (Docker built)" \
    --zip-file fileb://requests-layer.zip \
    --compatible-runtimes python3.13 \
    --compatible-architectures x86_64

---
```
# Lambda関数にレイヤーをアタッチ
aws lambda update-function-configuration \
    --function-name your-function-name \
    --layers arn:aws:lambda:ap-northeast-1:123456789012:layer:requests-layer:1
```
