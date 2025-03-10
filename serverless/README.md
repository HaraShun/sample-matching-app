```
export DB_NAME='your_database_name'
export DB_USER='your_database_user'
export DB_PASSWORD='your_database_password'
export DB_HOST='your_database_host'
export DB_PORT='5432'
```

```
aws bedrock list-foundation-models --output table \
--query 'modelSummaries[*].[modelId,modelName,providerName]' \
--region ap-northeast-1
```