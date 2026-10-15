"""
Farm AI - Two-line weather report + farming alerts
==================================================
Every sentence is chosen from REAL numbers in the weather dict returned by
utils.live_weather.get_live_weather(). Returns None / [] when data is missing,
so the app never shows an invented summary.

Thresholds are deliberately simple and conservative. Alerts are general
precautions, not agronomic prescriptions (no pesticide names or doses).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from i18n import t

HOT_C, WARM_C, COOL_C = 38, 32, 20
RAIN_LIKELY_PCT, RAIN_POSSIBLE_PCT = 60, 30
WINDY_KMH = 25

CONDITIONS = {
    "Clear":        {"en": "Clear sky", "te": "నిర్మలమైన ఆకాశం", "hi": "साफ़ आसमान"},
    "Clouds":       {"en": "Cloudy", "te": "మేఘావృతం", "hi": "बादल"},
    "Rain":         {"en": "Rain", "te": "వర్షం", "hi": "बारिश"},
    "Drizzle":      {"en": "Light rain", "te": "తేలికపాటి వర్షం", "hi": "हल्की बारिश"},
    "Thunderstorm": {"en": "Thunderstorm", "te": "ఉరుములతో వర్షం", "hi": "आंधी-तूफ़ान"},
    "Mist":         {"en": "Mist", "te": "మంచు పొగ", "hi": "धुंध"},
    "Haze":         {"en": "Haze", "te": "పొగమంచు", "hi": "धुंध"},
    "Fog":          {"en": "Fog", "te": "పొగమంచు", "hi": "कोहरा"},
    "Smoke":        {"en": "Smoky", "te": "పొగ", "hi": "धुआँ"},
    "Dust":         {"en": "Dusty", "te": "దుమ్ము", "hi": "धूल"},
}


def condition_text(main: str, lang: str) -> str:
    row = CONDITIONS.get(main)
    return (row.get(lang) or row["en"]) if row else main


def two_line_summary(w: dict, lang: str):
    """Return (line1, line2) or None if the weather data is not usable."""
    if not w or w.get("status") not in ("live", "stale") or w.get("temp_c") is None:
        return None
    temp = w["temp_c"]
    rain = w.get("rain_chance_pct")
    wind = w.get("wind_kmh") or 0

    if temp >= HOT_C:
        a = t("ws_temp_hot", lang)
    elif temp >= WARM_C:
        a = t("ws_temp_warm", lang)
    elif temp >= COOL_C:
        a = t("ws_temp_mild", lang)
    else:
        a = t("ws_temp_cool", lang)

    if rain is None:
        line1 = a + "."
    else:
        if rain >= RAIN_LIKELY_PCT:
            b = t("ws_rain_likely", lang)
        elif rain >= RAIN_POSSIBLE_PCT:
            b = t("ws_rain_possible", lang)
        else:
            b = t("ws_rain_none", lang)
        sep = ", " if lang != "hi" else ", "
        line1 = f"{a}{sep}{b}."

    # Line 2: one practical suggestion, in priority order
    if rain is not None and rain >= RAIN_POSSIBLE_PCT:
        line2 = t("ws_advice_rain", lang)
    elif wind >= WINDY_KMH:
        line2 = t("ws_advice_wind", lang)
    elif temp >= HOT_C:
        line2 = t("ws_advice_hot", lang)
    else:
        line2 = t("ws_advice_default", lang)
    return line1, line2


def alerts(w: dict, lang: str):
    """List of alert strings supported by the forecast. Empty list = nothing special."""
    if not w or w.get("status") not in ("live", "stale"):
        return []
    out = []
    days = []
    if w.get("today_forecast"):
        days.append(w["today_forecast"])
    days += w.get("forecast", [])
    if any(d.get("rain_mm", 0) >= 40 or (d.get("rain_chance_pct", 0) >= 80 and d.get("rain_mm", 0) >= 15) for d in days):
        out.append(t("alert_heavy_rain", lang))
    if any(d.get("temp_max", 0) >= 42 for d in days) or (w.get("temp_c") or 0) >= 42:
        out.append(t("alert_heat", lang))
    if any(d.get("wind_kmh_max", 0) >= 40 for d in days):
        out.append(t("alert_wind", lang))
    return out
