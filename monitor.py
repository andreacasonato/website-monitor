#!/usr/bin/env python3
"""Website Change Monitor: check URLs for changes and notify via email."""

import argparse
import json
from pathlib import Path


# Load the list of URLs from urls.json
def load_urls() -> list:
    config_path = Path(__file__).parent / "urls.json"

    if not config_path.exists():
        print("Error: urls.json not found. Create it first.")
        return []

    with open(config_path, "r", encoding="utf-8") as f:
        urls = json.load(f)

    # Guard: make sure it's a list and not empty
    if not isinstance(urls, list) or len(urls) == 0:
        print("Error: urls.json must contain a non-empty list.")
        return []

    print(f"Loaded {len(urls)} URL(s):")
    for entry in urls:
        print(f"  - {entry['name']}: {entry['url']}")

    return urls


def main():
    parser = argparse.ArgumentParser(
        description="Monitor websites for content changes."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Minutes between checks (default: 60)"
    )
    parser.add_argument(
        "--check-now",
        action="store_true",
        help="Run an immediate check before starting the schedule"
    )

    args = parser.parse_args()

    # Load URLs on startup
    urls = load_urls()
    if not urls:
        return

    print(f"\nInterval: every {args.interval} minute(s)")


if __name__ == "__main__":
    main()