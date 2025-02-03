# 説明

S3 バケットを AWS CLI で作成し、100名分のテストデータ（JSON）をアップロード。

Knowledge Base の `データソース` とする。

100名分のテストデータは ChatGPT に生成してもらいました。

## デプロイ

```
$ aws s3api create-bucket --bucket {my-datasource-bucket} --region ap-northeast-1 --create-bucket-configuration LocationConstraint=ap-northeast-1
```

```
$ aws s3 cp test-user-data.json.json s3://{my-datasource-bucket}/
```