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
# キーワードは「今すぐ客」向けの短い比較キーワードではなく、
# 悩み・不安を抱えた人が実際に検索しそうなロングテールキーワードを採用。
# 新規サイトでも上位表示を狙いやすく、記事のペルソナ・悩みとも一致しやすい。
GENRES = {
    "金融": {
        "keywords": [
            "手取り20万円 貯金できない 原因",
            "クレジットカード 使いすぎ 対策",
            "家計簿 三日坊主 改善方法",
            "貯金 苦手 性格 直し方",
            "電子マネー チャージ 使いすぎ 防ぐ",
            "銀行口座 使い分け コツ",
            "ボーナス 使い道 貯金 割合"
        ],
        "affiliate": "クレジットカード・銀行口座開設"
    },
    "投資": {
        "keywords": [
            "つみたてNISA 損した 知恵袋",
            "iDeCo デメリット 後悔",
            "投資信託 選び方 わからない",
            "少額投資 意味ない と言われる理由",
            "投資 怖くて始められない",
            "積立投資 続かない 原因",
            "老後資金 いくら必要 不安"
        ],
        "affiliate": "証券口座開設"
    },
    "不動産": {
        "keywords": [
            "マンション購入 後悔 知恵袋",
            "中古マンション 注意点 見落としがち",
            "賃貸と持ち家 どっちが得 シミュレーション",
            "不動産投資 やめとけ 理由",
            "新築マンション 契約後 不安",
            "実家 相続 どうする 揉める"
        ],
        "affiliate": "不動産査定・投資サービス"
    },
    "住宅ローン": {
        "keywords": [
            "住宅ローン 審査落ち 理由",
            "変動金利 上がったらどうなる",
            "住宅ローン 返済きつい 知恵袋",
            "繰り上げ返済 しない方がいい 理由",
            "住宅ローン 借り換え タイミング いつ",
            "火災保険 相場 わからない 住宅ローン"
        ],
        "affiliate": "住宅ローン申込み"
    },
    "転職": {
        "keywords": [
            "転職 3社目 やばい",
            "未経験 転職 30代 厳しい",
            "転職エージェント しつこい 断り方",
            "転職 決まらない 原因",
            "転職 年収下がった 後悔",
            "地方 転職 求人少ない 悩み"
        ],
        "affiliate": "転職エージェント登録"
    },
    "就職": {
        "keywords": [
            "就活 内定ゼロ 焦り",
            "面接 落ちる理由 わからない",
            "自己分析 意味ない と言われる",
            "就活エージェント 微妙 知恵袋",
            "新卒 就職先 決まらない 不安"
        ],
        "affiliate": "就活支援サービス登録"
    },
    "保険": {
        "keywords": [
            "生命保険 入りすぎ 見直し",
            "医療保険 いらない 論争",
            "火災保険 相場 わからない",
            "自動車保険 更新 高くなった",
            "保険 見直し タイミング わからない",
            "独身 保険 いらない と言われる"
        ],
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
あなたは「マネーライフナビ」というお金に関する情報サイトの運営者本人として記事を書きます。
運営者はファイナンシャルプランナー等の専門資格を持つ専門家ではなく、
自分自身で公的機関や各サービスの公開情報を調べてまとめる一個人という立場です。
「専門家として教える」のではなく「同じ悩みを持つ人のために調べた内容を共有する」というスタンスで、
読者に本当に役立つ高品質なブログ記事を書いてください。

このブログの一番大事な目的は、アフィリエイト収益そのものではなく、
「同じお金の悩みを抱える読者に、本当に寄り添って、少しでも安心してもらうこと」です。
そのために、以下のトーンを必ず意識してください。
- 読者を見下したり、教科書的に正論を押し付けたりしない。「隣で一緒に悩んでくれる友人」のような距離感で書く
- 読者の失敗や不安を茶化さず、まず「そう思うのは当然ですよ」と受け止めてから話を進める
- 記事のどこかに、思わずクスッと笑えるような、リアルであるあるなユーモア（例えば運営者自身の失敗談・あるあるな本音のツッコミなど）を最低1箇所は自然に入れる。ただし悩みの深刻さを軽視するようなブラックユーモアや皮肉にはしない
- 「アフィリエイト商品を売るための記事」ではなく「読者の悩みを解決した結果、たまたま役立つサービスを紹介する記事」という順序を守る

## 記事条件
- **ジャンル**: {genre_name}
- **メインキーワード（検索意図）**: {keyword}
- **アフィリエイト商品**: {genre_data["affiliate"]}
- **文字数**: 2500〜3500字
- 上記メインキーワードで検索する人が何を知りたいか・どんな不安を解消したいかを最初に想像し、その検索意図に正面から答える記事にすること

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
- 運営者自身を「専門家」「FP」「監修者」など専門資格保有者であるかのように名乗らせない。あくまで「自分で調べた一個人」というトーンを保つ
- 記事全体を通して「読者を大事にする気持ち」が伝わる文章にすること。テンプレ的な明るさではなく、悩みに真摯に向き合った上でのユーモアであること
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


# 全記事共通で末尾に挿入する運営者情報・免責事項への導線（E-E-A-T対策）
AUTHOR_DISCLAIMER_HTML = """
<div style="background:#f9fafb;border:1px solid #d1d5db;border-radius:8px;padding:16px 20px;margin:28px 0;font-size:0.9em;color:#374151;">
<p style="margin:0 0 6px 0;">この記事は、運営者（Ikuo）が自分自身で調べ、まとめた内容です。専門家による監修を受けたものではありません。より詳しい・個別の判断が必要な内容は、専門家や各サービスの窓口に直接ご相談ください。</p>
<p style="margin:0;"><a href="/about/">運営者情報</a>　<a href="/disclaimer/">免責事項</a>　<a href="/privacy-policy-2/">プライバシーポリシー</a></p>
</div>
"""

# 転職・就職カテゴリ専用CTA（2026-07-27 もしもアフィリエイトで提携した、
# 実際に転職・就職支援を行うサービスへの導線。内容と無関係な金融相談CTAではなく、
# 読者の悩み（転職・就活）に直接応えるサービスを紹介する）
CAREER_CTA_HTML = """
<div style="background:#eff6ff;border:1px solid #93c5fd;border-radius:8px;padding:16px 20px;margin:28px 0;">
<p style="margin:0 0 10px 0;font-weight:bold;">一人で抱え込まず、プロに話を聞いてもらうという選択肢</p>
<p style="margin:0 0 10px 0;">転職や就活の悩みは、誰かに話すだけで整理できることもあります。どちらも無料相談なので、「まだ転職するか決めていない」という段階でも気軽に利用できます。</p>
<p style="margin:0 0 6px 0;">▶ <a href="//af.moshimo.com/af/c/click?a_id=5716939&p_id=5870&pc_id=16301&pl_id=75201&url=https%3A%2F%2Fremoful.com%2Fmoshimo" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">Remoful（リモフル）でキャリア相談する</a></p>
<p style="margin:0;">▶ <a href="//af.moshimo.com/af/c/click?a_id=5716940&p_id=7239&pc_id=20766&pl_id=91222" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">サクキャリマッチで無料面談を申し込む</a></p>
<img src="//i.moshimo.com/af/i/impression?a_id=5716939&p_id=5870&pc_id=16301&pl_id=75201" width="1" height="1" style="border:none;" loading="lazy">
<img src="//i.moshimo.com/af/i/impression?a_id=5716940&p_id=7239&pc_id=20766&pl_id=91222" width="1" height="1" style="border:none;" loading="lazy">
</div>
"""

# CAREER_CTA_HTML を挿入する対象ジャンル
CAREER_CTA_GENRES = {"転職", "就職"}


def _append_author_disclaimer(article_content: str, genre_name: str = None) -> str:
    """<article>タグ内の末尾（</article>直前）に運営者情報リンク（と該当ジャンルならCTA）を挿入する"""
    insertion = ""
    if genre_name in CAREER_CTA_GENRES:
        insertion += CAREER_CTA_HTML
    insertion += AUTHOR_DISCLAIMER_HTML

    if "</article>" in article_content:
        return article_content.replace("</article>", insertion + "</article>", 1)
    return article_content + insertion


def save_article(article_content, genre_name, keyword, perspective):
    """記事をファイルに保存（人間レビュー用）"""
    article_content = _append_author_disclaimer(article_content, genre_name)

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
