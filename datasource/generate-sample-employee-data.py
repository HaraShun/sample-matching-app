import json
import random
from typing import List, Dict

def generate_employee_data(count: int = 2000) -> List[Dict]:
    # 基本データセット
    departments = [
        "人事部", "財務部", "マーケティング部", "営業部", "開発部", "品質管理部",
        "カスタマーサポート部", "広報部", "法務部", "経営企画部", "調達部",
        "研究開発部", "海外事業部", "情報システム部", "総務部", "商品企画部"
    ]

    prefectures = [
        "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
        "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
        "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
        "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
        "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
        "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
        "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
    ]

    clubs = [
        "サッカー部", "野球部", "バスケットボール部", "バレーボール部", "テニス部",
        "陸上部", "水泳部", "剣道部", "柔道部", "弓道部", "吹奏楽部", "茶道部",
        "書道部", "美術部", "写真部", "演劇部", "放送部", "新聞部", "科学部",
        "天文部", "囲碁・将棋部", "料理部", "ダンス部", "合唱部", "軽音楽部",
        "応援団", "空手部", "ハンドボール部", "卓球部", "バドミントン部"
    ]

    hobbies = [
        "読書", "映画鑑賞", "音楽鑑賞", "ゲーム", "料理", "バイク", "写真撮影",
        "絵画", "書道", "園芸", "釣り", "登山", "キャンプ", "サイクリング",
        "ドライブ", "カフェ巡り", "温泉巡り", "スポーツ観戦", "アニメ鑑賞",
        "プログラミング", "DIY", "ヨガ", "筋トレ", "ランニング", "水泳",
        "ボードゲーム", "パズル", "コレクション", "手芸", "楽器演奏",
        "ダンス", "カラオケ", "ガーデニング", "ペット", "鉄道旅行",
        "天体観測", "ボランティア", "マジック", "ドローン撮影", "外国語学習"
    ]

    movies = [
        "スター・ウォーズシリーズ", "マーベル映画", "ハリー・ポッターシリーズ",
        "ロード・オブ・ザ・リングシリーズ", "ジブリ映画", "タイタニック",
        "インセプション", "ショーシャンクの空に", "フォレスト・ガンプ",
        "ゴッドファーザー", "マトリックス", "ジュラシック・パークシリーズ",
        "バック・トゥ・ザ・フューチャー", "パイレーツ・オブ・カリビアン",
        "トップガン", "アバター", "インターステラー", "グラディエーター",
        "ラ・ラ・ランド", "シン・エヴァンゲリオン", "君の名は。", "千と千尋の神隠し",
        "ボヘミアン・ラプソディ", "アナと雪の女王", "ターミネーター",
        "ブレードランナー", "コマンドー", "プレデター", "エイリアン",
        "ゲーム・オブ・スローンズ", "ブレイキング・バッド", "ストレンジャー・シングス",
        "ウエストワールド", "ウォーキング・デッド", "シャーロック",
        "フレンズ", "THE LAST OF US", "韓流ドラマ", "台湾ドラマ", "中国ドラマ"
    ]

    cuisines = [
        "和食", "中華", "イタリアン", "フレンチ", "スペイン料理", "メキシコ料理",
        "インド料理", "タイ料理", "ベトナム料理", "韓国料理", "地中海料理",
        "アメリカン", "ロシア料理", "トルコ料理", "ギリシャ料理", "モロッコ料理",
        "ブラジル料理", "ペルー料理", "エチオピア料理", "レバノン料理",
        "インドネシア料理", "マレーシア料理", "シンガポール料理", "ネパール料理",
        "スイス料理", "ドイツ料理", "イギリス料理", "北欧料理", "カリブ料理",
        "アフリカ料理"
    ]

    weekend_activities = [
        "映画鑑賞", "読書", "スポーツ", "ショッピング", "料理研究", "温泉",
        "旅行", "ドライブ", "カフェ巡り", "美術館巡り", "博物館巡り",
        "ライブ参戦", "スポーツ観戦", "DIY", "家庭菜園", "ペットと遊ぶ",
        "プログラミング", "ゲーム", "楽器演奏", "ヨガ", "筋トレ",
        "ランニング", "サイクリング", "ハイキング", "写真撮影", "絵画",
        "習い事", "ボランティア活動", "勉強", "資格取得", "釣り",
        "キャンプ", "パーティー", "友人と会う", "家族と過ごす", "寝て過ごす",
        "動画配信サービス視聴", "音楽鑑賞", "掃除", "整理整頓"
    ]

    faculties = [
        "法学部", "経済学部", "経営学部", "商学部", "文学部", "教育学部",
        "理学部", "工学部", "医学部", "歯学部", "薬学部", "看護学部",
        "農学部", "獣医学部", "水産学部", "情報学部", "芸術学部", "音楽学部",
        "体育学部", "生命科学部", "環境学部", "国際関係学部", "社会学部",
        "心理学部", "デザイン学部", "建築学部", "観光学部", "栄養学部"
    ]

    family_names = [
        "佐藤", "鈴木", "高橋", "田中", "渡辺", "伊藤", "山本", "中村", "小林",
        "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林",
        "斎藤", "清水", "山崎", "阿部", "森", "池田", "橋本", "山下", "石川",
        "中島", "前田", "藤田", "後藤", "小川", "岡田", "村上", "長谷川", "近藤",
        "石井", "斉藤", "坂本", "遠藤", "藤井", "青木", "福田", "三浦", "西村",
        "藤原", "太田", "松田", "原田", "岡本", "中野", "中川", "小野", "田村",
        "竹内", "金子", "和田", "中山", "石田", "上田", "森田", "小島", "柴田",
        "原", "宮崎", "酒井", "工藤", "横山", "武田", "増田", "小山", "野口",
        "大野", "松井", "菅原", "佐野", "杉山", "千葉", "野村", "渡部", "菊地",
        "岩崎", "久保", "木下", "佐川", "野田", "松尾", "菊池", "上原", "中原",
        "細川", "大谷", "中谷", "小谷", "大川", "大田", "田原", "村田"
    ]

    first_names = [
        "翔太", "大輔", "健一", "直人", "達也", "亮", "学", "誠", "拓海",
        "裕子", "美咲", "真理", "明日香", "彩", "美穂", "麻衣", "愛", "舞",
        "陽子", "智子", "真由美", "恵美", "由美子", "京子", "幸子", "和子",
        "優子", "明美", "友美", "香織", "直美", "順子", "典子", "早苗",
        "久美子", "裕美", "真紀", "恵子", "美加子", "純子", "智美", "薫",
        "陽一", "和也", "洋平", "拓也", "健太", "翔", "大地", "海斗", "蓮",
        "優花", "萌", "さくら", "美咲", "陽菜", "優奈", "彩乃", "遥", "美月",
        "結衣", "茜", "俊太郎", "駿太郎", "圭介", "智樹", "理沙", "沙織",
        "凜", "由人", "宏明", "賢治", "由仁", "芽衣", "祐介",
        "Wei", "颯汰", "克明", "麻莉亜", "次郎", "美郷", "文麿", "令"
    ]

    # 従業員データ生成
    employees = []
    used_names = set()  # 重複チェック用
    while len(employees) < count:
        # 名前生成（重複チェック）
        while True:
            family = random.choice(family_names)
            first = random.choice(first_names)
            full_name = f"{family} {first}"
            if full_name not in used_names:
                used_names.add(full_name)
                break
        employee = {
            "名前": full_name,
            "部署": random.choice(departments),
            "出身地": random.choice(prefectures),
            "学生時代の部活": random.choice(clubs),
            "趣味": random.choice(hobbies),
            "好きな映画・ドラマ": random.choice(movies),
            "好きな料理ジャンル": random.choice(cuisines),
            "休日の過ごし方": random.choice(weekend_activities),
            "大学の学部": random.choice(faculties)
        }
        employees.append(employee)
    return employees

# データ生成
employees_data = generate_employee_data(2000)

# JSONファイルに出力
output_file = "2000-sample-employee-data.json"  # 出力ファイル名を指定
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(employees_data, f, ensure_ascii=False, indent=4)

print(f"JSONデータが '{output_file}' に出力されました。")
