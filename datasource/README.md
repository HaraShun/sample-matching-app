# 説明

S3 バケットを AWS CLI で作成し、100名分のテストデータ（JSON）をアップロード。

Knowledge Base の `データソース` とする。

100名分のテストデータは ChatGPT に生成してもらいました。


## Pythonコード実行
```
$ python generate-sample-employee-data.py
```

## JSON Line 化
```
$ jq -c '.[]' 340-sample-employee-data.json > flat-340-sample-employee-data.jsonl
```

## S3 アップロード

```
$ aws s3api create-bucket --bucket {my-datasource-bucket} --region ap-northeast-1 --create-bucket-configuration LocationConstraint=ap-northeast-1
```

```
$ aws s3 cp test-user-data.json.json s3://{my-datasource-bucket}/
```