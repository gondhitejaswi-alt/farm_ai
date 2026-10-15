"""Farm AI - Complete Test Suite (v3)
Run from any directory: python tests/test_agents.py
"""
import sys, os, traceback
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS = FAIL = 0

def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  PASS  {name}")
        PASS += 1
    except Exception as e:
        print(f"  FAIL  {name}: {e}")
        traceback.print_exc()
        FAIL += 1

# ── Agent tests ──────────────────────────────────────────────
def test_soil():
    from agents.soil_agent import SoilAgent
    r = SoilAgent().analyze(6.5, 100, 50, 35, "Telangana", "Kharif", 1.8, "Rice")
    assert "best_crop" in r, f"Missing best_crop. Keys: {list(r.keys())}"
    assert r["best_crop"] == "Rice", f"Expected Rice got {r['best_crop']}"
    assert r["soil_health"].endswith("/100")
    assert len(r["top5_crops"]) > 0

def test_irrigation():
    from agents.irrigation_agent import IrrigationAgent
    r = IrrigationAgent().analyze("Rice", 55, 15, 30, 75, "vegetative")
    assert "SKIP" in r["decision"] or "LIGHT" in r["decision"] or "IRRIGATE" in r["decision"], \
           f"Bad decision: {r['decision']}"
    assert "reason" in r
    assert r["action"]  # not empty

def test_pest():
    from agents.pest_agent import PestAgent
    r = PestAgent().analyze("Rice", 27, 85, 8, "vegetative", ["yellow spots"], 5)
    assert r["alert_level"] in ("LOW","MEDIUM","HIGH")
    assert r["action"], "Action is empty!"
    assert len(r["pest_risks"]) > 0

def test_yield():
    from agents.yield_agent import YieldAgent
    r = YieldAgent().analyze("Telangana", "Rice", 5, rainfall_mm=900)
    assert r["yield_per_acre_kg"] > 500, f"Yield too low: {r['yield_per_acre_kg']}"
    assert r["expected_revenue"] > 50000, f"Revenue too low: {r['expected_revenue']}"

def test_fertilizer():
    from agents.fertilizer_agent import FertilizerAgent
    r = FertilizerAgent().analyze("Rice", 5, 0, 0, 0)
    plan = r["fertilizer_plan"]
    assert plan["Urea_kg"] > 0, f"No Urea. Plan: {plan}"
    assert r["total_cost"] > 0
    assert r["money_saved"] > 0

def test_harvest():
    from agents.harvest_agent import HarvestAgent
    r = HarvestAgent().analyze("Rice", 5, 22, rain_next_7days_mm=30, acres=5)
    assert "timing_status" in r
    assert r["expected_revenue"] > 0
    # Should warn about rain (30mm within 5 days)
    assert r.get("rain_warning") is not None, "Should show rain warning for 30mm in 5 days"

def test_market():
    from agents.market_agent import MarketAgent
    r = MarketAgent().analyze("Rice", "Telangana", 5)
    assert r["best_price"] > 0, f"No price. Keys: {list(r.keys())}"
    assert r["best_mandi"], "No mandi name"
    # Should prefer local Telangana mandis
    local_mandis = ["Hyderabad","Warangal","Karimnagar","Nizamabad"]
    assert r["best_mandi"] in local_mandis, \
           f"Should return local mandi, got {r['best_mandi']}"

def test_leaf_scan():
    from agents.leaf_scan_agent import LeafScanAgent
    r = LeafScanAgent().analyze_text("yellow spots on leaves", "Rice")
    assert "detected_disease" in r
    assert r["confidence_pct"] >= 0
    assert r["action"]

def test_digital_twin():
    from agents.digital_twin_agent import DigitalTwinAgent
    base = {"crop":"Rice","acres":5,"soil_ph":6.5,"nitrogen":100,
            "rainfall_mm":900,"pest_incidence":0.1}
    r = DigitalTwinAgent().simulate(base, {"nitrogen":150})
    assert "delta" in r, f"Missing delta. Keys: {list(r.keys())}"
    assert "verdict" in r
    # All scenarios
    r2 = DigitalTwinAgent().run_scenarios(base)
    assert len(r2["all_scenarios"]) > 0
    assert r2["best_scenario"]

def test_weather():
    from utils.weather_api import get_weather, get_7day_forecast
    w = get_weather("Telangana")
    assert "temperature_c" in w
    assert 10 <= w["temperature_c"] <= 55
    fc = get_7day_forecast("Telangana")
    assert len(fc) == 7

def test_mandi():
    from utils.mandi_api import get_mandi_prices, get_price_trend
    p = get_mandi_prices("Rice", "Telangana")
    assert len(p) > 0
    t = get_price_trend("Rice", 7)
    assert len(t) == 7

def test_crop_data():
    from data.crop_data import CROPS, PESTS, STATE_ML_PERFORMANCE, MANDI_PRICES
    assert "Rice" in CROPS
    assert CROPS["Rice"]["ph_min"] == 5.5
    assert "Blast" in PESTS
    assert PESTS["Blast"]["crop"] == "Rice"
    assert "Telangana" in STATE_ML_PERFORMANCE
    assert STATE_ML_PERFORMANCE["Telangana"]["r2"] >= 0.9
    assert "Telangana" in MANDI_PRICES
    assert "Rice" in MANDI_PRICES["Telangana"]

def test_helpers():
    from utils.helpers import format_rupees, get_season, get_growth_stage
    assert format_rupees(150000) == "Rs 1.5 L"
    assert format_rupees(50000)  == "Rs 50K"
    assert format_rupees(500)    == "Rs 500"
    assert get_season(7)  == "Kharif"
    assert get_season(1)  == "Rabi"
    assert get_growth_stage(5,  120) == "seedling"
    assert get_growth_stage(60, 120) == "flowering"

def test_whatsapp_message():
    from dashboard.whatsapp_alerts import build_message
    msg = build_message({"farmer_name":"Raju","crop":"Rice","state":"Telangana",
                         "acres":5,"soil_ph":6.5,"nitrogen":90,"phosphorus":45,
                         "potassium":35,"soil_moisture_pct":55,"growth_stage":"vegetative"})
    assert "Raju" in msg
    assert "WATER" in msg
    assert "PEST" in msg
    assert "YIELD" in msg
    assert len(msg) > 100

# ── Run ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nFarm AI v3 - Complete Test Suite")
    print("=" * 48)
    test("Soil Agent",          test_soil)
    test("Irrigation Agent",    test_irrigation)
    test("Pest Agent",          test_pest)
    test("Yield Agent",         test_yield)
    test("Fertilizer Agent",    test_fertilizer)
    test("Harvest Agent",       test_harvest)
    test("Market Agent",        test_market)
    test("Leaf Scan Agent",     test_leaf_scan)
    test("Digital Twin Agent",  test_digital_twin)
    test("Weather API",         test_weather)
    test("Mandi API",           test_mandi)
    test("Crop Data",           test_crop_data)
    test("Helper Utils",        test_helpers)
    test("WhatsApp Message",    test_whatsapp_message)
    print("=" * 48)
    print(f"  Results: {PASS} passed, {FAIL} failed")
    if FAIL == 0:
        print("  ALL TESTS PASSED!")
    else:
        print(f"  {FAIL} tests need fixing")
