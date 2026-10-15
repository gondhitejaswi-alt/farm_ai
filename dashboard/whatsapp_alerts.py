"""
Farm AI - WhatsApp / SMS Morning Alert System
Sends 6AM farm advisory to farmers
Cost: Rs 0.50 per message via Twilio
"""
import os, sys, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents.irrigation_agent  import IrrigationAgent
from agents.pest_agent         import PestAgent
from agents.yield_agent        import YieldAgent
from agents.fertilizer_agent   import FertilizerAgent
from utils.weather_api         import get_weather
from utils.helpers             import format_rupees

try:
    from twilio.rest import Client
    TWILIO_OK = True
except ImportError:
    TWILIO_OK = False


def build_message(config: dict) -> str:
    name   = config.get("farmer_name", "Farmer")
    crop   = config.get("crop", "Rice")
    state  = config.get("state", "Telangana")
    acres  = config.get("acres", 5)
    ph     = config.get("soil_ph", 6.5)
    n      = config.get("nitrogen", 100)
    p      = config.get("phosphorus", 50)
    k      = config.get("potassium", 35)
    stage  = config.get("growth_stage", "vegetative")
    moist  = config.get("soil_moisture_pct", 55)

    wx     = get_weather(state)
    temp   = wx["temperature_c"]; hum = wx["humidity_pct"]; rain = wx["rainfall_mm"]

    irr    = IrrigationAgent().analyze(crop, moist, rain, temp, hum, stage, 80, acres)
    pest   = PestAgent().analyze(crop, temp, hum, rain, stage, [], acres)
    yld    = YieldAgent().analyze(state, crop, acres, ph, n, p, k, 900, temp, hum)
    fert   = FertilizerAgent().analyze(crop, acres, n, p, k, ph)

    today  = datetime.datetime.now().strftime("%d %b %Y")
    saved  = irr.get("money_saved_today", 0) + fert.get("money_saved", 0)

    lines = [
        f"FARM AI - {today}",
        f"Namaste {name}!",
        "",
        f"Weather: {temp}C | Rain {rain}mm | Humidity {hum}%",
        "",
        f"WATER: {irr['decision']}",
        f"  {irr['tip']}",
        "",
        f"PEST ({pest.get('alert_level', 'LOW')}): {pest.get('top_threat', 'None')} {pest.get('top_threat_risk', pest.get('confidence_pct', 0))}% risk",
        f"  {pest.get('immediate_action', pest.get('action', 'Monitor crop'))}",
        "",
        f"YIELD: {yld['yield_per_acre_kg']:,} kg/acre = {format_rupees(yld['expected_revenue'])}",
        "",
        f"FERTILIZER: {fert['action']}",
        "",
        f"TODAY YOU SAVE: {format_rupees(saved)}",
        "",
        "Farm AI - Helping farmers earn more",
    ]
    return "\n".join(lines)


def send_whatsapp(phone: str, message: str) -> bool:
    if not TWILIO_OK:
        print("Install twilio: pip install twilio"); return False
    sid   = os.getenv("TWILIO_ACCOUNT_SID","")
    token = os.getenv("TWILIO_AUTH_TOKEN","")
    from_ = os.getenv("TWILIO_WHATSAPP_FROM","whatsapp:+14155238886")
    if not sid or not token:
        print("Set TWILIO keys in .env"); return False
    try:
        c = Client(sid, token)
        c.messages.create(body=message, from_=from_, to=f"whatsapp:{phone}")
        print(f"Sent to {phone}"); return True
    except Exception as e:
        print(f"Failed: {e}"); return False


def demo_alert(config: dict = None):
    cfg = config or {
        "farmer_name": "Raju", "crop": "Rice", "state": "Telangana",
        "acres": 5, "soil_ph": 6.5, "nitrogen": 90,
        "phosphorus": 45, "potassium": 35,
        "soil_moisture_pct": 55, "growth_stage": "vegetative",
    }
    msg = build_message(cfg)
    print("\n" + "="*55)
    print("  6 AM WHATSAPP ALERT PREVIEW")
    print("="*55)
    print(msg)
    print("="*55)
    print(f"\nLength: {len(msg)} chars | Cost: Rs 0.50 per farmer")
    return msg


DEMO_FARMERS = [
    {"farmer_name":"Raju","phone":"+91XXXXXXXXXX","crop":"Rice",
     "state":"Telangana","acres":5,"soil_ph":6.5,"nitrogen":90,"phosphorus":45,"potassium":35},
    {"farmer_name":"Suresh","phone":"+91XXXXXXXXXX","crop":"Cotton",
     "state":"Telangana","acres":10,"soil_ph":7.0,"nitrogen":80,"phosphorus":40,"potassium":40},
]

if __name__ == "__main__":
    demo_alert(DEMO_FARMERS[0])
