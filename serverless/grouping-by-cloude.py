import json
import random
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # S3クライアントとBedrockクライアントの設定
    s3 = boto3.client('s3')
    bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-northeast-1')
    
    # S3バケットとオブジェクト情報の取得（環境変数または直接指定）
    bucket_name = os.environ.get('S3_BUCKET_NAME', 'hara-datasource')
    file_key = os.environ.get('S3_FILE_KEY', 'flat-340-sample-employee-data.jsonl')
    output_key = os.environ.get('S3_OUTPUT_KEY', 'employee_grouping_results.json')
    
    try:
        # S3からJSONLデータを取得
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
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
        
        # データが空の場合はエラーを返す
        if not employees:
            return {
                'statusCode': 400,
                'body': json.dumps('No valid employee data found in the file')
            }
        
        # データをランダムにシャッフル
        random.shuffle(employees)
        
        # データを複数のチャンクに分割（Claudeの入力制限を考慮）
        chunk_size = min(100, len(employees) // 5)  # 最大5チャンクに分割
        chunks = [employees[i:i + chunk_size] for i in range(0, len(employees), chunk_size)]
        
        # 各チャンクをClaudeに送信してグルーピング
        all_groups = {}
        
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
            
            # グループ情報を解析して統合
            chunk_groups = parse_groups(result)
            all_groups = merge_groups(all_groups, chunk_groups)
        
        # 最終的なグループ情報をJSON形式で保存
        s3.put_object(
            Bucket=bucket_name,
            Key=output_key,
            Body=json.dumps(all_groups, ensure_ascii=False, indent=2),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Employee grouping completed successfully',
                'output_location': f's3://{bucket_name}/{output_key}',
                'group_count': len(all_groups)
            })
        }
        
    except ClientError as e:
        print(f"Error: {e}")
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
以下の社員データを趣味でグループ分けしてください。

グループ分けのルール：
・「趣味」でグルーピングする。
・各グループの人数は適切な数とする。
・1人1つのグループに所属する。
・グループ名は直感的にわかりやすくする。

出力形式：
・各グループのグループ名を表示する。
・出力するグループ名は必ず最後に「グループ」をつける。
・各グループのメンバー全員のIDをリスト形式で表示する。
・各グループは、"メンバーID: []" の形式で出力する。
・マッチング理由を説明する１文を追加する。

社員データ:
{employees_json}
"""
    return prompt

def parse_groups(result):
    """Claudeの回答からグループ情報を抽出する関数"""
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
                # リスト形式のIDを抽出して解析
                member_ids_str = line.split("メンバーID:")[1].strip()
                # 文字列をリストに変換（様々な形式に対応）
                if member_ids_str.startswith('[') and member_ids_str.endswith(']'):
                    # JSON形式のリスト
                    member_ids = json.loads(member_ids_str.replace("'", "\""))
                else:
                    # カンマ区切りの値
                    member_ids = [id.strip() for id in member_ids_str.split(',')]
                
                groups[current_group]["members"].extend(member_ids)
            except Exception as e:
                print(f"Error parsing member IDs: {e}")
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
