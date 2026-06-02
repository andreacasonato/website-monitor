# Website Change Monitor

Monitors a list of websites for content changes on a schedule and sends an email notification when a change is detected. State is stored locally in JSON so changes are detected across runs.

## Setup

### 1. Install dependencies

```bash
pip3 install requests schedule python-dotenv
```

### 2. Create your URLs config file

Create `urls.json` in the project folder:

```json
[
  {
    "name": "Example Site",
    "url": "https://example.com"
  },
  {
    "name": "GitHub Trending",
    "url": "https://github.com/trending"
  }
]
```

### 3. Create your credentials file

Create `.env` in the project folder:

```
SENDER_EMAIL=your@gmail.com
SENDER_PASSWORD=your16charapppassword
RECEIVER_EMAIL=your@gmail.com
```

To generate a Gmail App Password:
- Go to myaccount.google.com
- Search "App Passwords"
- Create one called "website monitor"
- Paste the 16-character password without spaces

## Usage

```bash
python3 monitor.py                        # check every 60 minutes
python3 monitor.py --interval 30          # check every 30 minutes
python3 monitor.py --check-now            # run an immediate check, then schedule
python3 monitor.py --interval 5 --check-now   # immediate check, then every 5 minutes
```

Press `Ctrl+C` to stop the monitor.

## How it works

1. Fetches each URL and hashes the page content
2. Compares the hash against the previously stored one in `state.json`
3. If the hash changed, sends an email listing every changed URL
4. Saves the new state and waits for the next interval

## Notes

- `urls.json`, `state.json`, and `.env` are excluded from this repo
- Create them locally before running the monitor
- Sender and receiver email can be the same address
