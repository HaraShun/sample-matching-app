import boto3
import json
import random
import re
import logging
import os

# S3 クライアントの設定
s3 = boto3.client('s3', region_name='ap-northeast-1')

# UUIDのパターン（8-4-4-4-12の16進数）
uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

# Lambda クライアントの設定
LAMBDA_CLIENT = boto3.client('lambda')
CHECK_HOLIDAY_LAMBDA_NAME = os.environ.get("CHECK_HOLIDAY_LAMBDA_NAME")

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# S3 からJSONファイルを読み込む
def read_json_file(bucket_name, file_name):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error reading JSON file: {e}")
        return None

# メンバー ID を再分類してグループを再編成
def regroup_json_data(input_data):
    if not input_data or "groups" not in input_data:
        logger.warning("Invalid input data structure")
        return []
    
    groups_data = {}
    discarded_members = []
    
    # 入力データからグループ情報を抽出
    for group in input_data.get("groups", []):
        group_name = group.get("group_name", "")
        reason = group.get("reason", "")
        member_ids = group.get("member_ids", [])
        
        # UUIDパターンに一致するIDのみをフィルタリング
        valid_ids = []
        for member_id in member_ids:
            if member_id and isinstance(member_id, str):
                clean_id = member_id.strip()
                if uuid_pattern.match(clean_id):
                    valid_ids.append(clean_id)
                else:
                    logger.warning(f"Invalid UUID format: {member_id}")
        
        if valid_ids:
            groups_data[group_name] = {
                "reason": reason,
                "ids": valid_ids
            }
    
    # 結果のJSONデータ構造
    json_data = []
    
    # グループの再編成
    for group_name, group_data in groups_data.items():
        ids = group_data["ids"]
        reason = group_data["reason"]
        
        random.shuffle(ids)  # メンバー ID をシャッフル
        
        if len(ids) <= 7:  # 7人以下は切り捨てられたメンバーとして追加
            discarded_members.extend(ids)
            logger.info(f"Group '{group_name}' with {len(ids)} members moved to discarded list")
        elif len(ids) <= 10:  # 8人以上10人以下はそのまま
            json_data.append({
                "theme": group_name,
                "reason": reason,
                "group_list": [{"id_list": ids}]
            })
            logger.info(f"Group '{group_name}' kept as single group with {len(ids)} members")
        else:  # 11人以上は10人ずつのグループに分ける
            secondary_groups = []
            for i in range(0, len(ids), 10):
                secondary_group = ids[i:i+10]
                # グループサイズをチェック
                if len(secondary_group) <= 7 and i + 10 >= len(ids):
                    # 最後のグループが7人以下なら切り捨てる
                    discarded_members.extend(secondary_group)
                    logger.info(f"Last subgroup of '{group_name}' with {len(secondary_group)} members moved to discarded list")
                else:
                    secondary_groups.append({"id_list": secondary_group})
            
            if secondary_groups:  # 空でない場合のみ追加
                json_data.append({
                    "theme": group_name,
                    "reason": reason,
                    "group_list": secondary_groups
                })
                logger.info(f"Group '{group_name}' split into {len(secondary_groups)} subgroups")
    
    # 切り捨てられたメンバー一覧を追加
    if discarded_members:
        # 切り捨てメンバーも10人ずつのグループに分ける
        discarded_groups = []
        random.shuffle(discarded_members)  # 切り捨てメンバーもシャッフル
        
        for i in range(0, len(discarded_members), 10):
            discarded_group = discarded_members[i:i+10]
            discarded_groups.append({"id_list": discarded_group})
        
        json_data.append({
            "theme": "切り捨てられたメンバー一覧",
            "reason": "7人以下のグループから集められたメンバーです",
            "group_list": discarded_groups
        })
        logger.info(f"Created discarded members group with {len(discarded_members)} total members in {len(discarded_groups)} subgroups")
    
    return json_data

# JSON データを保存し、S3 にアップロード
def save_and_upload_json(json_data, bucket_name, file_name):
    try:
        json_content = json.dumps(json_data, indent=4, ensure_ascii=False)
        s3.put_object(
            Body=json_content, 
            Bucket=bucket_name, 
            Key=file_name,
            ContentType='application/json'
        )
        logger.info(f"JSON data successfully uploaded to s3://{bucket_name}/{file_name}")
        return True
    except Exception as e:
        logger.error(f"Error uploading JSON to S3: {e}")
        return False

# Lambda ハンドラー関数
def lambda_handler(event, context):
    bucket_name = os.environ.get("BUCKET_NAME")
    file_name = os.environ.get("OBJECT_KEY")
    output_file_name = os.environ.get("OUTPUT_OBJECT_KEY")
    
    # 祝日チェック
    if is_today_holiday():
        logger.info("今日は祝日です。処理をスキップします。")
        # 空の結果ファイルを生成
        empty_result = [{
            "theme": "処理スキップ",
            "reason": "今日は祝日なので処理をスキップしました",
            "group_list": []
        }]
        save_and_upload_json(empty_result, bucket_name, output_file_name)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': '今日は祝日なので処理をスキップしました'})
        }
    
    # 必要な環境変数のチェック
    if not all([bucket_name, file_name, output_file_name]):
        logger.error("Required environment variables are missing")
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Required environment variables are missing",
                "required": ["BUCKET_NAME", "OBJECT_KEY", "OUTPUT_OBJECT_KEY"]
            })
        }
    
    try:
        # JSONファイルを読み込み
        input_data = read_json_file(bucket_name, file_name)
        
        if input_data is None:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Failed to read input JSON file"})
            }
        
        # グループ再編成処理
        regrouped_data = regroup_json_data(input_data)
        
        if not regrouped_data:
            logger.warning("No valid groups were created")
            # 空の結果でも正常終了
            empty_result = [{
                "theme": "処理結果なし",
                "reason": "有効なグループが作成されませんでした",
                "group_list": []
            }]
            save_and_upload_json(empty_result, bucket_name, output_file_name)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "No valid groups created, empty result uploaded",
                    "total_groups": 0
                })
            }
        
        # 結果をログ出力（デバッグ用）
        logger.info("Regrouped data structure:")
        logger.info(json.dumps(regrouped_data, indent=2, ensure_ascii=False))
        
        # S3にアップロード
        upload_success = save_and_upload_json(regrouped_data, bucket_name, output_file_name)
        
        if upload_success:
            # 統計情報を計算
            total_groups = len(regrouped_data)
            total_subgroups = sum(len(group.get("group_list", [])) for group in regrouped_data)
            total_members = sum(
                len(subgroup.get("id_list", [])) 
                for group in regrouped_data 
                for subgroup in group.get("group_list", [])
            )
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Data processed successfully",
                    "total_themes": total_groups,
                    "total_subgroups": total_subgroups,
                    "total_members": total_members,
                    "output_location": f"s3://{bucket_name}/{output_file_name}"
                })
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Failed to upload result to S3"})
            }
            
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal server error",
                "error": str(e)
            })
        }

def is_today_holiday():
    """祝日判定Lambdaを呼び出す"""
    try:
        response = LAMBDA_CLIENT.invoke(
            FunctionName=CHECK_HOLIDAY_LAMBDA_NAME,
            InvocationType='RequestResponse',
        )
        payload_str = response['Payload'].read().decode('utf-8')
        logger.info(f"祝日Lambda応答: {payload_str}")
        payload = json.loads(payload_str)

        if response['StatusCode'] != 200:
            logger.info(f"祝日判定Lambdaのステータスコード: {response['StatusCode']}")
            return True  # 念のため、祝日とみなして処理スキップ

        body = json.loads(payload.get("body", "{}"))
        return body.get("is_holiday", True)  # デフォルト True = 安全優先でスキップ

    except Exception as e:
        logger.error(f"祝日判定Lambdaの呼び出しに失敗: {str(e)}", exc_info=True)
        return True  # エラー時は祝日扱いにしてスキップ
