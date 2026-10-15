"""
Farm AI - Live weather for the farmer-facing app
================================================
Differences from utils/weather_api.py (which the 9 agents still use):

* NEVER returns made-up numbers. If the API cannot be reached the caller gets
  an explicit status, not mock data and not random() forecasts.
* Works per district (Telangana + Andhra Pradesh), chosen manually - no GPS.
* Every result carries `fetched_at` so the UI can show "last updated" and
  warn when data is old.
* Rain chance comes from the forecast's own probability-of-precipitation
  ("pop") field, not from extrapolating 1 hour of rain x 24.

Data source: OpenWeatherMap (https://openweathermap.org) - attribution is shown in the UI.
"""

import os
import time
import datetime
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:  # dotenv is optional
    pass

# (lat, lon, state, Telugu name, Hindi name)
DISTRICTS = {
    # Telangana
    "Hyderabad":     (17.385, 78.487, "TS", "హైదరాబాద్", "हैदराबाद"),
    "Warangal":      (17.977, 79.599, "TS", "వరంగల్", "वारंगल"),
    "Karimnagar":    (18.438, 79.133, "TS", "కరీంనగర్", "करीमनगर"),
    "Nizamabad":     (18.672, 78.094, "TS", "నిజామాబాద్", "निज़ामाबाद"),
    "Khammam":       (17.247, 80.151, "TS", "ఖమ్మం", "खम्मम"),
    "Nalgonda":      (17.057, 79.267, "TS", "నల్గొండ", "नलगोंडा"),
    "Adilabad":      (19.664, 78.532, "TS", "ఆదిలాబాద్", "आदिलाबाद"),
    "Mahbubnagar":   (16.737, 77.985, "TS", "మహబూబ్‌నగర్", "महबूबनगर"),
    "Medak":         (18.046, 78.263, "TS", "మెదక్", "मेदक"),
    "Siddipet":      (18.101, 78.852, "TS", "సిద్దిపేట", "सिद्दिपेट"),
    "Suryapet":      (17.140, 79.623, "TS", "సూర్యాపేట", "सूर्यापेट"),
    "Sangareddy":    (17.619, 78.081, "TS", "సంగారెడ్డి", "संगारेड्डी"),
    "Mancherial":    (18.870, 79.459, "TS", "మంచిర్యాల", "मंचेरियल"),
    # Andhra Pradesh
    "Visakhapatnam": (17.687, 83.219, "AP", "విశాఖపట్నం", "विशाखापत्तनम"),
    "Vijayawada":    (16.506, 80.648, "AP", "విజయవాడ", "विजयवाड़ा"),
    "Guntur":        (16.307, 80.437, "AP", "గుంటూరు", "गुंटूर"),
    "Tirupati":      (13.629, 79.419, "AP", "తిరుపతి", "तिरुपति"),
    "Kurnool":       (15.829, 78.037, "AP", "కర్నూలు", "कर्नूल"),
    "Anantapur":     (14.681, 77.600, "AP", "అనంతపురం", "अनंतपुर"),
    "Nellore":       (14.443, 79.987, "AP", "నెల్లూరు", "नेल्लोर"),
    "Kakinada":      (16.989, 82.247, "AP", "కాకినాడ", "काकीनाडा"),
    "Rajahmundry":   (17.000, 81.804, "AP", "రాజమహేంద్రవరం", "राजमहेंद्रवरम"),
    "Eluru":         (16.711, 81.095, "AP", "ఏలూరు", "एलुरु"),
    "Ongole":        (15.505, 80.050, "AP", "ఒంగోలు", "ओंगोल"),
    "Kadapa":        (14.467, 78.824, "AP", "కడప", "कडपा"),
    "Srikakulam":    (18.296, 83.897, "AP", "శ్రీకాకుళం", "श्रीकाकुलम"),
    "Machilipatnam": (16.187, 81.138, "AP", "మచిలీపట్నం", "मछलीपट्टनम"),
    "Vizianagaram":  (18.107, 83.396, "AP", "విజయనగరం", "विजयनगरम"),
}

CACHE_TTL_SECONDS = 30 * 60          # re-fetch after 30 minutes
STALE_WARN_MINUTES = 90              # warn in UI beyond this age
_cache = {}                          # district -> result dict


def district_label(name: str, lang: str) -> str:
    row = DISTRICTS.get(name)
    if not row or lang == "en":
        return name
    return row[3] if lang == "te" else row[4]


def api_key() -> str:
    return os.getenv("OPENWEATHER_API_KEY", "").strip()


def _local_date(ts: int, tz_offset: int) -> datetime.date:
    return (datetime.datetime.utcfromtimestamp(ts + tz_offset)).date()


def _fetch(district: str) -> dict:
    lat, lon = DISTRICTS[district][0], DISTRICTS[district][1]
    key = api_key()
    base = "https://api.openweathermap.org/data/2.5"
    cur = requests.get(f"{base}/weather", params={"lat": lat, "lon": lon, "appid": key, "units": "metric"}, timeout=8)
    if cur.status_code != 200:
        raise RuntimeError(f"current weather HTTP {cur.status_code}")
    fc = requests.get(f"{base}/forecast", params={"lat": lat, "lon": lon, "appid": key, "units": "metric"}, timeout=8)
    if fc.status_code != 200:
        raise RuntimeError(f"forecast HTTP {fc.status_code}")
    c, f = cur.json(), fc.json()

    tz = int(f.get("city", {}).get("timezone", c.get("timezone", 19800)))
    now_local = datetime.datetime.utcfromtimestamp(time.time() + tz)
    today = now_local.date()

    # Group the 3-hourly forecast by local date
    days = {}
    for item in f.get("list", []):
        d = _local_date(item["dt"], tz)
        days.setdefault(d, []).append(item)

    def day_summary(d, items):
        temps = [i["main"]["temp"] for i in items]
        pops = [i.get("pop", 0) for i in items]
        rain = sum(i.get("rain", {}).get("3h", 0) for i in items)
        mains = [i["weather"][0]["main"] for i in items]
        return {
            "date": d.isoformat(),
            "temp_max": round(max(temps), 1),
            "temp_min": round(min(temps), 1),
            "rain_chance_pct": round(max(pops) * 100),
            "rain_mm": round(rain, 1),
            "condition": max(set(mains), key=mains.count),
            "wind_kmh_max": round(max(i["wind"]["speed"] for i in items) * 3.6, 1),
        }

    daily = [day_summary(d, items) for d, items in sorted(days.items())]
    today_row = next((r for r in daily if r["date"] == today.isoformat()), None)
    # Today's high/low also consider the current reading
    cur_t = c["main"]["temp"]
    hi = lo = None
    if today_row:
        hi = round(max(today_row["temp_max"], cur_t), 1)
        lo = round(min(today_row["temp_min"], cur_t), 1)

    return {
        "ok": True,
        "district": district,
        "fetched_at": time.time(),
        "temp_c": round(cur_t, 1),
        "humidity_pct": c["main"]["humidity"],
        "condition": c["weather"][0]["main"],     # Clear / Clouds / Rain / ...
        "wind_kmh": round(c["wind"]["speed"] * 3.6, 1),
        "temp_high_c": hi,
        "temp_low_c": lo,
        "rain_chance_pct": today_row["rain_chance_pct"] if today_row else None,
        "forecast": [r for r in daily if r["date"] != today.isoformat()][:4],
        "today_forecast": today_row,
    }


def get_live_weather(district: str, force: bool = False) -> dict:
    """
    Returns a dict with key `status`:
      "live"            fresh data (fetched within the cache window)
      "stale"           the API failed but we hold older real data (see age_minutes)
      "not_configured"  no API key set
      "unavailable"     API failed and we hold nothing
    Numbers are only ever present when they came from the API.
    """
    if district not in DISTRICTS:
        return {"status": "unavailable"}
    if not api_key():
        return {"status": "not_configured"}

    cached = _cache.get(district)
    if cached and not force and time.time() - cached["fetched_at"] < CACHE_TTL_SECONDS:
        return {**cached, "status": "live", "age_minutes": int((time.time() - cached["fetched_at"]) / 60)}

    try:
        data = _fetch(district)
        _cache[district] = data
        return {**data, "status": "live", "age_minutes": 0}
    except Exception as e:  # network down, bad key, rate limit...
        print(f"[live_weather] fetch failed for {district}: {type(e).__name__}")  # no message: it can contain the API key in the URL
        if cached:
            age = int((time.time() - cached["fetched_at"]) / 60)
            return {**cached, "status": "stale", "age_minutes": age}
        return {"status": "unavailable"}


def format_time(ts: float) -> str:
    """Local India time, e.g. '3:45 PM'."""
    ist = datetime.datetime.utcfromtimestamp(ts + 19800)
    return ist.strftime("%I:%M %p").lstrip("0")
