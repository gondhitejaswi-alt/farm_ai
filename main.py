"""
Farm AI - Main Entry Point  (v2 - Real Data Edition)
Usage:
    python main.py              # Interactive
    python main.py --demo       # Quick demo
    python main.py --train      # Retrain ML
    python main.py --whatsapp   # Preview SMS alert
    python main.py --test       # Run all tests
    streamlit run dashboard/streamlit_app.py   # Web UI
"""

import sys, os, argparse

# ── Robust path setup: works from ANY working directory ──────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agents.soil_agent        import SoilAgent
from agents.irrigation_agent  import IrrigationAgent
from agents.pest_agent        import PestAgent
from agents.yield_agent       import YieldAgent
from agents.fertilizer_agent  import FertilizerAgent
from agents.harvest_agent     import HarvestAgent
from agents.market_agent      import MarketAgent
from agents.leaf_scan_agent   import LeafScanAgent
from agents.digital_twin_agent import DigitalTwinAgent
from utils.weather_api        import get_weather
from utils.helpers            import format_rupees, get_season, get_growth_stage
from data.crop_data           import CROPS

try:
    from rich.console import Console
    from rich import box
    console = Console()
    RICH = True
except ImportError:
    class _C:
        def print(self, *a, **k):
            # Strip rich markup tags
            import re
            msg = str(a[0]) if a else ""
            msg = re.sub(r'\[.*?\]', '', msg)
            print(msg)
    console = _C()
    RICH = False

HEADER = """
=================================================================
   FARM AI  v2  -  9 AGENT INTELLIGENT FARMING SYSTEM
   Real Data: 61K records | 42 crops | 22 states | R2 up to 1.00
================================================================="""


def run_all_agents(config: dict, verbose: bool = True) -> dict:
    crop    = config.get("crop", "Rice")
    state   = config.get("state", "Telangana")
    acres   = float(config.get("acres", 5))
    ph      = float(config.get("soil_ph", 6.5))
    n       = float(config.get("nitrogen", 100))
    p       = float(config.get("phosphorus", 50))
    k       = float(config.get("potassium", 35))
    om      = float(config.get("organic_matter", 1.8))
    moist   = float(config.get("soil_moisture_pct", 55))
    days    = int(config.get("days_planted", 30))
    symp    = config.get("symptoms", "yellow spots")

    weather  = get_weather(state)
    temp     = weather["temperature_c"]
    humidity = weather["humidity_pct"]
    rain     = weather["rainfall_mm"]
    season   = get_season()
    grow_d   = CROPS.get(crop, {}).get("grow_days", 120)
    stage    = get_growth_stage(days, grow_d)

    if verbose:
        console.print(f"\n  [{state}] {crop} | {acres} acres | Stage: {stage}")
        console.print(f"  Weather: {temp}C | {humidity}% humidity | {rain}mm rain\n")

    agents_run = [
        ("1. Soil Agent",
         lambda: SoilAgent().analyze(ph, n, p, k, state, season, om, crop)),
        ("2. Irrigation Agent",
         lambda: IrrigationAgent().analyze(crop, moist, rain, temp, humidity, stage, 80, acres)),
        ("3. Pest Agent",
         lambda: PestAgent().analyze(crop, temp, humidity, rain, stage, [symp] if symp else [], acres)),
        ("4. Yield Agent",
         lambda: YieldAgent().analyze(state, crop, acres, ph, n, p, k, 900, temp, humidity)),
        ("5. Fertilizer Agent",
         lambda: FertilizerAgent().analyze(crop, acres, n, p, k, ph, season)),
        ("6. Harvest Agent",
         lambda: HarvestAgent().analyze(crop, max(0, grow_d - days), 20,
                                        rain_next_7days_mm=rain * 2, acres=acres)),
        ("7. Market Agent",
         lambda: MarketAgent().analyze(crop, state, acres, season)),
        ("8. Leaf Scan Agent",
         lambda: LeafScanAgent().analyze_text(symp, crop)),
        ("9. Digital Twin",
         lambda: DigitalTwinAgent().run_scenarios({
             "crop": crop, "acres": acres, "soil_ph": ph,
             "nitrogen": n, "rainfall_mm": 900, "pest_incidence": 0.1})),
    ]

    results = {}
    total_savings = 0
    for name, fn in agents_run:
        try:
            r = fn()
            results[name] = r
            action = r.get("action") or r.get("advice") or r.get("verdict") or ""
            if verbose:
                console.print(f"  [{name}]")
                console.print(f"    {action}")
            sv = r.get("annual_savings", "")
            nums = [int(s.replace(",","")) for s in sv.split() if s.replace(",","").isdigit()]
            if nums:
                total_savings += nums[0]
        except Exception as e:
            if verbose:
                console.print(f"  [{name}] ERROR: {e}")
            results[name] = {}

    if verbose:
        console.print(f"\n  TOTAL ANNUAL SAVINGS: {format_rupees(total_savings)}/year")
        console.print("=" * 65)

    results["_total_savings"] = total_savings
    return results


def demo_mode():
    console.print(HEADER)
    console.print("\n  DEMO — Telangana Rice Farm (5 acres)\n")
    run_all_agents({
        "farmer_name": "Demo Farmer", "state": "Telangana",
        "crop": "Rice", "acres": 5, "soil_ph": 6.5,
        "nitrogen": 100, "phosphorus": 50, "potassium": 35,
        "organic_matter": 1.8, "soil_moisture_pct": 55,
        "days_planted": 30, "symptoms": "yellow spots",
    })


def interactive_mode():
    console.print(HEADER)
    console.print("\n  Enter farm details (Enter = use defaults)\n")
    name  = input("  Farmer name [Raju]: ").strip() or "Raju"
    state = input("  State [Telangana]: ").strip() or "Telangana"
    crop  = input("  Crop [Rice]: ").strip() or "Rice"
    try: acres = float(input("  Farm size acres [5]: ").strip() or 5)
    except: acres = 5.0
    try: ph = float(input("  Soil pH [6.5]: ").strip() or 6.5)
    except: ph = 6.5

    console.print(f"\n  Running 9 agents for {name} | {acres}ac {crop} in {state}...\n")
    run_all_agents({"farmer_name": name, "state": state, "crop": crop,
                    "acres": acres, "soil_ph": ph,
                    "nitrogen": 100, "phosphorus": 50, "potassium": 35,
                    "soil_moisture_pct": 55, "days_planted": 30,
                    "symptoms": "yellow spots"})


def train_mode():
    console.print(HEADER)
    console.print("\n  TRAINING ML MODELS on real data...\n")
    from ml.yield_predictor import YieldPredictor
    YieldPredictor().train(verbose=True)


def test_mode():
    console.print(HEADER)
    console.print("\n  RUNNING TEST SUITE...\n")
    import subprocess
    test_path = os.path.join(ROOT, "tests", "test_agents.py")
    subprocess.run([sys.executable, test_path], cwd=ROOT)


def whatsapp_mode():
    from dashboard.whatsapp_alerts import demo_alert
    demo_alert()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Farm AI v2 - 9 Agent System")
    parser.add_argument("--demo",      action="store_true", help="Quick demo")
    parser.add_argument("--train",     action="store_true", help="Train ML models")
    parser.add_argument("--whatsapp",  action="store_true", help="Preview WhatsApp alert")
    parser.add_argument("--test",      action="store_true", help="Run test suite")
    parser.add_argument("--dashboard", action="store_true", help="Launch Streamlit UI")
    args = parser.parse_args()

    if   args.demo:      demo_mode()
    elif args.train:     train_mode()
    elif args.whatsapp:  whatsapp_mode()
    elif args.test:      test_mode()
    elif args.dashboard: os.system(f"streamlit run {os.path.join(ROOT,'dashboard','streamlit_app.py')}")
    else:                interactive_mode()
