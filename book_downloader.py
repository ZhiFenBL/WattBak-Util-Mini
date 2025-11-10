#!/usr/bin/env python3
import os
import sys
import requests
import subprocess
import json
import time

API_BASE = "https://www.wattpad.com/api/v3"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_json(url):
    for _ in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 400:
                # stop pagination after invalid offset
                return None
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"⚠️ Error fetching {url}: {e}")
            time.sleep(2)
    return None


def get_all_stories(username):
    """Paginate through all stories for a user."""
    stories = []
    url = f"{API_BASE}/users/{username}/stories?fields=stories(id,modifyDate)&limit=100"

    while url:
        data = fetch_json(url)
        if not data:
            break
        stories.extend(data.get("stories", []))
        url = data.get("nextUrl")
        if url and "offset=2000" in url:  # limit offset
            break

    return stories


def load_existing_stories(json_path):
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_stories_json(json_path, data):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def download_story(story_id, output_dir):
    cmd = [
        "wp-mini-epub-cli", "do",
        "--id", str(story_id),
        "--img",
        "--output-path", output_dir
    ]
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading story {story_id}: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run book_downloader.py <username>")
        sys.exit(1)

    username = sys.argv[1].strip().lower()
    base_dir = os.path.join("book_data", username)
    os.makedirs(base_dir, exist_ok=True)
    json_path = os.path.join(base_dir, "stories.json")

    print(f"📚 Fetching stories for user: {username}")
    stories = get_all_stories(username)

    if not stories:
        print("❌ No stories found.")
        return

    print(f"✅ Found {len(stories)} stories.")
    existing = load_existing_stories(json_path)
    updated = {}

    for i, s in enumerate(stories, 1):
        story_id = str(s.get("id"))
        modify_date = s.get("modifyDate")
        if not story_id:
            continue

        prev_date = existing.get(story_id)
        if prev_date == modify_date:
            print(f"[{i}/{len(stories)}] ⏩ Up to date: {story_id}")
            updated[story_id] = modify_date
            continue

        print(f"[{i}/{len(stories)}] ⬇️ Downloading story {story_id} (updated or new)")
        if download_story(story_id, base_dir):
            updated[story_id] = modify_date
        else:
            print(f"⚠️ Skipped {story_id}")

    save_stories_json(json_path, updated)
    print(f"\n🎉 Completed! JSON updated at {json_path}")


if __name__ == "__main__":
    main()