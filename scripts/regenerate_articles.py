#!/usr/bin/env python3
"""
指定した記事を改修版プロンプトで再生成するスクリプト
"""

import os
import sys
import json
import datetime
import anthropic

# generate_article.py の関数を流用
sys.path.insert(0, os.path.dirname(__file__))
from generate_article import GENRES, PERSONAS, build_prompt, save_draft

# ─────────────────────────────────────────
# 再生成する記事を指定（ジャンルkey × 視点key）
# ─────────────────────────────────────────
ARTICLES_TO_REGENERATE = [
    {"genre_key": "転職",     "persona_key": "定年退職後"},
    {"genre_key": "住宅ローン","persona_key": "シングルマザー"},
    {"genre_key": "金融",     "persona_key": "40代管理職"},
]


def find_genre(key: str) -> dict:
    for g in GENRES:
        if g["key"] == key:
            return g
    raise ValueError(f"ジャンルが見つかりません: {key}")


def find_persona(key: str) -> dict:
    for p in PERSONAS:
        if p["key"] == key:
            return p
    raise ValueError(f"視点が見つかりません: {key}")


def regenerate(genre: dict, persona: dict, client: anthropic.Anthropic, today: str) -> str:
    prompt = build_prompt(genre, persona)
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY が設定されていません")

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.date.today().strftime("%Y-%m-%d")

    results = []
    for item in ARTICLES_TO_REGENERATE:
        genre = find_genre(item["genre_key"])
        persona = find_persona(item["persona_key"])

        print(f"再生成中: {genre['label']} × {persona['key']} ...")
        content = regenerate(genre, persona, client, today)
        filepath = save_draft(content, genre, persona, f"{today}_v2")
        print(f"  → 保存: {filepath}")
        results.append({"genre": genre["key"], "persona": persona["key"], "file": os.path.basename(filepath)})

    summary_path = os.path.join(os.path.dirname(__file__), "..", "drafts", f"regenerate_summary_{today}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n完了！{len(results)}記事を再生成しました。")
    print(f"サマリー: {summary_path}")
    print("drafts/ フォルダを確認して、WordPressに再投稿してください。")


if __name__ == "__main__":
    main()
