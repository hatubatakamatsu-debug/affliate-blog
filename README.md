# アフィリエイトブログ自動生成システム

毎朝9時にClaude APIが記事を自動生成し、`drafts/` フォルダに保存します。
人間が確認・編集後、WordPressへ投稿します。

---

## セットアップ手順

### 1. GitHubリポジトリ作成（Private推奨）

```bash
cd ~/Documents/affiliate-blog
git init
git add .
git commit -m "initial commit"
# GitHub上でPrivateリポジトリを作成してから:
git remote add origin https://github.com/あなたのユーザー名/affiliate-blog.git
git push -u origin main
```

### 2. GitHub Secrets を設定

リポジトリ → Settings → Secrets and variables → Actions → New repository secret

| シークレット名 | 値 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude APIキー（[console.anthropic.com](https://console.anthropic.com)） |
| `WP_URL` | `https://yourblog.com` |
| `WP_USERNAME` | WordPressユーザー名 |
| `WP_APP_PASSWORD` | WordPressアプリパスワード |

### 3. WordPressアプリパスワード取得

1. WordPress管理画面 → ユーザー → プロフィール
2. 「アプリケーションパスワード」セクション
3. 名前（例: GitHub Actions）を入力 → 追加
4. 表示されたパスワードを `WP_APP_PASSWORD` シークレットに登録

---

## 毎日の作業フロー

```
【自動】毎朝9時 → GitHub Actions → Claude API → drafts/ に保存 → mainブランチにコミット

【手動】
1. drafts/draft_YYYY-MM-DD_ジャンル_視点.html を開く
2. 内容を確認・編集
3. <!-- AFFILIATE_LINK: xxx --> 箇所に実際のアフィリエイトリンクを挿入
4. 下記コマンドでWordPressに下書き投稿
5. WordPress管理画面で最終確認 → 公開
```

### 投稿コマンド

```bash
export WP_URL="https://yourblog.com"
export WP_USERNAME="あなたのユーザー名"
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

pip install anthropic   # 初回のみ
python scripts/post_to_wordpress.py drafts/draft_2024-01-15_投資_20代会社員.html
```

### 手動で記事を生成したい場合

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python scripts/generate_article.py
```

---

## ジャンル・視点の一覧

| ジャンル | 代表キーワード |
|---|---|
| 金融（クレカ・銀行） | クレジットカード、ポイント還元 |
| 投資（NISA・iDeCo） | インデックス投資、積立NISA |
| 不動産 | 家賃収入、不動産クラウドファンディング |
| 住宅ローン | 固定金利、借り換え |
| 転職 | 転職エージェント、年収アップ |
| 就職 | 就活、インターン |
| 保険 | 生命保険、医療保険 |

| 立場 | プロフィール概要 |
|---|---|
| 20代会社員 | 26歳・年収350万・一人暮らし |
| 30代既婚子あり | 35歳・世帯年収700万 |
| 40代管理職 | 43歳・年収900万 |
| 50代老後意識 | 52歳・定年まで10年 |
| 20代女性フリーランス | 24歳・収入不安定 |
| 地方中小企業 | 38歳・年収450万 |
| シングルマザー | 32歳・年収280万 |
| 定年退職後 | 63歳・年金受給者 |

---

## 注意事項

- **必ず人間が確認・編集**してから公開すること（Googleガイドライン遵守）
- 金融記事は**元本割れリスク等の開示**を確認すること
- 使用するASPの**AI記事に関する規約**を事前に確認すること
