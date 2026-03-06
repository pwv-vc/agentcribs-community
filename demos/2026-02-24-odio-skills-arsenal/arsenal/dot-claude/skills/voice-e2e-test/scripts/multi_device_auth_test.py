#!/usr/bin/env python3
"""
Multi-Device Auth Test - Reproduces the auth error when opening link on second device.

This test demonstrates the bug in validate_voice_auth_token_active() where it always
checks expires_at (5-minute initial TTL) instead of session_expires_at (24-hour session)
when the ticket is already confirmed.

Scenario:
1. Device 1 (phone) opens link, confirms auth
2. Device 2 (desktop) opens same link after initial TTL expires
3. Device 2 gets 401 "Token expired" even though session should be valid for 24h

Usage:
    python3 multi_device_auth_test.py --call-sid CA123... --token abc123...

For manual testing with short TTL:
    python3 multi_device_auth_test.py --call-sid CA123... --token abc123... --wait-seconds 310
"""

import argparse
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright


def timestamp():
    return datetime.now().strftime("%H:%M:%S")


def run_multi_device_test(call_sid: str, token: str, base_url: str, wait_seconds: int) -> dict:
    """
    Simulate multi-device auth flow.

    Returns dict with test results.
    """
    full_url = f"{base_url}/voice/verify?call_sid={call_sid}&token={token}"
    api_base = base_url.rstrip('/')

    results = {
        "device1_confirm": None,
        "device1_tips": None,
        "device1_localStorage": None,
        "wait_seconds": wait_seconds,
        "device2_confirm": None,
        "device2_tips": None,
        "device2_tips_error": None,
        "passed": False,
    }

    with sync_playwright() as p:
        # ==========================================
        # DEVICE 1 (Phone) - First browser context
        # ==========================================
        print(f"\n[DEVICE 1] START: {timestamp()}")
        print(f"[DEVICE 1] Opening: {full_url[:80]}...")

        browser1 = p.chromium.launch(headless=True)
        context1 = browser1.new_context()
        page1 = context1.new_page()

        # Open verification page
        page1.goto(full_url)
        page1.wait_for_load_state('networkidle')
        page1.wait_for_timeout(2000)  # Wait for JS to execute

        # Check localStorage was set
        local_storage = page1.evaluate("() => JSON.stringify(localStorage)")
        results["device1_localStorage"] = "voice-dashboard-auth" in local_storage
        print(f"[DEVICE 1] localStorage set: {results['device1_localStorage']}")

        # The page auto-confirms, let's verify by calling /tips
        tips_url = f"{api_base}/api/voice/tips?call_sid={call_sid}&token={token}"
        tips_response = page1.evaluate(f"""
            async () => {{
                const response = await fetch("{tips_url}");
                return {{
                    status: response.status,
                    ok: response.ok,
                    body: response.ok ? await response.json() : await response.text()
                }};
            }}
        """)

        results["device1_tips"] = tips_response["status"]
        print(f"[DEVICE 1] /tips response: {tips_response['status']}")

        if tips_response["status"] != 200:
            print(f"[DEVICE 1] ERROR: Tips failed with {tips_response['status']}: {tips_response['body']}")
            browser1.close()
            return results

        # Confirm endpoint should also work
        confirm_url = f"{api_base}/api/voice/call-auth/confirm"
        confirm_response = page1.evaluate(f"""
            async () => {{
                const response = await fetch("{confirm_url}", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ call_id: "{call_sid}", token: "{token}" }})
                }});
                return {{ status: response.status, ok: response.ok }};
            }}
        """)

        results["device1_confirm"] = confirm_response["status"]
        print(f"[DEVICE 1] /confirm response: {confirm_response['status']}")
        print(f"[DEVICE 1] END: {timestamp()}")

        # Close device 1 browser (simulating user closing phone)
        browser1.close()

        # ==========================================
        # WAIT - Simulate time passing
        # ==========================================
        if wait_seconds > 0:
            print(f"\n[WAIT] Waiting {wait_seconds} seconds to simulate time passing...")
            print(f"[WAIT] (This simulates opening link on desktop after initial 5-min TTL expires)")

            # Show countdown for long waits
            if wait_seconds > 10:
                for remaining in range(wait_seconds, 0, -30):
                    print(f"[WAIT] {remaining} seconds remaining...")
                    time.sleep(min(30, remaining))
            else:
                time.sleep(wait_seconds)

            print(f"[WAIT] Done waiting")

        # ==========================================
        # DEVICE 2 (Desktop) - Second browser context
        # ==========================================
        print(f"\n[DEVICE 2] START: {timestamp()}")
        print(f"[DEVICE 2] Opening same link on different device...")

        browser2 = p.chromium.launch(headless=True)
        context2 = browser2.new_context()  # Fresh context = no localStorage from device 1
        page2 = context2.new_page()

        # Verify localStorage is empty (different device)
        page2.goto(base_url)  # Go to base first to check localStorage
        local_storage_2 = page2.evaluate("() => JSON.stringify(localStorage)")
        device2_has_auth = "voice-dashboard-auth" in local_storage_2
        print(f"[DEVICE 2] localStorage before: {local_storage_2[:100] if len(local_storage_2) > 100 else local_storage_2}")

        if device2_has_auth:
            print("[DEVICE 2] WARNING: Device 2 already has auth in localStorage (unexpected)")

        # Now open the verification link
        page2.goto(full_url)
        page2.wait_for_load_state('networkidle')
        page2.wait_for_timeout(2000)

        # Check if page shows error or loads correctly
        page_content = page2.content()

        # Try /confirm endpoint
        confirm_response_2 = page2.evaluate(f"""
            async () => {{
                const response = await fetch("{confirm_url}", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ call_id: "{call_sid}", token: "{token}" }})
                }});
                return {{
                    status: response.status,
                    ok: response.ok,
                    body: response.ok ? "" : await response.text()
                }};
            }}
        """)

        results["device2_confirm"] = confirm_response_2["status"]
        print(f"[DEVICE 2] /confirm response: {confirm_response_2['status']}")

        # Try /tips endpoint - THIS IS WHERE THE BUG MANIFESTS
        tips_response_2 = page2.evaluate(f"""
            async () => {{
                const response = await fetch("{tips_url}");
                return {{
                    status: response.status,
                    ok: response.ok,
                    body: response.ok ? await response.json() : await response.text()
                }};
            }}
        """)

        results["device2_tips"] = tips_response_2["status"]
        results["device2_tips_error"] = tips_response_2.get("body") if not tips_response_2["ok"] else None

        print(f"[DEVICE 2] /tips response: {tips_response_2['status']}")
        if not tips_response_2["ok"]:
            print(f"[DEVICE 2] /tips error: {tips_response_2['body']}")

        print(f"[DEVICE 2] END: {timestamp()}")

        browser2.close()

    # ==========================================
    # ANALYZE RESULTS
    # ==========================================
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    print(f"\nDevice 1 (Phone):")
    print(f"  /confirm: {results['device1_confirm']} {'✓' if results['device1_confirm'] == 204 else '✗'}")
    print(f"  /tips:    {results['device1_tips']} {'✓' if results['device1_tips'] == 200 else '✗'}")
    print(f"  localStorage: {'set ✓' if results['device1_localStorage'] else 'NOT set ✗'}")

    print(f"\nWait: {results['wait_seconds']} seconds")

    print(f"\nDevice 2 (Desktop):")
    print(f"  /confirm: {results['device2_confirm']} {'✓' if results['device2_confirm'] == 204 else '✗'}")
    print(f"  /tips:    {results['device2_tips']} {'✓' if results['device2_tips'] == 200 else '✗'}")
    if results['device2_tips_error']:
        print(f"  /tips error: {results['device2_tips_error']}")

    # The bug: /confirm succeeds (returns 204 when already confirmed without checking token)
    # but /tips fails with 401 because validate_voice_auth_token_active checks expires_at
    # instead of session_expires_at

    if results['device2_confirm'] == 204 and results['device2_tips'] == 401:
        print("\n🐛 BUG CONFIRMED: /confirm succeeds but /tips fails with 401")
        print("   This happens because validate_voice_auth_token_active() checks")
        print("   expires_at (5-min) instead of session_expires_at (24h)")
        results["passed"] = False
    elif results['device2_confirm'] == 204 and results['device2_tips'] == 200:
        print("\n✓ PASS: Both endpoints work on device 2")
        results["passed"] = True
    else:
        print(f"\n? UNEXPECTED: confirm={results['device2_confirm']}, tips={results['device2_tips']}")
        results["passed"] = False

    return results


def main():
    parser = argparse.ArgumentParser(description="Multi-device auth test for Voice")
    parser.add_argument("--call-sid", required=True, help="Call SID from confirmation link")
    parser.add_argument("--token", required=True, help="Auth token from confirmation link")
    parser.add_argument("--base-url", default="https://voice.wren.ngrok.dev", help="Base URL for voice app")
    parser.add_argument("--wait-seconds", type=int, default=0,
                        help="Seconds to wait between device 1 and device 2 (use 310 to test past 5-min TTL)")

    args = parser.parse_args()

    print("=" * 60)
    print("MULTI-DEVICE AUTH TEST")
    print("=" * 60)
    print(f"\nThis test simulates:")
    print("  1. Device 1 (phone) opens link and confirms auth")
    print("  2. Wait {args.wait_seconds}s (simulating user switching devices)")
    print("  3. Device 2 (desktop) opens same link")
    print("\nExpected behavior: Both devices should work within 24h session")
    print(f"Bug behavior: Device 2 gets 401 after 5-min expires_at passes")

    results = run_multi_device_test(
        call_sid=args.call_sid,
        token=args.token,
        base_url=args.base_url,
        wait_seconds=args.wait_seconds,
    )

    sys.exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()
