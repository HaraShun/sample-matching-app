import json
import random
import boto3
import os
import logging
import re
from botocore.exceptions import ClientError
from botocore.config import Config

# Lambdaクライアントの設定
LAMBDA_CLIENT = boto3.client('lambda')
CHECK_HOLIDAY_LAMBDA_NAME = os.environ.get("CHECK_HOLIDAY_LAMBDA_NAME")

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # S3クライアントの設定
    s3 = boto3.client('s3')

    # クライアントの読み取りタイムアウト値を増やす
    config = Config(read_timeout=1000)

    # Bedrockクライアントの設定
    bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-northeast-1', config=config)

    # S3バケットとオブジェクト情報の取得
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    input_bucket_name = os.environ.get('INPUT_S3_BUCKET_NAME')
    file_key = os.environ.get('S3_FILE_KEY')
    output_key = os.environ.get('S3_OUTPUT_KEY')
    summary_output_key = os.environ.get('S3_SUMMARY_OUTPUT_KEY')

    if is_today_holiday():
        logger.info("今日は祝日です。処理をスキップします。")
        empty_result = {
            "message": "今日は祝日なので処理をスキップしました",
            "groups": [],
            "total_groups": 0,
            "total_members": 0
        }
        
        # 空の結果をS3にJSONでアップロード
        s3.put_object(
            Bucket=bucket_name,
            Key=output_key,
            Body=json.dumps(empty_result, ensure_ascii=False, indent=2),
            ContentType='application/json'
        )
        
        s3.put_object(
            Bucket=bucket_name,
            Key=summary_output_key,
            Body=json.dumps(empty_result, ensure_ascii=False, indent=2),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': '今日は祝日なので処理をスキップしました'})
        }
        
    try:
        # S3からJSONLデータを取得
        response = s3.get_object(Bucket=input_bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')

        # JSONLデータを解析（各行が独立したJSONオブジェクト）
        employees = []
        for line in file_content.strip().split('\n'):
            if line.strip():
                try:
                    employee = json.loads(line)
                    employees.append(employee)
                except json.JSONDecodeError:
                    continue

        # データが空の場合は空の結果ファイルを生成
        if not employees:
            empty_result = {
                "message": "社員データが存在しないため、グルーピングは実行されませんでした",
                "groups": [],
                "total_groups": 0,
                "total_members": 0
            }
            
            # 空の結果をS3にJSONでアップロード
            s3.put_object(
                Bucket=bucket_name,
                Key=output_key,
                Body=json.dumps(empty_result, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )
            
            s3.put_object(
                Bucket=bucket_name,
                Key=summary_output_key,
                Body=json.dumps(empty_result, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No employee data found, empty result files created',
                    'output_location': f's3://{bucket_name}/{output_key}',
                    'summary_location': f's3://{bucket_name}/{summary_output_key}',
                    'group_count': 0
                })
            }

        # データをランダムにシャッフル
        random.shuffle(employees)

        # データを複数のチャンクに分割（Claudeの入力制限を考慮）
        chunk_size = min(100, len(employees))
        chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]

        # 各チャンクをClaudeに送信してグルーピング
        all_groups = {}
        chunk_results = []

        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} with {len(chunk)} employees")

            # Claudeへのプロンプト作成
            prompt = create_prompt(chunk)

            # Claudeに送信
            response = bedrock.converse(
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
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
            result = response['output']['message']['content'][0]['text']

            # チャンク結果を保存
            chunk_results.append({
                "chunk_id": i + 1,
                "employees_count": len(chunk),
                "claude_response": result
            })

            # グループ情報を解析して統合
            chunk_groups = parse_groups_from_json(result)
            all_groups = merge_groups(all_groups, chunk_groups)

        # 最終結果をJSON形式で構成
        final_result = {
            "processing_info": {
                "total_employees": len(employees),
                "chunks_processed": len(chunks),
                "processing_date": None  # 必要に応じて日付を追加
            },
            "chunk_details": chunk_results,
            "groups": format_groups_for_output(all_groups),
            "summary": {
                "total_groups": len(all_groups),
                "total_members_grouped": sum(len(group['members']) for group in all_groups.values())
            }
        }

        # サマリー用のデータ（グループ情報のみ）
        summary_result = {
            "groups": format_groups_for_output(all_groups),
            "summary": {
                "total_groups": len(all_groups),
                "total_members_grouped": sum(len(group['members']) for group in all_groups.values())
            }
        }

        # 結果をS3にJSONファイルとしてアップロード（全体ファイル）
        s3.put_object(
            Bucket=bucket_name,
            Key=output_key,
            Body=json.dumps(final_result, ensure_ascii=False, indent=2),
            ContentType='application/json'
        )

        # サマリーファイルをアップロード
        s3.put_object(
            Bucket=bucket_name,
            Key=summary_output_key,
            Body=json.dumps(summary_result, ensure_ascii=False, indent=2),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Employee grouping completed successfully',
                'output_location': f's3://{bucket_name}/{output_key}',
                'summary_location': f's3://{bucket_name}/{summary_output_key}',
                'group_count': len(all_groups)
            })
        }

    except ClientError as e:
        print(f"Error: {e}")
        # エラーが発生した場合も空の結果ファイルを生成
        try:
            error_result = {
                "error": f"データ処理中にエラーが発生しました: {str(e)}",
                "groups": [],
                "total_groups": 0,
                "total_members": 0
            }
            
            # エラー結果をS3にJSONでアップロード
            s3.put_object(
                Bucket=bucket_name,
                Key=output_key,
                Body=json.dumps(error_result, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )
            
            s3.put_object(
                Bucket=bucket_name,
                Key=summary_output_key,
                Body=json.dumps(error_result, ensure_ascii=False, indent=2),
                ContentType='application/json'
            )
        except Exception as upload_error:
            print(f"Error uploading empty result files: {upload_error}")
            
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing the request: {str(e)}')
        }

def create_prompt(employees):
    """Claudeへのプロンプトを作成する関数"""
    employees_json = json.dumps(employees, ensure_ascii=False)

    prompt = f"""
あなたはデータ分析の専門家です。
全社員のデータを閲覧しグループ分けできる権限を持っています。
社員全員を最寄り駅でグループ分けし、さらに下記ルールでグループ分けしてください。
出力形式は以下の例に厳密に従ってください。句読点や括弧の形式も正確に守ってください。

**重要**: 回答は必ずJSON形式で出力してください。

出力形式:
```json
[
  {{
    "グループ名": "「アウトドア愛好家グループ」",
    "理由": "メンバー全員がアウトドア活動を趣味としているため",
    "メンバーID": ["12345678-abcd-efgh-ijkl-abc123456789", "22345678-abcd-efgh-ijkl-abc123456789"]
  }},
  {{
    "グループ名": "「甘党集合グループ」",
    "理由": "メンバー全員がスイーツを好んでいるため",
    "メンバーID": ["32345678-abcd-efgh-ijkl-abc123456789", "42345678-abcd-efgh-ijkl-abc123456789"]
  }},
  {{
    "グループ名": "「読書クラブグループ」",
    "理由": "読書が共通の趣味であるため",
    "メンバーID": ["52345678-abcd-efgh-ijkl-abc123456789", "62345678-abcd-efgh-ijkl-abc123456789"]
  }}
]
```

グループ分けのルール：
・「趣味」でグルーピングする。
・各グループの人数は8人以上100人以下とする。
・1人1つだけのグループに所属する。
・グループ名は直感的にわかりやすくする。

出力形式：
・各グループのグループ名を表示する。
・グループ名には必ず「」をつける。
・グループ名は通販番組の商品紹介のように興味をひくものにする。
・出力するグループ名は必ず最後に「グループ」をつける。
・各グループのメンバー全員のIDをリスト形式で表示する。
・グルーピング理由を説明する１文を追加する。
・回答は必ずJSON配列形式で出力する。

社員データ:
{employees_json}
"""
    return prompt

def parse_groups_from_json(result):
    """ClaudeのJSON回答からグループ情報を抽出する関数"""
    groups = {}
    
    try:
        # JSON部分を抽出（```json と ``` の間）
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # バックティックがない場合、JSON配列らしき部分を探す
            json_match = re.search(r'\[.*?\]', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # 最後の手段として全体をJSONとして解析を試みる
                json_str = result.strip()
        
        # JSONを解析
        group_list = json.loads(json_str)
        
        # リスト形式の場合
        if isinstance(group_list, list):
            for group in group_list:
                if isinstance(group, dict) and 'グループ名' in group:
                    group_name = group['グループ名']
                    groups[group_name] = {
                        'members': group.get('メンバーID', []),
                        'reason': group.get('理由', '')
                    }
        # オブジェクト形式の場合
        elif isinstance(group_list, dict):
            for key, value in group_list.items():
                if isinstance(value, dict) and 'メンバーID' in value:
                    groups[key] = {
                        'members': value.get('メンバーID', []),
                        'reason': value.get('理由', '')
                    }
                    
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw result: {result}")
        # JSONの解析に失敗した場合、テキスト解析にフォールバック
        groups = parse_groups_from_text_fallback(result)
    except Exception as e:
        print(f"Unexpected error in JSON parsing: {e}")
        groups = parse_groups_from_text_fallback(result)
    
    return groups

def parse_groups_from_text_fallback(result):
    """JSON解析に失敗した場合のテキスト解析フォールバック"""
    groups = {}
    current_group = None

    for line in result.strip().split('\n'):
        line = line.strip()
        
        # グループ名を検出
        if "グループ" in line and ":" not in line and "メンバー" not in line:
            current_group = line.strip()
            if current_group not in groups:
                groups[current_group] = {"members": [], "reason": ""}

        # メンバーIDを検出
        elif current_group and "メンバーID:" in line:
            try:
                member_ids_str = line.split("メンバーID:")[1].strip()
                if member_ids_str.startswith('[') and member_ids_str.endswith(']'):
                    member_ids = json.loads(member_ids_str.replace("'", "\""))
                else:
                    member_ids = [id.strip() for id in member_ids_str.split(',')]
                groups[current_group]["members"].extend(member_ids)
            except Exception as e:
                print(f"Error parsing member IDs in fallback: {e}")
                continue

        # マッチング理由を検出
        elif current_group and ("理由" in line or "これらのメンバーは" in line):
            groups[current_group]["reason"] = line.strip()

    return groups

def merge_groups(all_groups, new_groups):
    """複数のチャンクから得られたグループ情報を統合する関数"""
    for group_name, group_info in new_groups.items():
        if group_name in all_groups:
            # 既存のグループにメンバーを追加
            all_groups[group_name]["members"].extend(group_info["members"])
            # 理由が空の場合は新しい理由を使用
            if not all_groups[group_name]["reason"] and group_info["reason"]:
                all_groups[group_name]["reason"] = group_info["reason"]
        else:
            # 新しいグループを追加
            all_groups[group_name] = group_info

    return all_groups

def format_groups_for_output(all_groups):
    """グループ情報を出力用の形式に整形する関数"""
    formatted_groups = []
    
    for group_name, group_info in all_groups.items():
        formatted_group = {
            "group_name": group_name,
            "reason": group_info["reason"],
            "member_count": len(group_info["members"]),
            "member_ids": group_info["members"]
        }
        formatted_groups.append(formatted_group)
    
    # メンバー数の多い順にソート
    formatted_groups.sort(key=lambda x: x["member_count"], reverse=True)
    
    return formatted_groups

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
