"""Website Change Monitor: check URLs for changes and notify via email."""

import argparse
import hashlib       # NEW
import json
from pathlib import Path
import requests      # NEW


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


# Fetch a URL and return a hash of its content
def fetch_hash(url: str) -> str | None:
    try:
        # timeout=10 means give up after 10 seconds if no response
        response = requests.get(url, timeout=10)

        # raises an error if the server returned
        # a failure code like 404 (not found) or 500 (server error)
        response.raise_for_status()

        # Encode the content to bytes, then hash it with md5
        # hexdigest() returns the hash as a readable string like "a3f5b2c1..."
        content = response.text.encode("utf-8")
        return hashlib.md5(content).hexdigest()

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Could not fetch {url}: {e}")
        return None


# Check all URLs and print their current hash
def check_urls(urls: list) -> None:
    print("\nChecking URLs...")
    for entry in urls:
        name = entry["name"]
        url = entry["url"]
        print(f"  Checking: {name}")
        hash_value = fetch_hash(url)
        if hash_value:
            print(f"  Hash: {hash_value}")


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

    # Run an immediate check
    check_urls(urls)


if __name__ == "__main__":
    main()