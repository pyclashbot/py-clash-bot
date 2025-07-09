import argparse
import requests
import sys


def main():
    parser = argparse.ArgumentParser(description="Trigger Discord Webhook for release notification.")
    parser.add_argument('--prerelease', action='store_true', help='Is this a prerelease?')
    parser.add_argument('--version', required=True, help='Release version (e.g., v1.2.3)')
    parser.add_argument('--url', required=True, help='Release URL')
    parser.add_argument('--webhook-code', required=True, help='Discord webhook code')
    args = parser.parse_args()

    if args.prerelease:
        webhook_url = f"https://www.pyclashbot.app/api/webhook/release/prerelease?code={args.webhook_code}"
        title = f"New Pre-release! {args.version}"
    else:
        webhook_url = f"https://www.pyclashbot.app/api/webhook/release?code={args.webhook_code}"
        title = f"New Release! {args.version}"

    payload = {
        "title": title,
        "description": "Click to view changes and download",
        "url": args.url,
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"Webhook triggered successfully: {response.text}")
    except Exception as e:
        print(f"Failed to trigger webhook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 