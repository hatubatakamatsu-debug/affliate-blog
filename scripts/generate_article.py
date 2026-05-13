#!/usr/bin/env python3
"""
アフィリエイトブログ記事自動生成スクリプト
Claude APIを使用して7ジャンル × 8視点の記事を生成します
"""

import os
import json
import random
import datetime
import anthropic

# ─────────────────────────────────────────
# ジャンル定義
# ─────────────────────────────────────────
GENRES = [
    {"key": "金融",     "label": "💰 金融（クレジットカード・銀行）",    "keywords": ["クレジットカード", "銀行口座", "ポイント還元", "キャッシュレス"]},
    {"key": "投資",     "label": "📈 投資（NISA・iDeCo・株式）",         "keywords": ["NISA", "iDeCo", "インデックス投資", "積立投資"]},
    {"key": "不動産",   "label": "🏠 不動産投資",                         "keywords": ["不動産投資", "家賃収入", "賃貸経営", "不動産クラウドファンディング"]},
    {"key": "住宅ローン","label": "🏦 住宅ローン",                         "keywords": ["住宅ローン", "固定金利", "変動金利", "借り換え"]},
    {"key": "転職",     "label": "💼 転職",                               "keywords": ["転職エージェント", "年収アップ", "キャリアチェンジ", "転職サイト"]},
    {"key": "就職",     "label": "🎓 就職・就活",                          "keywords": ["就活", "新卒", "インターン", "内定"]},
    {"key": "保険",     "label": "🛡️ 保険",                              "keywords": ["生命保険", "医療保険", "火災保険", "保険見直し"]},
]

# ─────────────────────────────────────────
# 立場・視点定義
# ─────────────────────────────────────────
PERSONAS = [
    {
        "key": "20代会社員",
        "profile": "26歳・独身・会社員・年収350万円・都内一人暮らし",
        "concerns": "将来への不安、貯蓄の始め方、副業への興味",
    },
    {
        "key": "30代既婚子あり",
        "profile": "35歳・既婚・子供2人・世帯年収700万円・郊外在住",
        "concerns": "教育費、住宅ローン、老後資金の三重苦",
    },
    {
        "key": "40代管理職",
        "profile": "43歳・管理職・年収900万円・子供の大学進学を控える",
        "concerns": "資産形成の加速、税金対策、相続への備え",
    },
    {
        "key": "50代老後意識",
        "profile": "52歳・年収700万円・定年まで残り10年・老後資金が不安",
        "concerns": "退職金の運用、年金の仕組み、ダウンサイジング",
    },
    {
        "key": "20代女性フリーランス",
        "profile": "24歳・女性・フリーランスデザイナー・収入不安定",
        "concerns": "国民年金・国民健康保険の負担、収入変動への対応",
    },
    {
        "key": "地方中小企業",
        "profile": "38歳・地方在住・中小企業勤務・年収450万円",
        "concerns": "地方での資産形成、転職か起業か、都市部との格差",
    },
    {
        "key": "シングルマザー",
        "profile": "32歳・シングルマザー・子供1人・年収280万円",
        "concerns": "教育費の確保、生活費の節約、公的支援の活用",
    },
    {
        "key": "定年退職後",
        "profile": "63歳・定年退職済み・年金受給者・退職金2000万円",
        "concerns": "退職金の安全な運用、医療費への備え、生活費の確保",
    },
]


def build_prompt(genre: dict, persona: dict) -> str:
    """記事生成用プロンプトを構築"""
    keyword = random.choice(genre["keywords"])
    today = datetime.date.today().strftime("%Y年%m月%d日")

    return f"""あなたは次のプロフィールを持つ人物本人です。ライターではなく、自分の体験を語るブログを書いてください。

## あなた自身のプロフィール
{persona['profile']}
主な悩み・関心: {persona['concerns']}

## 記事条件
- ジャンル: {genre['label']}
- メインキーワード: {keyword}
- 文字数: 2000〜2500文字
- 公開日: {today}

## 記事構成（必ず守ること）
1. タイトル（<title>タグ内に記載、32文字以内、数字や具体性を含む）
2. リード文（200文字）：「私、〇〇で失敗しました」「正直、最初は全然うまくいきませんでした」など、自分の失敗や迷いから書き始める
3. H2見出し3〜4個（各500文字程度）：自分が実際に試したこと・感じたことを軸に書く
4. まとめ（200文字）：「向かない人もいる」と正直に書いた上で、行動を促すCTA

## 出力フォーマット
HTML形式で出力してください。以下の構造を使用:
- <title>記事タイトル</title>
- <meta name="description" content="120文字以内のディスクリプション">
- <article>タグで本文全体を囲む
- 見出しは<h2>、小見出しは<h3>
- 重要箇所は<strong>タグで強調
- リストは<ul>/<ol>タグを使用
- アフィリエイトリンク挿入箇所に <!-- AFFILIATE_LINK: {keyword}関連サービス名 --> のコメントを3箇所以上入れる

## 注意事項
- 金融商品は元本割れリスクなど必要な開示を含める
- 実在するサービス名を具体的に挙げる（ただし誇張しない）
- 「〜です。〜ます。」調の丁寧語で統一する
- 「正直に言うと…」「〜は向かない人もいます」など、本音っぽい表現を自然に盛り込む
- メリットだけでなく、自分が感じたデメリット・注意点も率直に書く
- ユーモアや軽いたとえ話を適度に盛り込み、読者が思わずクスッとできる箇所を1〜2か所入れる（ただし深刻なトピックでは控えめに）
"""


def generate_article(genre: dict, persona: dict, client: anthropic.Anthropic) -> str:
    """Claude APIで記事を生成"""
    prompt = build_prompt(genre, persona)

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def save_draft(content: str, genre: dict, persona: dict, date_str: str) -> str:
    """drafts/フォルダに下書きを保存"""
    drafts_dir = os.path.join(os.path.dirname(__file__), "..", "drafts")
    os.makedirs(drafts_dir, exist_ok=True)

    filename = f"draft_{date_str}_{genre['key']}_{persona['key']}.html"
    filepath = os.path.join(drafts_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"<!-- ジャンル: {genre['label']} -->\n")
        f.write(f"<!-- 視点: {persona['profile']} -->\n")
        f.write(f"<!-- 生成日: {date_str} -->\n\n")
        f.write(content)

    return filepath


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY が設定されていません")

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.date.today().strftime("%Y-%m-%d")

    # ランダムに1ジャンル × 1視点を選択（GitHub Actionsで毎日1記事）
    genre = random.choice(GENRES)
    persona = random.choice(PERSONAS)

    print(f"[{today}] 生成開始: {genre['label']} × {persona['key']}")

    content = generate_article(genre, persona, client)
    filepath = save_draft(content, genre, persona, today)

    print(f"保存完了: {filepath}")

    # サマリーJSONを更新
    summary_path = os.path.join(os.path.dirname(__file__), "..", "drafts", f"summary_{today}.json")
    summary = {
        "date": today,
        "genre": genre["key"],
        "genre_label": genre["label"],
        "persona": persona["key"],
        "persona_profile": persona["profile"],
        "filepath": os.path.basename(filepath),
        "status": "draft",
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"サマリー保存: {summary_path}")
    print("完了！drafts/ フォルダを確認して編集・アフィリエイトリンク挿入後に投稿してください。")


if __name__ == "__main__":
    main()
