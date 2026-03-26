#!/usr/bin/env python3
"""Print all Claude API rate limit headers from a test request."""

import anthropic


def main():
    client = anthropic.Anthropic()

    # Use with_raw_response to access HTTP headers
    with client.messages.with_raw_response.create(
        model="claude-haiku-4-5",
        max_tokens=1,
        messages=[{"role": "user", "content": "Hi"}],
    ) as raw:
        headers = raw.headers

    # Collect all rate limit headers
    rate_limit_headers = {
        key: value
        for key, value in headers.items()
        if key.lower().startswith(("x-ratelimit-", "retry-after", "anthropic-ratelimit-"))
    }

    if not rate_limit_headers:
        print("No rate limit headers found in response.")
        return

    # Group by category for readable output
    categories = {
        "Limits": [],
        "Remaining": [],
        "Resets": [],
        "Other": [],
    }

    for key, value in sorted(rate_limit_headers.items()):
        k = key.lower()
        if "limit-requests" in k or "limit-tokens" in k or "limit-input" in k or "limit-output" in k:
            if "remaining" not in k and "reset" not in k:
                categories["Limits"].append((key, value))
        elif "remaining" in k:
            categories["Remaining"].append((key, value))
        elif "reset" in k:
            categories["Resets"].append((key, value))
        else:
            categories["Other"].append((key, value))

    print("=" * 60)
    print("  Claude API Rate Limit Headers")
    print("=" * 60)

    for category, items in categories.items():
        if not items:
            continue
        print(f"\n{category}:")
        for key, value in items:
            # Strip common prefix for cleaner display
            display_key = key.replace("x-ratelimit-", "").replace("anthropic-ratelimit-", "")
            print(f"  {display_key:<35} {value}")

    print()


if __name__ == "__main__":
    main()
