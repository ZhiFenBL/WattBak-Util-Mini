#!/usr/bin/env python3
import os
import sys
import json
import requests

API_BASE = "https://www.wattpad.com/api/v3"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_json(url):
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()

def get_all_stories(username):
    stories = []
    url = f"{API_BASE}/users/{username}/stories?fields=stories(id,modifyDate)&limit=100"
    while url:
        data = fetch_json(url)
        stories.extend(data.get("stories", []))
        url = data.get("nextUrl")
        if url and "offset=2000" in url:
            break
    return stories

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run book_update_checker.py <usernames.txt>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print("❌ File not found.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        usernames = [u.strip() for u in f if u.strip()]

    for username in usernames:
        json_path = os.path.join("book_data", username, "stories.json")
        if not os.path.exists(json_path):
            print(f"🆕 {username}: No local data yet (new user)")
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            local = json.load(f)

        remote = get_all_stories(username)
        updates = []

        for s in remote:
            sid = str(s["id"])
            mdate = s["modifyDate"]
            if sid not in local or local[sid] != mdate:
                updates.append(sid)

        if updates:
            print(f"🔄 {username}: {len(updates)} stories updated/new → {', '.join(updates)}")
        else:
            print(f"✅ {username}: All up to date.")


if __name__ == "__main__":
    main()
