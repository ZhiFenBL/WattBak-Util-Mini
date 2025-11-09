#!/usr/bin/env python3
import os
import sys
import subprocess

def read_usernames(file_path):
    if not os.path.exists(file_path):
        print(f"❌ User file not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        users = [u.strip() for u in f if u.strip() and not u.startswith("#")]
    return sorted(set(users))  # remove duplicates + sorted order


def run_downloader(username, index, total):
    print(f"\n[{index}/{total}] ▶ {username}")
    try:
        subprocess.run(["uv", "run", "book_downloader.py", username],
                       check=True, capture_output=False)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while processing {username}: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run book_automate.py <users.txt>")
        sys.exit(1)

    users_file = sys.argv[1]
    users = read_usernames(users_file)
    total = len(users)

    print(f"📋 {total} unique users to process.\n")

    for i, username in enumerate(users, start=1):
        run_downloader(username, i, total)

    print("\n✅ All users processed successfully.")


if __name__ == "__main__":
    main()