"""
Farm AI - Real Weather API
OpenWeatherMap: LIVE data when OPENWEATHER_API_KEY is set
Realistic seasonal mock: fallback when offline or no key
"""

import os, requests, datetime, random, json, math
from pathlib import Path

# ── .env loader — MUST run before reading any env var ─────────
def _load_env():
    """
    Search for .env in multiple locations so it works regardless
    of which directory you run streamlit from.
    """
    candidates = [
        Path(__file__).parent.parent / ".env",          # farm_ai/.env  (correct)
        Path(__file__).parent.parent.parent / ".env",   # one level up
        Path.cwd() / ".env",                            # wherever you run from
        Path.cwd() / "farm_ai" / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                # Use setdefault so shell env vars take priority
                os.environ.setdefault(k, v)
            break  # stop after first found .env

_load_env()

# Read key AFTER _load_env() has run
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
DEMO_MODE       = os.getenv("DEMO_MODE", "false").strip().lower() == "true"

CACHE_FILE = Path(__file__).parent / "_weather_cache.json"

# ── City coordinates ──────────────────────────────────────────
CITY_COORDS = {
    "Hyderabad":          (17.385,  78.487), "Warangal":    (17.977, 79.599),
    "Karimnagar":         (18.438,  79.133), "Nizamabad":   (18.671, 78.094),
    "Chennai":            (13.083,  80.270), "Coimbatore":  (11.017, 76.967),
    "Ludhiana":           (30.901,  75.857), "Amritsar":    (31.634, 74.873),
    "Pune":               (18.521,  73.857), "Nashik":      (19.997, 73.790),
    "Bengaluru":          (12.972,  77.594), "Mysuru":      (12.303, 76.655),
    "Bhopal":             (23.259,  77.413), "Indore":      (22.719, 75.857),
    "Patna":              (25.594,  85.137), "Ranchi":      (23.344, 85.310),
    "Kolkata":            (22.572,  88.364), "Bhubaneswar": (20.296, 85.825),
    "Jaipur":             (26.912,  75.787), "Ahmedabad":   (23.023, 72.572),
    "Lucknow":            (26.850,  80.949), "Guwahati":    (26.144, 91.736),
    "Thiruvananthapuram": ( 8.524,  76.936), "Kochi":       ( 9.931, 76.267),
    "Shillong":           (25.574,  91.882), "Dehradun":    (30.317, 78.032),
    "Chandigarh":         (30.733,  76.779), "Raipur":      (21.251, 81.629),
    "Jodhpur":            (26.292,  73.023), "Varanasi":    (25.317, 83.013),
}

STATE_CITIES = {
    "Telangana":        "Hyderabad",   "Andhra Pradesh":    "Hyderabad",
    "Tamil Nadu":       "Chennai",     "Punjab":            "Ludhiana",
    "Maharashtra":      "Pune",        "Karnataka":         "Bengaluru",
    "West Bengal":      "Kolkata",     "Bihar":             "Patna",
    "Rajasthan":        "Jaipur",      "Gujarat":           "Ahmedabad",
    "Uttar Pradesh":    "Lucknow",     "Madhya Pradesh":    "Bhopal",
    "Odisha":           "Bhubaneswar", "Jharkhand":         "Ranchi",
    "Chhattisgarh":     "Raipur",      "Haryana":           "Chandigarh",
    "Himachal Pradesh": "Dehradun",    "Uttarakhand":       "Dehradun",
    "Assam":            "Guwahati",    "Kerala":            "Kochi",
    "Meghalaya":        "Shillong",    "Arunachal Pradesh": "Guwahati",
}

# ── Cache helpers (1 hour) ─────────────────────────────────────
def _load_cache(city: str) -> dict:
    try:
        data = json.loads(CACHE_FILE.read_text())
        if data.get("_city") == city:
            age = datetime.datetime.now().timestamp() - data.get("_ts", 0)
            if age < 3600:
                return data
    except Exception:
        pass
    return {}

def _save_cache(city: str, data: dict):
    try:
        CACHE_FILE.write_text(json.dumps({**data, "_city": city,
                                          "_ts": datetime.datetime.now().timestamp()}))
    except Exception:
        pass

# ── Live OpenWeatherMap fetch ─────────────────────────────────
def _fetch_live(lat: float, lon: float) -> dict:
    url = (f"https://api.openweathermap.org/data/2.5/weather"
           f"?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=metric")
    r = requests.get(url, timeout=8)
    if r.status_code == 401:
        raise Exception("Invalid API key — check OPENWEATHER_API_KEY in .env")
    if r.status_code != 200:
        raise Exception(f"API returned {r.status_code}: {r.text[:120]}")
    d = r.json()

    # UV index (best-effort, may not be available on free plan)
    uv = 6.0
    try:
        uv_r = requests.get(
            f"https://api.openweathermap.org/data/2.5/uvi"
            f"?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}", timeout=5)
        if uv_r.status_code == 200:
            uv = float(uv_r.json().get("value", 6))
    except Exception:
        pass

    clouds    = d["clouds"]["all"]
    solar_rad = round(max(5.0, (1 - clouds / 100) * 25 + uv * 0.5), 1)

    return {
        "temperature_c":  round(d["main"]["temp"], 1),
        "feels_like_c":   round(d["main"]["feels_like"], 1),
        "humidity_pct":   d["main"]["humidity"],
        "pressure_hpa":   d["main"]["pressure"],
        "rainfall_mm":    round(d.get("rain", {}).get("1h", 0) * 24, 1),
        "wind_kmh":       round(d["wind"]["speed"] * 3.6, 1),
        "wind_dir_deg":   d["wind"].get("deg", 180),
        "cloud_pct":      clouds,
        "visibility_km":  round(d.get("visibility", 10000) / 1000, 1),
        "description":    d["weather"][0]["description"].title(),
        "icon":           d["weather"][0]["main"],
        "uv_index":       round(uv, 1),
        "solar_rad":      solar_rad,
        "source":         "OpenWeatherMap LIVE ✅",
        "is_live":        True,
    }

# ── Season-aware realistic mock ───────────────────────────────
def _mock(state: str) -> dict:
    month      = datetime.datetime.now().month
    is_monsoon = 6 <= month <= 9
    is_winter  = month in [11, 12, 1, 2]
    BASE = {
        "Telangana": 32, "Andhra Pradesh": 31, "Tamil Nadu": 30,
        "Punjab": 23,    "Haryana": 24,         "Uttar Pradesh": 26,
        "Madhya Pradesh": 27, "Maharashtra": 28, "Gujarat": 30,
        "West Bengal": 27,    "Odisha": 29,       "Bihar": 27,
        "Karnataka": 28,      "Kerala": 29,       "Rajasthan": 34,
        "Himachal Pradesh": 18, "Uttarakhand": 20, "Assam": 26,
        "Jharkhand": 27,      "Chhattisgarh": 28, "Meghalaya": 20,
    }
    base    = BASE.get(state, 28) - (8 if is_winter else 0)
    temp    = round(base + random.uniform(-2, 2), 1)
    hum     = round(random.uniform(76, 93) if is_monsoon else random.uniform(42, 68), 1)
    rain    = round(random.uniform(4, 28)  if is_monsoon else random.uniform(0, 2),   1)
    wind    = round(random.uniform(8, 20), 1)
    clouds  = random.randint(50, 90) if is_monsoon else random.randint(10, 50)
    solar   = round(max(8, (1 - clouds / 100) * 24 + random.uniform(2, 6)), 1)
    return {
        "temperature_c":  temp,
        "feels_like_c":   round(temp + (hum - 50) * 0.02, 1),
        "humidity_pct":   hum,
        "pressure_hpa":   round(random.uniform(1005, 1015)),
        "rainfall_mm":    rain,
        "wind_kmh":       wind,
        "wind_dir_deg":   random.randint(0, 359),
        "cloud_pct":      clouds,
        "visibility_km":  round(random.uniform(6, 15), 1),
        "description":    "Monsoon showers" if is_monsoon else "Partly cloudy",
        "icon":           "Rain" if is_monsoon else "Clear",
        "uv_index":       round(random.uniform(4, 10), 1),
        "solar_rad":      solar,
        "source":         "Realistic mock — set OPENWEATHER_API_KEY in .env for live data",
        "is_live":        False,
    }


def get_weather(state: str = "Telangana", city: str = None) -> dict:
    """
    Returns live weather if OPENWEATHER_API_KEY is set and valid.
    Falls back to realistic seasonal mock otherwise.
    Caches live data for 1 hour so API quota is not wasted.
    """
    city   = city or STATE_CITIES.get(state, "Hyderabad")
    coords = CITY_COORDS.get(city)

    # Force mock in demo mode
    if DEMO_MODE:
        data = _mock(state)
        data.update({"city": city, "state": state})
        return data

    # Try cache first
    cached = _load_cache(city)
    if cached and "temperature_c" in cached:
        return cached

    # Try live API if key is present
    if OPENWEATHER_KEY and coords:
        try:
            data = _fetch_live(*coords)
            data.update({"city": city, "state": state})
            _save_cache(city, data)
            return data
        except Exception as e:
            # Print to terminal so developer sees what went wrong
            print(f"[WeatherAPI] ⚠️  Live fetch failed: {e}  → using mock data")

    # Fall back to mock
    data = _mock(state)
    data.update({"city": city, "state": state})
    return data


def get_7day_forecast(state: str = "Telangana") -> list:
    """7-day forecast — live from OpenWeatherMap or seasonal mock."""
    city   = STATE_CITIES.get(state, "Hyderabad")
    coords = CITY_COORDS.get(city)

    if not DEMO_MODE and OPENWEATHER_KEY and coords:
        try:
            url = (f"https://api.openweathermap.org/data/2.5/forecast"
                   f"?lat={coords[0]}&lon={coords[1]}"
                   f"&appid={OPENWEATHER_KEY}&units=metric&cnt=40")
            r   = requests.get(url, timeout=8)
            if r.status_code == 200:
                days = {}
                for item in r.json().get("list", []):
                    d = item["dt_txt"][:10]
                    days.setdefault(d, []).append(item)
                result = []
                for d, items in list(days.items())[:7]:
                    temps = [i["main"]["temp"] for i in items]
                    rain  = sum(i.get("rain", {}).get("3h", 0) for i in items)
                    hums  = [i["main"]["humidity"] for i in items]
                    dt    = datetime.datetime.strptime(d, "%Y-%m-%d")
                    result.append({
                        "date":         dt.strftime("%a %d %b"),
                        "rainfall_mm":  round(rain, 1),
                        "temp_max":     round(max(temps), 1),
                        "temp_min":     round(min(temps), 1),
                        "humidity_pct": round(sum(hums) / len(hums), 1),
                        "description":  items[0]["weather"][0]["description"].title(),
                        "is_live":      True,
                    })
                if result:
                    while len(result) < 7:
                        last = result[-1]
                        next_dt = datetime.datetime.now() + datetime.timedelta(days=len(result))
                        result.append({
                            "date":         next_dt.strftime("%a %d %b"),
                            "rainfall_mm":  last["rainfall_mm"],
                            "temp_max":     last["temp_max"],
                            "temp_min":     last["temp_min"],
                            "humidity_pct": last["humidity_pct"],
                            "description":  last["description"],
                            "is_live":      True,
                        })
                    return result[:7]
        except Exception as e:
            print(f"[ForecastAPI] ⚠️  {e}  → using mock forecast")

    # Mock 7-day
    w = get_weather(state)
    mon = datetime.datetime.now().month
    return [{
        "date":         (datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%a %d %b"),
        "rainfall_mm":  round(random.uniform(3, 25) if 6 <= mon <= 9 else random.uniform(0, 2), 1),
        "temp_max":     round(w["temperature_c"] + random.uniform(1, 4), 1),
        "temp_min":     round(w["temperature_c"] - random.uniform(4, 8), 1),
        "humidity_pct": round(w["humidity_pct"] + random.uniform(-5, 5), 1),
        "description":  w["description"],
        "is_live":      False,
    } for i in range(7)]


def debug_api_status() -> dict:
    """Call this to see exactly why live/mock is being used."""
    key = OPENWEATHER_KEY
    return {
        "key_set":        bool(key),
        "key_preview":    f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "(empty)",
        "demo_mode":      DEMO_MODE,
        "env_file_found": any(
            (Path(__file__).parent.parent / ".env").exists(),
            (Path.cwd() / ".env").exists(),
        ) if False else str([
            str(p) for p in [
                Path(__file__).parent.parent / ".env",
                Path.cwd() / ".env",
                Path.cwd() / "farm_ai" / ".env",
            ] if p.exists()
        ]),
    }


if __name__ == "__main__":
    print("=== API Status ===")
    print(f"Key set: {bool(OPENWEATHER_KEY)}")
    print(f"Key: {OPENWEATHER_KEY[:8]}..." if OPENWEATHER_KEY else "Key: (not set)")
    print(f"Demo mode: {DEMO_MODE}")
    w = get_weather("Telangana")
    print(f"\nWeather source: {w['source']}")
    print(f"Is live: {w['is_live']}")
    print(f"Temp: {w['temperature_c']}°C, Humidity: {w['humidity_pct']}%")
