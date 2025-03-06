import json
import random
from typing import List, Dict

def generate_employee_data(count: int = 340) -> List[Dict]:
    """
    ランダムな従業員データを生成する関数。

    Args:
        count (int): 生成する従業員データの数。デフォルトは340。

    Returns:
        List[Dict]: 従業員データのリスト。
    """

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
        "ダンス", "カラオケ", "ガーデニング", "ペットと遊ぶ", "鉄道旅行",
        "天体観測", "ボランティア活動", "マジック", "ドローン撮影", "外国語学習",
        "華道", "茶道", "テニス", "フットサル", "スポーツ", "ショッピング",
        "料理研究", "旅行", "美術館巡り", "博物館巡り", "ライブ参戦", "家庭菜園",
        "ハイキング", "資格取得", "パーティー", "友人と会う", "家族と過ごす", "寝て過ごす",
        "動画配信サービス視聴", "掃除", "整理整頓"
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
        "陽", "光", "優", "純", "薫", "凜", "翼", "千尋", "涼", "悠", "透", 
        "真", "直", "和", "響", "泉", "海", "空", "明", "望", "望月", "樹",
        "陽向", "怜", "翠", "慶", "輝", "智", "晶", "怜奈", "悠人", "悠希",
        "慧", "実", "尚", "春", "悠真", "葵", "律", "馨", "楓", "円", "玲",
        "祥", "綾", "朝陽", "海月", "悠生", "瑞希", "優衣", "奏", "詩", "颯",
        "静", "千歳", "朔", "飛鳥", "渚", "彬", "遥", "青", "雅", "玲央", 
        "朋", "夏希", "洸", "翔", "大地", "怜央", "奏多", "慧悟", "礼央",
        "陽翔", "柚", "優月", "望美", "綾人", "京", "仁", "悠人", "聖", "礼"
    ]

    nearest_stations = [
        "門前仲町駅"
    ]

    # nearest_stations = [
    #     "門前仲町駅", "清澄白河駅", "東京駅", "大手町駅", "日本橋駅", "三越前駅",
    #     "淀屋橋駅", "北浜駅", "西九条駅", "名古屋駅"
    # ]

    favorite_foods = [
        "ラーメン", "寿司", "ハンバーガー", "ピザ", "カレーライス",
        "天ぷら", "うどん", "そば", "お好み焼き", "たこ焼き",
        "餃子", "チャーハン", "麻婆豆腐", "ビビンバ", "キムチ",
        "トムヤムクン", "グリーンカレー", "フォー", "ナンとカレー", "タコス",
        "ステーキ", "ホットドッグ", "パスタ", "リゾット", "シュラスコ",
        "ロコモコ", "刺身", "すき焼き", "しゃぶしゃぶ", "アイスクリーム",
        "クラフトビール", "日本酒", "赤ワイン", "ラム酒", "ウィスキー",
        "カクテル", "緑茶", "炭酸飲料", "紅茶", "白ワイン",
        "和食", "中華", "イタリアン", "フレンチ", "スペイン料理", "メキシコ料理",
        "インド料理", "タイ料理", "ベトナム料理", "韓国料理", "地中海料理",
        "アメリカン", "ロシア料理", "トルコ料理", "ギリシャ料理", "モロッコ料理",
        "ブラジル料理", "ペルー料理", "エチオピア料理", "レバノン料理",
        "インドネシア料理", "マレーシア料理", "シンガポール料理", "ネパール料理",
        "スイス料理", "ドイツ料理", "イギリス料理", "北欧料理", "カリブ料理",
        "アフリカ料理"
    ]

    what_defines_you = [
        "好奇心旺盛", "几帳面", "社交的", "分析力が高い", "創造的",
        "忍耐強い", "リーダーシップがある", "聞き上手", "感受性が豊か", "論理的",
        "ユーモアがある", "冒険好き", "責任感が強い", "協調性がある", "計画的",
        "独立心が強い", "楽観的", "慎重派", "情熱的", "柔軟性がある",
        "音楽好き", "スポーツ好き", "読書好き", "旅行好き", "料理好き",
        "動物好き", "ゲーム好き", "映画好き", "自然が好き", "アートに興味がある"
    ]

    gender = [
        "男性", "女性"
    ]

    year = [
        "20代", "30代", "40代", "50代", "60代", "70代"
    ]

    # 従業員データ生成
    employees = []
    used_names = set()  # 重複チェック用
    employee_id_counter = 1001  # IDカウンターの初期値を1000に設定

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
            "employee_id": employee_id_counter,  # IDの付与
            "名前": full_name,
            "性別": random.choice(gender),
            "年代": random.choice(year),
            "部署": random.choice(departments),
            "出身地": random.choice(prefectures),
            "学生時代の部活": random.choice(clubs),
            "趣味": random.choice(hobbies),
            "大学の学部": random.choice(faculties),
            "最寄り駅": random.choice(nearest_stations),
            "好きな食べ物、飲み物、料理ジャンル": random.choice(favorite_foods),
            "あなたに関するキーワード": random.choice(what_defines_you)
        }

        employees.append(employee)
        employee_id_counter += 1  # IDカウンターをインクリメント

    return employees

# データ生成
employees_data = generate_employee_data(340)

# JSONファイルに出力
output_file = "340-sample-employee-data.json"  # 出力ファイル名を指定
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(employees_data, f, ensure_ascii=False, indent=4)

print(f"JSONデータが '{output_file}' に出力されました。")
