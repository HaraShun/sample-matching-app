# Dockerを使用してLambdaレイヤーを作成（最も確実な方法）

# 1. 作業ディレクトリの作成
mkdir -p ~/lambda-layers/requests-layer
cd ~/lambda-layers/requests-layer

# 2. Dockerfileの作成
cat > Dockerfile << 'EOF'
FROM public.ecr.aws/lambda/python:3.13

# 作業ディレクトリを作成
WORKDIR /opt

# pythonディレクトリを作成
RUN mkdir python

# requestsをインストール
RUN pip install requests -t python/

# 不要ファイルを削除
RUN find python/ -type d -name "__pycache__" -exec rm -rf {} + || true
RUN find python/ -name "*.pyc" -delete || true
RUN find python/ -name "*.pyo" -delete || true

# ZIPファイルを作成
RUN cd /opt && zip -r requests-layer.zip python/

CMD ["echo", "Layer created successfully"]
EOF

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
