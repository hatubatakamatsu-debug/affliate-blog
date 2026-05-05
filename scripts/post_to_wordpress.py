#!/usr/bin/env python3
"""
WordPress投稿スクリプト
レビュー済みのHTMLドラフトをWordPressに下書き投稿します

使い方:
    python scripts/post_to_wordpress.py drafts/draft_2024-01-15_投資_20代会社員.html

環境変数:
    WP_URL          例: https://yourblog.com
    WP_USERNAME     WordPressユーザー名
    WP_APP_PASSWORD WordPressアプリパスワード（スペース区切りでOK）
"""

import os
import sys
import json
import re
import base64
import urllib.request
import urllib.error


def load_html(filepath: str) -> tuple[str, str]:
    """HTMLファイルからタイトルと本文を抽出"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # <title>タグからタイトルを取得
    title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath)

    # <article>タグがあれば本文として使用、なければ全体を使用
    article_match = re.search(r"<article.*?>(.*?)</article>", content, re.DOTALL)
    body = article_match.group(1).strip() if article_match else content

    # コメント行（<!-- ... -->のメタ情報）を除去
    body = re.sub(r"<!--\s*(ジャンル|視点|生成日):.*?-->\n?", "", body)

    return title, body


def extract_description(content: str) -> str:
    """metaディスクリプションを抽出"""
    match = re.search(r'<meta name="description" content="(.*?)"', content)
    return match.group(1) if match else ""


def post_to_wordpress(title: str, body: str, excerpt: str = "") -> dict:
    """WordPress REST API で下書き投稿"""
    wp_url = os.environ.get("WP_URL", "").rstrip("/")
    wp_user = os.environ.get("WP_USERNAME", "")
    wp_pass = os.environ.get("WP_APP_PASSWORD", "").replace(" ", "")

    if not all([wp_url, wp_user, wp_pass]):
        raise EnvironmentError(
            "WP_URL / WP_USERNAME / WP_APP_PASSWORD のいずれかが未設定です"
        )

    # Basic認証ヘッダー
    credentials = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()

    payload = json.dumps(
        {
            "title": title,
            "content": body,
            "excerpt": excerpt,
            "status": "draft",       # 必ず下書きで投稿（公開はしない）
            "categories": [],         # 必要に応じてカテゴリIDを指定
        }
    ).encode("utf-8")

    url = f"{wp_url}/wp-json/wp/v2/posts"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"WordPress APIエラー {e.code}: {error_body}") from e


def main():
    if len(sys.argv) < 2:
        print("使い方: python scripts/post_to_wordpress.py <drafts/ファイル名.html>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"エラー: ファイルが見つかりません: {filepath}")
        sys.exit(1)

    print(f"読み込み中: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    title, body = load_html(filepath)
    excerpt = extract_description(raw)

    print(f"タイトル: {title}")
    print(f"ディスクリプション: {excerpt[:60]}..." if len(excerpt) > 60 else f"ディスクリプション: {excerpt}")

    confirm = input("\n上記の内容でWordPressに下書き投稿しますか？ [y/N]: ").strip().lower()
    if confirm != "y":
        print("キャンセルしました")
        sys.exit(0)

    print("投稿中...")
    result = post_to_wordpress(title, body, excerpt)

    post_id = result.get("id")
    edit_link = result.get("link", "").replace("?p=", "wp-admin/post.php?post=") + "&action=edit"
    wp_url = os.environ.get("WP_URL", "").rstrip("/")

    print(f"\n投稿完了！")
    print(f"  投稿ID : {post_id}")
    print(f"  編集URL: {wp_url}/wp-admin/post.php?post={post_id}&action=edit")
    print(f"\nWordPress管理画面で最終確認・公開してください。")


if __name__ == "__main__":
    main()
