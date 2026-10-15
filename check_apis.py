"""
Run:  python check_apis.py
Tests the 3 Farm AI APIs (OpenWeather, data.gov.in, Gemini) and prints
WORKING / NOT WORKING for each, with the reason.
"""
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from utils.api_health import check_all

ICON = {"working": "[ OK ]", "no_key": "[ -- ]", "key_rejected": "[FAIL]",
        "rate_limited": "[WAIT]", "network_error": "[NET ]", "error": "[FAIL]"}

if __name__ == "__main__":
    print("\nFarm AI - API check\n" + "=" * 50)
    results = check_all()
    for r in results:
        print(f"{ICON.get(r['state'], '[?]')} {r['name']:<12} {r['state']:<14} {r['detail']}  ({r['ms']} ms)")
    print("=" * 50)
    bad = [r["name"] for r in results if not r["ok"]]
    print("All 3 APIs are working." if not bad else "Not working: " + ", ".join(bad) + "  -> send me the line above and I will fix it.")
    sys.exit(0 if not bad else 1)
