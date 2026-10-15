"""
Farm AI - Real API health check (additive module)
=================================================
Calls each of the 3 external APIs once and reports honestly whether it works.
(The old sidebar only checked that a key *existed*, which is not the same as
the API actually answering.)

APIs:  1. OpenWeatherMap   (live weather)
       2. data.gov.in      (live mandi prices)
       3. Google Gemini    (leaf doctor + help chatbot)

Each result:  {"name", "state", "ok", "detail", "ms"}
  state = working | no_key | key_rejected | rate_limited | network_error | error
API keys are never included in the returned text.
"""

import os, time
import requests

try:
    from dotenv import load_dotenv
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(_root, ".env"))
except Exception:
    pass

TIMEOUT = 12


def _result(name, state, detail, t0):
    return {"name": name, "state": state, "ok": state == "working",
            "detail": detail, "ms": int((time.time() - t0) * 1000)}


def _classify(name, r, t0, ok_detail):
    if r.status_code == 200:
        return _result(name, "working", ok_detail, t0)
    if r.status_code in (401, 403) or (name == "Gemini" and r.status_code == 400):
        return _result(name, "key_rejected", f"HTTP {r.status_code} - the API key was rejected. Create a new key.", t0)
    if r.status_code == 429:
        return _result(name, "rate_limited", "HTTP 429 - daily/minute limit reached. Try later.", t0)
    return _result(name, "error", f"HTTP {r.status_code}", t0)


def check_openweather() -> dict:
    name, t0 = "OpenWeather", time.time()
    key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not key:
        return _result(name, "no_key", "OPENWEATHER_API_KEY missing in .env", t0)
    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather",
                         params={"lat": 17.385, "lon": 78.487, "appid": key, "units": "metric"}, timeout=TIMEOUT)
        if r.status_code == 200:
            return _result(name, "working", f"Hyderabad now {r.json()['main']['temp']} C", t0)
        return _classify(name, r, t0, "")
    except requests.RequestException as e:
        return _result(name, "network_error", f"No connection ({type(e).__name__})", t0)
    except Exception as e:
        return _result(name, "error", type(e).__name__, t0)


def check_mandi() -> dict:
    name, t0 = "data.gov.in", time.time()
    key = os.getenv("DATA_GOV_KEY", "").strip()
    if not key:
        return _result(name, "no_key", "DATA_GOV_KEY missing in .env", t0)
    try:
        r = requests.get("https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
                         params={"api-key": key, "format": "json", "limit": 1},
                         headers={"User-Agent": "FarmAI/2.0"}, timeout=TIMEOUT)
        if r.status_code == 200:
            n = len(r.json().get("records", []))
            return _result(name, "working", f"Mandi API answered ({n} record returned)", t0)
        return _classify(name, r, t0, "")
    except requests.RequestException as e:
        return _result(name, "network_error", f"No connection ({type(e).__name__})", t0)
    except Exception as e:
        return _result(name, "error", type(e).__name__, t0)


def check_gemini() -> dict:
    name, t0 = "Gemini", time.time()
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return _result(name, "no_key", "GEMINI_API_KEY missing in .env", t0)
    try:
        # Listing models needs the key but uses no generation quota.
        r = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                         params={"key": key, "pageSize": 5}, timeout=TIMEOUT)
        if r.status_code == 200:
            return _result(name, "working", "Gemini key accepted", t0)
        return _classify(name, r, t0, "")
    except requests.RequestException as e:
        return _result(name, "network_error", f"No connection ({type(e).__name__})", t0)
    except Exception as e:
        return _result(name, "error", type(e).__name__, t0)


def check_all() -> list:
    return [check_openweather(), check_mandi(), check_gemini()]
