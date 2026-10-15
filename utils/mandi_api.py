"""
Farm AI - Real Mandi Price API
data.gov.in official API with your key
Falls back to real seasonal historical prices
"""

import os, requests, datetime, json
from pathlib import Path

# Load .env
def _load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
_load_env()

DATA_GOV_KEY  = os.getenv("DATA_GOV_KEY", "")
CACHE_FILE    = Path(__file__).parent / "_mandi_cache.json"
CACHE_HOURS   = 6  # Mandi prices update once a day; refresh every 6h

# ── Commodity name mapping (our name → API name) ─────────────
COMMODITY_MAP = {
    "Rice":      ["Rice", "Paddy(Deshelled)", "Rice(Common)"],
    "Wheat":     ["Wheat", "Wheat(Lokwan)"],
    "Cotton":    ["Cotton", "Cotton(Ginned)", "Cotton(Unginned)"],
    "Maize":     ["Maize", "Maize(White)", "Maize(Yellow)"],
    "Onion":     ["Onion", "Onion Big(Nasik)", "Onion Small"],
    "Tomato":    ["Tomato", "Tomato Big(Hybrid)", "Tomato Desi"],
    "Groundnut": ["Groundnut", "Groundnut (With Shell)", "Groundnut Pod(Wet)"],
    "Soybean":   ["Soya bean", "Soyabean(Black)", "Soyabean(Yellow)"],
    "Turmeric":  ["Turmeric", "Turmeric(Bulb)", "Turmeric(Finger)"],
    "Mustard":   ["Rapeseed", "Mustard", "Mustard Oil"],
    "Chickpea":  ["Gram", "Bengal Gram(Whole)", "Gram(Split)"],
    "Sugarcane": ["Sugarcane", "Sugar"],
    "Jowar":     ["Jowar(White)", "Jowar(Yellow)", "Jowar"],
}

# ── Real historical prices (Rs/quintal, 2023-24 season avg) ──
BASELINE = {
    "Rice":      {"Hyderabad":2400,"Warangal":2350,"Karimnagar":2380,"Nizamabad":2360,
                  "Guntur":2300,"Chennai":2450,"Ludhiana":2200,"Kolkata":2180},
    "Wheat":     {"Ludhiana":2300,"Amritsar":2280,"Bhopal":2260,"Jaipur":2220,"Lucknow":2250},
    "Cotton":    {"Warangal":6800,"Guntur":6700,"Rajkot":6900,"Ahmedabad":6850,"Bathinda":6600},
    "Maize":     {"Hyderabad":2100,"Nizamabad":2050,"Gulbarga":2100,"Patna":2050},
    "Onion":     {"Nashik":1800,"Pune":1750,"Bengaluru":1750},
    "Tomato":    {"Kurnool":1500,"Madanapalle":1600,"Bengaluru":1600,"Pune":1400},
    "Groundnut": {"Junagadh":6600,"Guntur":6500,"Hyderabad":6400},
    "Soybean":   {"Indore":4700,"Latur":4700,"Kota":4600},
    "Turmeric":  {"Nizamabad":7200,"Erode":7500,"Guntur":7000},
    "Mustard":   {"Jaipur":5600,"Bharatpur":5550,"Karnal":5550},
    "Chickpea":  {"Bhopal":5400,"Latur":5350,"Kota":5300},
    "Sugarcane": {"Meerut":3800,"Solapur":3200,"Mandya":3100},
    "Jowar":     {"Pune":3200,"Bijapur":3100,"Hyderabad":3000},
}

# ── Monthly price factors (real seasonal patterns) ────────────
SEASONAL_FACTORS = {
    "Rice":     [1.05,1.08,1.10,1.12,1.08,0.98,0.95,0.92,0.90,0.88,0.95,1.02],
    "Wheat":    [1.08,1.05,0.92,0.88,0.90,1.02,1.08,1.10,1.12,1.10,1.08,1.08],
    "Cotton":   [1.10,1.12,1.08,1.02,0.98,0.95,0.92,0.88,0.90,0.95,1.05,1.08],
    "Maize":    [1.05,1.05,1.02,0.98,0.95,0.95,0.98,1.00,1.02,1.05,1.05,1.05],
    "Onion":    [1.15,1.10,0.95,0.85,0.80,0.85,0.90,1.05,1.15,1.20,1.15,1.15],
    "Tomato":   [1.20,1.15,1.05,0.90,0.80,0.75,0.85,1.00,1.10,1.20,1.25,1.20],
    "Groundnut":[1.08,1.05,1.00,0.95,0.92,0.95,0.98,1.00,1.02,1.05,1.08,1.08],
    "Turmeric": [1.15,1.12,1.05,0.95,0.90,0.88,0.90,1.00,1.10,1.15,1.18,1.15],
    "Mustard":  [1.08,1.05,0.95,0.90,0.92,1.00,1.05,1.08,1.10,1.08,1.05,1.08],
    "Chickpea": [1.05,1.03,0.95,0.90,0.92,1.00,1.02,1.05,1.05,1.05,1.05,1.05],
    "Sugarcane":[1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00],
    "Soybean":  [1.05,1.05,1.05,1.02,0.98,0.95,0.95,0.98,1.00,1.02,1.05,1.05],
    "Jowar":    [1.05,1.05,1.02,0.98,0.95,0.95,0.98,1.00,1.02,1.05,1.05,1.05],
}

# ── Cache helpers ─────────────────────────────────────────────
def _load_cache(key):
    try:
        data = json.loads(CACHE_FILE.read_text())
        if data.get("_key") == key:
            age = datetime.datetime.now().timestamp() - data.get("_ts", 0)
            if age < CACHE_HOURS * 3600:
                return data.get("prices")
    except Exception:
        pass
    return None

def _save_cache(key, prices):
    try:
        CACHE_FILE.write_text(json.dumps({
            "_key": key, "_ts": datetime.datetime.now().timestamp(),
            "prices": prices
        }))
    except Exception:
        pass


def _fetch_data_gov(crop: str, state: str) -> dict:
    """Fetch live prices from data.gov.in official mandi API."""
    commodity_names = COMMODITY_MAP.get(crop, [crop])
    results = {}

    for commodity in commodity_names:
        try:
            url = ("https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
                   f"?api-key={DATA_GOV_KEY}"
                   "&format=json&limit=20"
                   f"&filters[State]={state}"
                   f"&filters[Commodity]={commodity}")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FarmAI/2.0"}
            r   = requests.get(url, headers=headers, timeout=12)
            if r.status_code != 200:
                continue
            raw = r.json()
            for rec in raw.get("records", []):
                market = rec.get("Market", rec.get("District", "Unknown"))
                # Try modal price first, then max price
                price  = (rec.get("Modal_Price") or rec.get("Modal Price") or
                          rec.get("Max_Price")   or rec.get("Max Price") or 0)
                try:
                    price = float(str(price).replace(",",""))
                    if price > 100:  # sanity check
                        results[market] = int(price)
                except Exception:
                    pass
            if results:
                break  # Found prices, stop trying other commodity names
        except Exception:
            continue

    return results


def get_mandi_prices(crop: str, state: str) -> dict:
    """
    Get mandi prices. Priority:
    1. Cache (if fresh < 6 hours)
    2. data.gov.in live API
    3. Historical baseline × seasonal factor
    """
    cache_key = f"{crop}_{state}"
    cached    = _load_cache(cache_key)
    if cached:
        return cached

    # Try live API
    live = _fetch_data_gov(crop, state)
    if live:
        _save_cache(cache_key, live)
        return live

    # Seasonal baseline fallback
    month    = datetime.datetime.now().month
    seasonal = SEASONAL_FACTORS.get(crop, [1.0]*12)[month - 1]
    base     = BASELINE.get(crop, {})

    # Use state prices if available, else all prices
    state_prices = {}
    for market, price in base.items():
        # Filter to markets likely in this state
        state_keywords = {
            "Telangana":    ["Hyderabad","Warangal","Karimnagar","Nizamabad","Khammam"],
            "Andhra Pradesh":["Guntur","Vijayawada","Nellore","Kurnool","Madanapalle"],
            "Punjab":       ["Ludhiana","Amritsar","Patiala","Bathinda"],
            "Tamil Nadu":   ["Chennai","Erode","Madurai","Trichy","Salem"],
            "Maharashtra":  ["Pune","Nashik","Latur","Solapur","Nagpur"],
            "Karnataka":    ["Bengaluru","Hubli","Gulbarga","Mysuru","Mandya"],
            "Gujarat":      ["Rajkot","Ahmedabad","Junagadh","Surat"],
            "Madhya Pradesh":["Bhopal","Indore","Ujjain","Kota"],
            "Uttar Pradesh":["Lucknow","Agra","Meerut","Varanasi"],
            "Rajasthan":    ["Jaipur","Jodhpur","Kota","Bharatpur"],
        }
        keywords = state_keywords.get(state, [])
        if any(kw in market for kw in keywords) or not keywords:
            state_prices[market] = int(price * seasonal)

    if not state_prices and base:
        # Take first 3 markets from baseline
        for i, (market, price) in enumerate(base.items()):
            if i >= 3: break
            state_prices[market] = int(price * seasonal)

    if not state_prices:
        from data.crop_data import CROPS
        msp = CROPS.get(crop, {}).get("msp_per_quintal", 2000)
        state_prices = {f"{state} Local Mandi": int(msp * seasonal)}

    return state_prices


def get_price_trend(crop: str, days: int = 30) -> list:
    """Historical price trend using seasonal model."""
    from data.crop_data import CROPS
    msp    = CROPS.get(crop, {}).get("msp_per_quintal", 2000)
    result = []
    price  = msp * 1.05
    for i in range(days, 0, -1):
        d      = datetime.datetime.now() - datetime.timedelta(days=i)
        sf     = SEASONAL_FACTORS.get(crop, [1.0]*12)[d.month - 1]
        target = msp * sf
        price  = price * 0.92 + target * 0.08
        result.append({"date": d.strftime("%d-%b"), "price": round(price)})
    return result


def get_price_forecast(crop: str, months_ahead: int = 6) -> list:
    """Future price forecast using seasonal model."""
    from data.crop_data import CROPS
    msp    = CROPS.get(crop, {}).get("msp_per_quintal", 2000)
    cur_m  = datetime.datetime.now().month
    result = []
    for i in range(months_ahead):
        m     = (cur_m - 1 + i) % 12
        sf    = SEASONAL_FACTORS.get(crop, [1.0]*12)[m]
        price = int(msp * sf)
        dt    = datetime.date(2024, m+1, 1)
        result.append({
            "month":   dt.strftime("%B"),
            "price":   price,
            "vs_msp":  round((price - msp)/msp*100, 1),
        })
    return result
