"""Website Change Monitor: check URLs for changes and notify via email."""

import argparse
import hashlib
import json
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import requests
import schedule
from dotenv import load_dotenv


load_dotenv()

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


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


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


def send_email(changes: list) -> None:
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    receiver = os.getenv("RECEIVER_EMAIL")
    if not all([sender, password, receiver]):
        print("  [ERROR] Missing email credentials in .env file.")
        return
    body = "The following websites have changed:\n\n"
    for entry in changes:
        body += f"  - {entry['name']}: {entry['url']}\n"
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"Website Monitor: {len(changes)} change(s) detected"
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"  [EMAIL] Notification sent to {receiver}")
    except Exception as e:
        print(f"  [ERROR] Failed to send email: {e}")


# This is the function schedule will call on every interval
def run_check() -> None:
    urls = load_urls()
    if not urls:
        return
    state = load_state()
    changes = check_urls(urls, state)
    save_state(state)
    if changes:
        print(f"\n{len(changes)} change(s) detected.")
        send_email(changes)
    else:
        print("\nNo changes detected.")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor websites for content changes."
    )
    parser.add_argument("--interval", type=int, default=60,
        help="Minutes between checks (default: 60)")
    parser.add_argument("--check-now", action="store_true",
        help="Run an immediate check before starting the schedule")

    args = parser.parse_args()

    # Run an immediate check if --check-now was passed
    if args.check_now:
        print("Running immediate check...")
        run_check()

    # Schedule run_check() to run every X minutes
    schedule.every(args.interval).minutes.do(run_check)
    print(f"\nMonitor running. Checking every {args.interval} minute(s).")
    print("Press Ctrl+C to stop.\n")

    # Keep the script alive, checking every second if a job is due
    # time.sleep(1) prevents the loop from consuming 100% CPU
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()