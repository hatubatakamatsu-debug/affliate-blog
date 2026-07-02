"""
アフィリエイトブログ記事自動生成スクリプト
- ジャンル：金融・投資・不動産・住宅ローン・転職・就職・保険
- いろんな立場の視点で記事生成
- Claude API使用
"""

import anthropic
import json
import random
import datetime
import os
from pathlib import Path

# ===== 設定 =====
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ===== ジャンル定義 =====
GENRES = {
    "金融": {
        "keywords": ["クレジットカード おすすめ", "銀行口座 比較", "ネット銀行 メリット", "電子マネー 節約", "ポイント還元率 最強"],
        "affiliate": "クレジットカード・銀行口座開設"
    },
    "投資": {
        "keywords": ["つみたてNISA 始め方", "iDeCo 比較", "投資信託 初心者", "株式投資 少額", "米国株 ETF おすすめ"],
        "affiliate": "証券口座開設"
    },
    "不動産": {
        "keywords": ["マンション購入 注意点", "一戸建て vs マンション", "不動産投資 初心者", "賃貸 vs 購入", "新築 vs 中古"],
        "affiliate": "不動産査定・投資サービス"
    },
    "住宅ローン": {
        "keywords": ["住宅ローン 比較 2024", "変動金利 vs 固定金利", "住宅ローン 審査 通るコツ", "繰り上げ返済 メリット", "住宅ローン 借り換え"],
        "affiliate": "住宅ローン申込み"
    },
    "転職": {
        "keywords": ["転職エージェント おすすめ", "30代 転職 成功", "未経験 転職 方法", "年収アップ 転職", "転職サイト 比較"],
        "affiliate": "転職エージェント登録"
    },
    "就職": {
        "keywords": ["新卒 就活 スケジュール", "就活エージェント おすすめ", "内定 もらいやすい業界", "面接 対策 方法", "自己分析 やり方"],
        "affiliate": "就活支援サービス登録"
    },
    "保険": {
        "keywords": ["生命保険 比較 おすすめ", "医療保険 必要性", "火災保険 選び方", "自動車保険 安い", "保険 見直し 方法"],
        "affiliate": "保険一括比較サービス"
    }
}

# ===== 立場・視点定義（多様な読者層） =====
PERSPECTIVES = [
    {
        "persona": "20代会社員（Aさん）",
        "profile": "26歳・独身・都内在住・年収350万円・社会人3年目",
        "concern": "将来の不安を感じ始めたが何から始めればいいか分からない",
        "tone": "フレンドリーで共感しやすい文体"
    },
    {
        "persona": "30代既婚・子あり（Bさん）",
        "profile": "35歳・配偶者と子供2人・郊外在住・世帯年収700万円",
        "concern": "子供の教育費と老後資金の両立が心配",
        "tone": "具体的な数字と家族目線"
    },
    {
        "persona": "40代管理職（Cさん）",
        "profile": "43歳・部長職・年収900万円・住宅ローン残あり",
        "concern": "老後に向けた資産形成と子供の独立後の生活設計",
        "tone": "論理的・データ重視"
    },
    {
        "persona": "50代・老後を意識（Dさん）",
        "profile": "52歳・子供独立・年収800万円・定年まで10年",
        "concern": "退職後の収入源と資産の取り崩し方",
        "tone": "シニア層に寄り添う落ち着いた文体"
    },
    {
        "persona": "20代女性フリーランス（Eさん）",
        "profile": "24歳・フリーランスWebデザイナー・収入不安定",
        "concern": "会社員と違い社会保障が薄いため自分で備える必要がある",
        "tone": "女性目線・共感重視"
    },
    {
        "persona": "地方在住・中小企業勤務（Fさん）",
        "profile": "38歳・地方都市在住・中小企業勤務・年収450万円",
        "concern": "地方ならではのコストと都市との情報格差を感じている",
        "tone": "地方目線・現実的"
    },
    {
        "persona": "シングルマザー（Gさん）",
        "profile": "32歳・子供1人・パート+副業・年収280万円",
        "concern": "限られた収入で子供と自分の将来を守りたい",
        "tone": "節約・実用重視・励ます文体"
    },
    {
        "persona": "定年退職後（Hさん）",
        "profile": "63歳・年金受給者・退職金あり・夫婦2人暮らし",
        "concern": "退職金の運用と医療費増加への備え",
        "tone": "シニア向け・安心感重視"
    }
]


def select_todays_combination():
    """今日の日付をシードにして、ジャンルと視点を選択"""
    today = datetime.date.today()
    seed = int(today.strftime("%Y%m%d"))
    random.seed(seed)

    genre_name = random.choice(list(GENRES.keys()))
    genre_data = GENRES[genre_name]
    keyword = random.choice(genre_data["keywords"])
    perspective = random.choice(PERSPECTIVES)

    return genre_name, genre_data, keyword, perspective


def generate_article(genre_name, genre_data, keyword, perspective):
    """Claude APIで記事を生成"""

    prompt = f"""
あなたはSEOとアフィリエイトに精通したブログライターです。
以下の条件で、読者に本当に役立つ高品質なブログ記事を書いてください。

## 記事条件
- **ジャンル**: {genre_name}
- **メインキーワード**: {keyword}
- **アフィリエイト商品**: {genre_data["affiliate"]}
- **文字数**: 2500〜3500字

## 読者ペルソナ（この人の視点で書く）
- **人物**: {perspective["persona"]}
- **プロフィール**: {perspective["profile"]}
- **悩み・関心**: {perspective["concern"]}
- **文体**: {perspective["tone"]}

## 記事構成（必須）
1. **タイトル**（クリックされやすいもの・32文字以内）
2. **リード文**（読者の悩みに共感・200字）
3. **H2見出し1**: 基本知識・現状説明
4. **H2見出し2**: {perspective["persona"]}が直面する具体的な課題
5. **H2見出し3**: 解決策・おすすめの方法（ここでアフィリエイト商品を自然に紹介）
6. **H2見出し4**: 実際のステップ・手順
7. **H2見出し5**: よくある質問（Q&A形式・3つ）
8. **まとめ**（行動を促すCTA含む）

## 出力形式
WordPress投稿用のHTML形式で出力してください。
タイトルは<title>タグ、本文は<article>タグで囲んでください。

## 重要な注意事項
- 特定の金融商品を断定的に推奨しない（「〜が向いている人もいます」などの表現）
- 「投資は元本割れのリスクがあります」などのリスク開示を含める
- 保険・金融は「専門家への相談をおすすめします」を明記
- 読者の立場に寄り添い、押し付けがましくない自然なアフィリエイト誘導
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def save_article(article_content, genre_name, keyword, perspective):
    """記事をファイルに保存（人間レビュー用）"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"draft_{today}_{genre_name}.html"

    output_dir = Path("drafts")
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename

    # メタ情報をコメントとして追加
    meta = f"""<!--
=== 記事メタ情報 ===
生成日: {today}
ジャンル: {genre_name}
キーワード: {keyword}
視点: {perspective["persona"]}
アフィリエイト: ここに実際のアフィリエイトリンクを挿入してください
レビュー状態: 未レビュー
投稿状態: 未投稿

=== 編集チェックリスト ===
[ ] タイトルの確認・修正
[ ] アフィリエイトリンクの挿入
[ ] リスク開示文の確認
[ ] 画像の追加（アイキャッチ）
[ ] 内部リンクの追加
[ ] 投稿前の最終確認
-->

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(meta + article_content)

    # JSONサマリーも保存
    summary = {
        "date": today,
        "genre": genre_name,
        "keyword": keyword,
        "perspective": perspective["persona"],
        "filename": filename,
        "status": "draft"
    }

    summary_path = output_dir / f"summary_{today}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return filepath


def main():
    print(f"🚀 記事生成開始: {datetime.datetime.now()}")

    # 今日のジャンルと視点を選択
    genre_name, genre_data, keyword, perspective = select_todays_combination()

    print(f"📝 ジャンル: {genre_name}")
    print(f"🔑 キーワード: {keyword}")
    print(f"👤 視点: {perspective['persona']}")
    print("⏳ Claude APIで記事生成中...")

    # 記事生成
    article = generate_article(genre_name, genre_data, keyword, perspective)

    # 保存
    filepath = save_article(article, genre_name, keyword, perspective)

    print(f"✅ 記事生成完了！")
    print(f"📁 保存先: {filepath}")
    print(f"📌 次のステップ: drafts/フォルダの記事を編集・確認してからWordPressに投稿してください")


if __name__ == "__main__":
    main()
