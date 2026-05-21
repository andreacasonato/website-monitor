#!/usr/bin/env python3
"""Website Change Monitor: check URLs for changes and notify via email."""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Monitor websites for content changes."
    )

    # How many minutes between each check
    # type=int converts the string to an integer automatically
    # default=60 means once per hour if the user doesn't specify
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Minutes between checks (default: 60)"
    )

    # --check-now runs one immediate check before starting the schedule
    # useful for testing without waiting for the first interval to pass
    parser.add_argument(
        "--check-now",
        action="store_true",
        help="Run an immediate check before starting the schedule"
    )

    args = parser.parse_args()

    print(f"Interval: every {args.interval} minute(s)")
    print(f"Check now: {args.check_now}")


if __name__ == "__main__":
    main()