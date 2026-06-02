"""Website Change Monitor: check URLs for changes and notify via email."""

import argparse
import hashlib
import json
from pathlib import Path
import requests


STATE_FILE = Path(__file__).parent / "state.json"


def load_urls() -> list:
    config_path = Path(__file__).parent / "urls.json"
    if not config_path.exists():
        print("Error: urls.json not found. Create it first.")
        return []
    with open(config_path, "r", encoding="utf-8") as f:
        urls = json.load(f)
    if not isinstance(urls, list) or len(urls) == 0:
        print("Error: urls.json must contain a non-empty list.")
        return []
    return urls


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# Write the updated state back to state.json
def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        # indent=2 makes the file readable — one key per line, indented
        json.dump(state, f, indent=2)
    print(f"  State saved.")


def fetch_hash(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text.encode("utf-8")
        return hashlib.md5(content).hexdigest()
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Could not fetch {url}: {e}")
        return None


def check_urls(urls: list, state: dict) -> list:
    print("\nChecking URLs...")
    changes = []

    for entry in urls:
        name = entry["name"]
        url = entry["url"]
        print(f"  Checking: {name}")

        new_hash = fetch_hash(url)
        if new_hash is None:
            continue

        old_hash = state.get(url)

        if old_hash is None:
            print(f"  [NEW]     First check recorded.")
            state[url] = new_hash
        elif old_hash != new_hash:
            print(f"  [CHANGED] Change detected on {name}!")
            state[url] = new_hash
            changes.append(entry)
        else:
            print(f"  [OK]      No change.")

    return changes


def main():
    parser = argparse.ArgumentParser(
        description="Monitor websites for content changes."
    )
    parser.add_argument("--interval", type=int, default=60,
        help="Minutes between checks (default: 60)")
    parser.add_argument("--check-now", action="store_true",
        help="Run an immediate check before starting the schedule")

    args = parser.parse_args()

    urls = load_urls()
    if not urls:
        return

    state = load_state()
    changes = check_urls(urls, state)

    # Save state after every check
    save_state(state)

    if changes:
        print(f"\n{len(changes)} change(s) detected:")
        for entry in changes:
            print(f"  - {entry['name']}: {entry['url']}")
    else:
        print("\nNo changes detected.")


if __name__ == "__main__":
    main()