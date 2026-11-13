"""
Farm AI - Real Weather API (Multi-Tier Zero-Config)
====================================================
OpenWeatherMap: LIVE data when OPENWEATHER_API_KEY is set
Open-Meteo:     LIVE data automatically when no key is set (100% free)
Agro-climatic:  Offline seasonal model if no internet connection
"""

import os, requests, datetime, random, json, math
from pathlib import Path

# ── .env loader ───────────────────────────────────────────────
def _load_env():
    candidates = [
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent.parent / ".env",
        Path.cwd() / ".env",
        Path.cwd() / "farm_ai" / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
            break

_load_env()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
DEMO_MODE       = os.getenv("DEMO_MODE", "false").strip().lower() == "true"
CACHE_FILE      = Path(__file__).parent / "_weather_cache.json"

# ── City coordinates ──────────────────────────────────────────
CITY_COORDS = {
    "Hyderabad":          (17.385,  78.487), "Warangal":    (17.977, 79.599),
    "Karimnagar":         (18.438,  79.133), "Nizamabad":   (18.671, 78.094),
    "Visakhapatnam":      (17.687,  83.219), "Vijayawada":  (16.506, 80.648),
    "Guntur":             (16.307,  80.437), "Tirupati":    (13.629, 79.419),
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
    "Telangana":        "Hyderabad",   "Andhra Pradesh":    "Vijayawada",
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

# ── Cache helpers (30 minutes) ─────────────────────────────────
def _load_cache(city: str) -> dict:
    try:
        data = json.loads(CACHE_FILE.read_text())
        if data.get("_city") == city:
            age = datetime.datetime.now().timestamp() - data.get("_ts", 0)
            if age < 1800:
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


def _wmo_condition(code: int) -> tuple:
    if code == 0:
        return "Clear Sky", "Clear"
    if code in (1, 2, 3):
        return "Partly Cloudy", "Clouds"
    if code in (45, 48):
        return "Foggy", "Fog"
    if code in (51, 53, 55, 56, 57):
        return "Light Drizzle", "Rain"
    if code in (61, 63, 65, 80, 81, 82):
        return "Rain Showers", "Rain"
    if code in (95, 96, 99):
        return "Thunderstorm", "Thunderstorm"
    return "Cloudy", "Clouds"


# ── Live Open-Meteo fetch (Zero API key required) ──────────────
def _fetch_open_meteo(lat: float, lon: float) -> dict:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,surface_pressure,cloud_cover&daily=precipitation_sum,temperature_2m_max,temperature_2m_min&timezone=auto"
    r = requests.get(url, timeout=8)
    if r.status_code != 200:
        raise RuntimeError(f"Open-Meteo HTTP {r.status_code}")
    res = r.json()
    curr = res.get("current", {})
    daily = res.get("daily", {})
    code = int(curr.get("weather_code", 0))
    desc, icon = _wmo_condition(code)

    clouds = int(curr.get("cloud_cover", 20))
    uv = 6.0
    solar_rad = round(max(5.0, (1 - clouds / 100) * 25 + uv * 0.5), 1)
    rain_today = float(daily["precipitation_sum"][0]) if daily.get("precipitation_sum") else 0.0

    return {
        "temperature_c":  round(float(curr.get("temperature_2m", 27.0)), 1),
        "feels_like_c":   round(float(curr.get("temperature_2m", 27.0)), 1),
        "humidity_pct":   int(curr.get("relative_humidity_2m", 55)),
        "pressure_hpa":   round(float(curr.get("surface_pressure", 1012))),
        "rainfall_mm":    round(rain_today, 1),
        "wind_kmh":       round(float(curr.get("wind_speed_10m", 10.0)), 1),
        "wind_dir_deg":   180,
        "cloud_pct":      clouds,
        "visibility_km":  10.0,
        "description":    desc,
        "icon":           icon,
        "uv_index":       round(uv, 1),
        "solar_rad":      solar_rad,
        "source":         "Open-Meteo LIVE 🌤️",
        "is_live":        True,
    }


# ── Season-aware realistic mock (fallback when offline) ────────
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
        "source":         "Agro-climatic seasonal model 🌾",
        "is_live":        False,
    }


def get_weather(state: str = "Telangana", city: str = None) -> dict:
    """
    Returns live weather using OpenWeather (if key set) or Open-Meteo (zero key required).
    Falls back to realistic seasonal model if offline.
    """
    city   = city or STATE_CITIES.get(state, "Hyderabad")
    coords = CITY_COORDS.get(city) or CITY_COORDS["Hyderabad"]

    if DEMO_MODE:
        data = _mock(state)
        data.update({"city": city, "state": state})
        return data

    cached = _load_cache(city)
    if cached and "temperature_c" in cached:
        return cached

    # 1. Try OpenWeatherMap if key is present
    key = os.getenv("OPENWEATHER_API_KEY", "").strip() or OPENWEATHER_KEY
    if key and coords:
        try:
            data = _fetch_live(*coords)
            data.update({"city": city, "state": state})
            _save_cache(city, data)
            return data
        except Exception:
            pass

    # 2. Try Open-Meteo (Zero key required, free & live)
    if coords:
        try:
            data = _fetch_open_meteo(*coords)
            data.update({"city": city, "state": state})
            _save_cache(city, data)
            return data
        except Exception:
            pass

    # 3. Fall back to seasonal model
    data = _mock(state)
    data.update({"city": city, "state": state})
    return data


def get_7day_forecast(state: str = "Telangana") -> list:
    """7-day forecast from OpenWeather, Open-Meteo or seasonal model."""
    city   = STATE_CITIES.get(state, "Hyderabad")
    coords = CITY_COORDS.get(city) or CITY_COORDS["Hyderabad"]

    key = os.getenv("OPENWEATHER_API_KEY", "").strip() or OPENWEATHER_KEY

    # 1. Try OpenWeatherMap if key is available
    if not DEMO_MODE and key and coords:
        try:
            url = (f"https://api.openweathermap.org/data/2.5/forecast"
                   f"?lat={coords[0]}&lon={coords[1]}"
                   f"&appid={key}&units=metric&cnt=40")
            r = requests.get(url, timeout=8)
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
                if len(result) >= 5:
                    return result[:7]
        except Exception:
            pass

    # 2. Try Open-Meteo (Zero key required, free & live 7-day forecast)
    if not DEMO_MODE and coords:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum&timezone=auto"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                daily = r.json().get("daily", {})
                times = daily.get("time", [])
                result = []
                for i in range(min(7, len(times))):
                    dt = datetime.datetime.strptime(times[i], "%Y-%m-%d")
                    desc, _ = _wmo_condition(int(daily["weather_code"][i]))
                    result.append({
                        "date":         dt.strftime("%a %d %b"),
                        "rainfall_mm":  round(float(daily["precipitation_sum"][i]), 1),
                        "temp_max":     round(float(daily["temperature_2m_max"][i]), 1),
                        "temp_min":     round(float(daily["temperature_2m_min"][i]), 1),
                        "humidity_pct": 50.0,
                        "description":  desc,
                        "is_live":      True,
                    })
                if len(result) >= 5:
                    return result[:7]
        except Exception:
            pass

    # 3. Fallback mock 7-day
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
    key = os.getenv("OPENWEATHER_API_KEY", "").strip() or OPENWEATHER_KEY
    return {
        "key_set":     bool(key),
        "key_preview": f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "(empty)",
        "demo_mode":   DEMO_MODE,
        "provider":    "OpenWeatherMap" if key else "Open-Meteo (Zero-Config LIVE)",
    }
