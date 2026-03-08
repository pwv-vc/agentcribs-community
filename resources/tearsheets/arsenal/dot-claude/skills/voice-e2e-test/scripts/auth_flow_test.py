#!/usr/bin/env python3
"""
Auth Flow Test Script for Voice E2E Testing

Combines Steps 3-6 into a single script:
- BASE_URL: Check localStorage is empty
- FULL_URL: Check token is stored
- REFRESH: Check token persists
- BUTTON: Click "We're both here" button

Usage:
    python3 auth_flow_test.py --call-sid CA123... --token abc123... --screenshot-dir .playwright/...
"""

import argparse
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright


def timestamp():
    return datetime.now().strftime("%H:%M:%S")


def run_auth_flow(call_sid: str, token: str, screenshot_dir: str) -> bool:
    """Run all auth flow checks. Returns True if all pass, False otherwise."""

    base_url = "https://voice.wren.ngrok.dev/voice/verify"
    full_url = f"{base_url}?call_sid={call_sid}&token={token}"

    all_passed = True

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Sub-step: BASE_URL check
        print(f"[3:BASE_URL]  START: {timestamp()}")
        start = datetime.now()
        page.goto(base_url)
        page.wait_for_load_state('networkidle')
        local_storage = page.evaluate("() => JSON.stringify(localStorage)")
        is_empty = local_storage == "{}"
        duration = (datetime.now() - start).seconds
        status = "✓" if is_empty else "✗"
        result = "localStorage empty" if is_empty else "localStorage NOT empty"
        print(f"[3:BASE_URL]  END: {timestamp()} ({duration}s) - {result} {status}")
        page.screenshot(path=f"{screenshot_dir}/e2e-03-base-url.png")
        if not is_empty:
            all_passed = False

        # Sub-step: FULL_URL check
        print(f"[3:FULL_URL]  START: {timestamp()}")
        start = datetime.now()
        page.goto(full_url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)  # Give JS time to store token
        local_storage = page.evaluate("() => JSON.stringify(localStorage)")
        has_token = "voice-dashboard-auth" in local_storage
        duration = (datetime.now() - start).seconds
        status = "✓" if has_token else "✗"
        result = "token stored" if has_token else "token NOT stored"
        print(f"[3:FULL_URL]  END: {timestamp()} ({duration}s) - {result} {status}")
        page.screenshot(path=f"{screenshot_dir}/e2e-03-full-url.png")
        if not has_token:
            all_passed = False

        # Sub-step: REFRESH check
        print(f"[3:REFRESH]   START: {timestamp()}")
        start = datetime.now()
        page.reload()
        page.wait_for_load_state('networkidle')
        local_storage_after = page.evaluate("() => JSON.stringify(localStorage)")
        persists = "voice-dashboard-auth" in local_storage_after
        duration = (datetime.now() - start).seconds
        status = "✓" if persists else "✗"
        result = "token persists" if persists else "token LOST"
        print(f"[3:REFRESH]   END: {timestamp()} ({duration}s) - {result} {status}")
        page.screenshot(path=f"{screenshot_dir}/e2e-03-refresh.png")
        if not persists:
            all_passed = False

        # Sub-step: BUTTON click
        print(f"[3:BUTTON]    START: {timestamp()}")
        start = datetime.now()
        button = page.locator("text=We're both here now")
        if button.count() > 0:
            button.click()
            page.wait_for_timeout(2000)
            duration = (datetime.now() - start).seconds
            print(f"[3:BUTTON]    END: {timestamp()} ({duration}s) - button clicked ✓")
        else:
            duration = (datetime.now() - start).seconds
            print(f"[3:BUTTON]    END: {timestamp()} ({duration}s) - button NOT FOUND ✗")
            all_passed = False
        page.screenshot(path=f"{screenshot_dir}/e2e-03-button.png")

        browser.close()

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Auth flow test for Voice E2E")
    parser.add_argument("--call-sid", required=True, help="Call SID from confirmation link")
    parser.add_argument("--token", required=True, help="Auth token from confirmation link")
    parser.add_argument("--screenshot-dir", required=True, help="Directory for screenshots")

    args = parser.parse_args()

    success = run_auth_flow(args.call_sid, args.token, args.screenshot_dir)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
