"""
Farm AI - Farmer-Friendly Dashboard
Simple, clear, helpful for every Indian farmer.
Run: streamlit run dashboard/streamlit_app.py
"""

import sys, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

try:
    from agents.soil_agent         import SoilAgent
    from agents.irrigation_agent   import IrrigationAgent
    from agents.pest_agent         import PestAgent
    from agents.yield_agent        import YieldAgent
    from agents.fertilizer_agent   import FertilizerAgent
    from agents.harvest_agent      import HarvestAgent
    from agents.market_agent       import MarketAgent
    from agents.leaf_scan_agent    import LeafScanAgent
    from agents.digital_twin_agent import DigitalTwinAgent
    from utils.weather_api         import get_weather, get_7day_forecast
    from utils.helpers             import format_rupees, INDIAN_STATES, CROP_LIST, get_season, get_growth_stage
    from data.crop_data            import STATE_ML_PERFORMANCE, CROPS
except Exception as _import_err:
    import streamlit as _st
    _st.error(f"Setup error: {_import_err}")
    _st.warning("Make sure you ran: cd farm_ai  then  py -m streamlit run dashboard/streamlit_app.py")
    _st.stop()

# ── Page setup ───────────────────────────────────────────────
st.set_page_config(
    page_title="Farm AI - Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu&display=swap');
body { font-family: 'Segoe UI', sans-serif; }

.big-header {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 60%, #43A047 100%);
    padding: 1.5rem 2rem; border-radius: 14px; color: white;
    text-align: center; margin-bottom: 1.2rem;
}
.big-header h1 { font-size: 2rem; margin: 0; font-weight: 800; letter-spacing: 1px; }
.big-header p  { margin: 0.3rem 0 0; opacity: 0.88; font-size: 1rem; }

.card {
    background: white; border-radius: 12px; padding: 1rem 1.2rem;
    border-left: 5px solid #2E7D32; margin: 0.4rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.card h4 { margin: 0 0 0.4rem; color: #1B5E20; font-size: 0.95rem; }
.card p  { margin: 0; font-size: 0.87rem; color: #333; line-height: 1.5; }

.card-red    { border-left-color: #c62828; }
.card-orange { border-left-color: #e65100; }
.card-blue   { border-left-color: #1565C0; }
.card-purple { border-left-color: #6A1B9A; }
.card-teal   { border-left-color: #00695C; }

.metric-box {
    background: #F1F8E9; border: 1px solid #C5E1A5; border-radius: 10px;
    padding: 0.9rem; text-align: center;
}
.metric-box .val { font-size: 1.7rem; font-weight: 800; color: #1B5E20; }
.metric-box .lbl { font-size: 0.75rem; color: #555; margin-top: 0.2rem; }

.alert-red    { background:#FFEBEE; border-left:4px solid #c62828; padding:0.8rem 1rem; border-radius:8px; margin:0.3rem 0; }
.alert-orange { background:#FFF3E0; border-left:4px solid #e65100; padding:0.8rem 1rem; border-radius:8px; margin:0.3rem 0; }
.alert-green  { background:#E8F5E9; border-left:4px solid #2E7D32; padding:0.8rem 1rem; border-radius:8px; margin:0.3rem 0; }

div[data-testid="stSidebar"] { background:#F9FBE7; }
.stButton > button { background:#2E7D32 !important; color:white !important;
    border:none !important; border-radius:8px !important; font-weight:700 !important;
    padding: 0.5rem 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Weather cache functions (defined once, used throughout) ──
@st.cache_data(ttl=3600, show_spinner=False)
def _get_weather_cached(state_name: str):
    return get_weather(state_name)

@st.cache_data(ttl=3600, show_spinner=False)
def _get_forecast_cached(state_name: str):
    return get_7day_forecast(state_name)

# Fetch early so header badge works (sidebar not yet rendered, use default state)
_default_weather = _get_weather_cached("Telangana")

# ── Header ───────────────────────────────────────────────────
_is_live   = _default_weather.get("is_live", False)
live_badge = "🟢 LIVE Data" if _is_live else "🟡 Demo Data"
st.markdown(f"""
<div class="big-header">
  <h1>🌾 Farm AI — Smart Farming Assistant</h1>
  <p>9 AI Agents | 42 Crops | 22 States | 61,000 Real Records | {live_badge}</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👨‍🌾 Your Farm Details")
    farmer_name = st.text_input("Your Name", "Raju")
    state       = st.selectbox("State", INDIAN_STATES,
                               index=INDIAN_STATES.index("Telangana") if "Telangana" in INDIAN_STATES else 0)
    crop        = st.selectbox("Crop", CROP_LIST)
    acres       = st.number_input("Farm Size (acres)", 0.5, 500.0, 5.0, 0.5)

    st.markdown("---")
    st.markdown("### 🧪 Soil Test Results")
    st.caption("Use Rs 200 soil test kit from agri office")
    soil_ph    = st.slider("Soil pH", 4.0, 9.0, 6.5, 0.1,
                           help="6.0-7.5 is best for most crops")
    nitrogen   = st.slider("Nitrogen (kg/ha)", 0, 300, 100,
                           help="Most crops need 100-150 kg/ha")
    phosphorus = st.slider("Phosphorus (kg/ha)", 0, 150, 50)
    potassium  = st.slider("Potassium (kg/ha)", 0, 150, 35)
    org_matter = st.slider("Organic Matter (%)", 0.2, 5.0, 1.8, 0.1)

    st.markdown("---")
    st.markdown("### 🌿 Crop Status")
    days_planted  = st.number_input("Days Since Planting", 0, 365, 30)
    soil_moisture = st.slider("Soil Moisture (%)", 0, 100, 55,
                              help="50-70% is ideal for most crops")
    pest_symptoms = st.text_input("Symptoms Seen (if any)",
                                  placeholder="e.g. yellow spots, white powder...")

    st.markdown("---")

    # ── API Status debug panel ──────────────────────────────
    import os as _os
    _api_key  = _os.getenv("OPENWEATHER_API_KEY", "").strip()
    _demo     = _os.getenv("DEMO_MODE", "false").strip().lower() == "true"
    _mandi_key= _os.getenv("DATA_GOV_KEY", "").strip()
    # Use _default_weather here (sidebar renders before the state-specific fetch)
    if _default_weather.get("is_live"):
        st.success("🟢 **LIVE Weather** — OpenWeatherMap")
    elif not _api_key:
        st.error("🔴 **No API key** — add OPENWEATHER_API_KEY to .env file")
    elif _demo:
        st.warning("🟡 **DEMO_MODE=true** — change to false in .env")
    else:
        st.warning(f"🟡 **Demo Weather** — key found ({_api_key[:6]}...) but API failed (check internet)")
    if _mandi_key:
        st.success("🟢 **LIVE Mandi Prices** — data.gov.in")
    else:
        st.error("🔴 **No Mandi key** — add DATA_GOV_KEY to .env file")

    st.markdown("---")
    run_btn = st.button("🚀 Get My Farm Advice", use_container_width=True)

# ── Fetch weather for selected state ──────────────────────────
weather  = _get_weather_cached(state)
forecast = _get_forecast_cached(state)
temp     = weather["temperature_c"]
humidity = weather["humidity_pct"]
rain     = weather["rainfall_mm"]
season   = get_season()
grow_d   = CROPS.get(crop, {}).get("grow_days", 120)
stage    = get_growth_stage(days_planted, grow_d)

# ── Top bar: weather + ML ─────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
for col, val, lbl in [
    (c1, f"{temp}°C", "Temperature"),
    (c2, f"{humidity}%", "Humidity"),
    (c3, f"{rain}mm", "Rain Today"),
    (c4, season, "Season"),
    (c5, stage.title(), "Crop Stage"),
    (c6, f"R²={STATE_ML_PERFORMANCE.get(state,{}).get('r2',0.5):.3f}", f"ML Accuracy ({state[:6]})"),
]:
    col.markdown(f'<div class="metric-box"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>',
                 unsafe_allow_html=True)

st.markdown("---")

# ── Run agents ───────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=300)
def run_agents(crop, state, acres, soil_ph, nitrogen, phosphorus, potassium,
               org_matter, days_planted, soil_moisture, pest_symptoms,
               temp, humidity, rain, season, stage, wind_kmh, solar_rad):
    symp = [pest_symptoms] if pest_symptoms and len(pest_symptoms) > 2 else []
    def safe(fn):
        try: return fn()
        except Exception as e: return {"error": str(e), "action": f"Agent error: {e}",
                                       "advice":"", "decision":"", "reason":"",
                                       "tip":"", "alert_level":"LOW",
                                       "top_threat":"None","top_threat_risk":0,
                                       "immediate_action":"No data","pest_risks":[],
                                       "high_risk_pests":[],"total_spray_cost":0,
                                       "crop_loss_prevented":0,"annual_savings":"",
                                       "yield_per_acre_kg":2000,"total_yield_kg":10000,
                                       "expected_revenue":200000,"model_r2":0.5,
                                       "confidence_label":"Medium","storage_needed_tonnes":5,
                                       "storage_advice":"","money_saved":0,
                                       "fertilizer_plan":{"Urea_kg":88,"DAP_kg":44,"MOP_kg":17},
                                       "total_cost":5000,"without_ai_cost":6000,
                                       "warnings":["Agent unavailable"],"schedule":[],
                                       "recommended_npk":{"N_kg_ha":120,"P_kg_ha":60,"K_kg_ha":40},
                                       "timing_status":"WAIT","days_to_harvest":60,
                                       "expected_price":2200,"msp":2183,
                                       "expected_revenue":200000,"drying_advice":"",
                                       "drying_cost":0,"rain_warning":None,
                                       "best_selling_month":"November","best_month_price":2400,
                                       "best_mandi":"Local Mandi","best_price":2200,
                                       "vs_msp_pct":0,"all_prices":{},"market_trend":"Stable",
                                       "trend_advice":"","switch_advice":"","top_alternatives":[],
                                       "detected_disease":"Unknown","confidence_pct":0,
                                       "disease_description":"","pesticide":"Consult agronomist",
                                       "dose":"","spray_timing":"","cost_per_acre":0,
                                       "organic_alternative":"Neem oil","plantix_alternative":"",
                                       "all_scenarios":[],"best_scenario":{},"worst_scenario":{},
                                       "soil_health":"60/100","health_label":"Good",
                                       "ph_class":"Neutral","ph_status":"Good",
                                       "nutrient_scores":{"Nitrogen":"60/100","Phosphorus":"60/100","Potassium":"60/100","Organic Matter":"60/100"},
                                       "best_crop":crop,"top5_crops":[crop],"avoid_crops":[],
                                       "amendments":["No data available"],"expected_revenue_per_acre":50000,
                                       "money_saved_today":0,"pump_hours":0,"pump_cost":0,
                                       "water_needed_mm":0,"rain_forecast_mm":rain,
                                       "soil_moisture_pct":soil_moisture,"growth_stage":stage}
    # ── Leaf scan runs FIRST so pest+fert agents can use its result ──
    leaf_result = safe(lambda: LeafScanAgent().analyze_text(
        pest_symptoms or "healthy leaves", crop=crop, soil_ph=soil_ph))

    return {
        "soil":    safe(lambda: SoilAgent().analyze(soil_ph, nitrogen, phosphorus, potassium,
                                       state, season, org_matter, crop)),
        "irr":     safe(lambda: IrrigationAgent().analyze(crop, soil_moisture, rain, temp,
                                             humidity, stage, 80, acres,
                                             wind_kmh=wind_kmh, solar_rad=solar_rad)),
        "pest":    safe(lambda: PestAgent().analyze(
                           leaf_scan_result=leaf_result,
                           weather={"temperature_c": temp, "humidity_pct": humidity, "rainfall_mm": rain},
                           crop=crop, growth_stage=stage, acres=acres, soil_ph=soil_ph)),
        "yield":   safe(lambda: YieldAgent().analyze(state, crop, acres, soil_ph, nitrogen,
                                        phosphorus, potassium, rain, temp, humidity,
                                        wind_speed=wind_kmh, solar_rad=solar_rad)),
        "fert":    safe(lambda: FertilizerAgent().analyze(
                           crop=crop, acres=acres,
                           current_n=nitrogen, current_p=phosphorus, current_k=potassium,
                           soil_ph=soil_ph, season=season,
                           leaf_scan_result=leaf_result,
                           days_since_planting=days_planted)),
        "harvest": safe(lambda: HarvestAgent().analyze(crop, max(0, grow_d - days_planted), 20,
                                          rain_next_7days_mm=rain * 2, temp_c=temp, acres=acres, state=state)),
        "market":  safe(lambda: MarketAgent().analyze(crop, state, acres, season)),
        "leaf":    leaf_result,
        "twin":    safe(lambda: DigitalTwinAgent().run_scenarios({
                       "crop": crop, "acres": acres, "soil_ph": soil_ph,
                       "nitrogen": nitrogen, "rainfall_mm": 900, "pest_incidence": 0.1})),
    }

with st.spinner("🤖 Running 9 Farm AI Agents for your farm..."):
    wind_kmh   = weather.get("wind_kmh", 12.0)
    solar_rad  = weather.get("solar_rad", 18.0) or 18.0  # real solar radiation from weather API
    R = run_agents(crop, state, acres, soil_ph, nitrogen, phosphorus, potassium,
                   org_matter, days_planted, soil_moisture, pest_symptoms,
                   temp, humidity, rain, season, stage, wind_kmh, solar_rad)

soil_r   = R["soil"];  irr_r  = R["irr"];  pest_r = R["pest"]
yield_r  = R["yield"]; fert_r = R["fert"]; harv_r = R["harvest"]
mkt_r    = R["market"];leaf_r = R["leaf"]; twin_r = R["twin"]

# ── TABS ─────────────────────────────────────────────────────
tabs = st.tabs(["📋 Daily Plan", "🧪 Soil", "💧 Water", "🐛 Pests",
                "📈 Yield", "🧬 Fertilizer", "🌾 Harvest",
                "💰 Market", "📸 Leaf Scan", "🔮 What-If", "📊 Analytics"])

# ════════════════════════════════════════════════════════════
# TAB 1 — DAILY PLAN  (most important for farmer)
# ════════════════════════════════════════════════════════════
with tabs[0]:
    st.subheader(f"📋 Good Morning {farmer_name}! Here is today's plan for your {crop} farm")
    st.caption(f"{datetime.datetime.now().strftime('%A, %d %B %Y')} | "
               f"{acres} acres | {state} | Stage: {stage.title()}")

    # URGENT alerts at top
    urgents = []
    if pest_r.get("alert_level", "LOW") == "HIGH":
        urgents.append(("🔴 PEST EMERGENCY", pest_r.get("immediate_action", pest_r.get("action_today", "Monitor crop")), "red"))
    if "URGENT" in harv_r.get("timing_status", "On Track") or "OVERDUE" in harv_r.get("timing_status", "On Track"):
        urgents.append(("🔴 HARVEST URGENT", harv_r.get("advice", "Monitor crop daily"), "red"))
    if harv_r.get("rain_warning"):
        urgents.append(("🌧️ RAIN WARNING", harv_r.get("rain_warning", ""), "red"))

    if urgents:
        for title, msg, _ in urgents:
            st.markdown(f'<div class="alert-red"><b>{title}:</b> {msg}</div>',
                        unsafe_allow_html=True)
        st.markdown("")

    # 3-column summary
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""<div class="card">
<h4>1. 🧪 Soil — {soil_r.get('health_label', 'Good')} ({soil_r.get('soil_health', '60/100')})</h4>
<p>pH {soil_ph} → <b>{soil_r.get('ph_class', 'Neutral')}</b><br>
Best crop for your soil: <b>{soil_r.get('best_crop', crop)}</b><br>
{(soil_r.get('amendments') or ['No corrections needed'])[0]}</p></div>""", unsafe_allow_html=True)

        dec = irr_r.get("decision", "Monitor soil moisture")
        card_col = "blue" if "SKIP" in dec else "orange"
        st.markdown(f"""<div class="card card-{card_col}">
<h4>2. 💧 Water — {dec}</h4>
<p>{irr_r.get('reason', 'Check soil moisture')}<br><b>{irr_r.get('tip', 'Monitor daily')}</b></p></div>""", unsafe_allow_html=True)

        pest_col = "red" if pest_r.get("alert_level", "LOW")=="HIGH" else "orange" if pest_r.get("alert_level", "LOW")=="MEDIUM" else ""
        st.markdown(f"""<div class="card card-{pest_col}">
<h4>3. 🐛 Pest Alert — {pest_r.get('alert_level', pest_r.get('risk_level', 'LOW'))}</h4>
<p>Risk: <b>{pest_r.get('top_threat', pest_r.get('detected_disease', 'None'))}</b> ({pest_r.get('top_threat_risk', pest_r.get('confidence', 0))}%)<br>
{pest_r.get('immediate_action', pest_r.get('action_today', pest_r.get('recommendation', 'Monitor crop')))}</p></div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="card card-purple">
<h4>4. 📈 Yield Forecast — ML R²={yield_r.get('model_r2', 0.5):.3f}</h4>
<p>Expected: <b>{yield_r.get('yield_per_acre_kg', 2000):,} kg/acre</b> | Total: <b>{yield_r.get('total_yield_kg', 10000):,} kg</b><br>
Revenue: <b>{format_rupees(yield_r.get('expected_revenue', 0))}</b> | {yield_r.get('confidence_label', 'MEDIUM')} confidence</p></div>""",
        unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div class="card card-teal">
<h4>5. 🧬 Fertilizer</h4>
<p>{fert_r.get('action', 'Apply fertilizers as per schedule')}<br>
Money saved vs guessing: <b>{format_rupees(fert_r.get('money_saved', 0))}</b><br>
{(fert_r.get('warnings') or ['Apply fertilizers as per schedule'])[0]}</p></div>""", unsafe_allow_html=True)

        harv_col = "red" if "URGENT" in harv_r.get("timing_status", "On Track") or "OVERDUE" in harv_r.get("timing_status", "On Track") else "orange" if "SOON" in harv_r.get("timing_status", "On Track") or "TODAY" in harv_r.get("timing_status", "On Track") else ""
        st.markdown(f"""<div class="card card-{harv_col}">
<h4>6. 🌾 Harvest — {harv_r.get('timing_status', 'On Track')}</h4>
<p>{harv_r.get('advice', 'Monitor crop daily')}<br>
Expected price: <b>Rs {harv_r.get('expected_price', 2200)}/quintal</b><br>
Revenue: <b>{format_rupees(harv_r.get('expected_revenue', 0))}</b></p></div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="card">
<h4>7. 💰 Market — {mkt_r.get('market_trend', 'Stable')}</h4>
<p>Best: <b>{mkt_r.get('best_mandi', 'Local Mandi')}</b> @ <b>Rs {mkt_r.get('best_price', 2200)}/quintal</b> ({mkt_r.get('vs_msp_pct', 0.0):+.1f}% vs MSP)<br>
{mkt_r.get('trend_advice', 'Hold and monitor prices')}</p></div>""", unsafe_allow_html=True)

        best_sc = twin_r.get("best_scenario", {})
        st.markdown(f"""<div class="card">
<h4>8-9. 📸 Leaf Scan + 🔮 What-If</h4>
<p>Disease detected: <b>{leaf_r.get('detected_disease', 'Unknown')}</b> ({leaf_r.get('confidence_pct', 0)}% confident)<br>
Best change you can make: <b>{best_sc.get('scenario','')}</b><br>
{best_sc.get('verdict','')}</p></div>""", unsafe_allow_html=True)

    # Annual profit summary
    st.markdown("---")
    st.markdown("### 💰 Your Annual Extra Profit Breakdown")
    profit_data = {
        "Right crop (Soil Agent)":      150000,
        "Save pump cost (Irrigation)":   50000,
        "Prevent pest loss (Pest)":     250000,
        "Storage planning (Yield)":     100000,
        "Exact fertilizer (Fertilizer)":100000,
        "Best harvest time (Harvest)":   50000,
        "Best mandi price (Market)":    100000,
        "Accurate disease ID (Leaf)":    50000,
        "Avoid bad decisions (Twin)":   100000,
    }
    p1, p2, p3 = st.columns(3)
    total = sum(profit_data.values())
    for i, (k, v) in enumerate(profit_data.items()):
        col = [p1, p2, p3][i % 3]
        col.markdown(f'<div class="metric-box"><div class="val">{format_rupees(v)}</div><div class="lbl">{k}</div></div>',
                     unsafe_allow_html=True)
    st.success(f"🎉 Total Extra Profit: {format_rupees(total)}/year for {acres} acres | "
               f"For 10 acres: {format_rupees(total * acres/5)} | ROI: 3000x on Rs 2,000 app cost")

    # 7-day forecast
    st.markdown("### 🌤️ 7-Day Weather Forecast")
    fc  = pd.DataFrame(forecast)
    fig = go.Figure()
    fig.add_bar(x=fc["date"], y=fc["rainfall_mm"], name="Rain (mm)", marker_color="#1565C0", opacity=0.7)
    fig.add_scatter(x=fc["date"], y=fc["temp_max"], name="Max Temp °C",
                    line=dict(color="#c62828", width=2.5), yaxis="y2", mode="lines+markers")
    fig.update_layout(
        yaxis=dict(title=dict(text="Rainfall (mm)", font=dict(color="#1565C0"))),
        yaxis2=dict(title=dict(text="Temperature (°C)", font=dict(color="#c62828")), overlaying="y", side="right"),
        height=260, margin=dict(t=10,b=20), legend=dict(orientation="h"),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — SOIL
# ════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("🧪 Soil Analysis — Is your soil ready?")

    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown(f"**Soil Health Score:** {soil_r.get('soil_health', '60/100')} ({soil_r.get('health_label', 'Good')})")
        st.markdown(f"**pH {soil_ph}** → {soil_r.get('ph_class', 'Neutral')}")
        st.markdown(f"**Status:** {soil_r.get('ph_status', 'Normal')}")
        st.markdown(f"**Best crop for your soil:** `{soil_r.get('best_crop', crop)}`")

        st.markdown("**Top 5 crops that will grow well:**")
        for i, c in enumerate(soil_r.get("top5_crops", []), 1):
            info = CROPS.get(c, {})
            tel  = info.get("telugu", "")
            rev  = round(info.get("avg_yield_kg_acre",0) * info.get("msp_per_quintal",0) / 100)
            st.markdown(f"  {i}. **{c}** {f'({tel})' if tel else ''} — Rs {rev:,}/acre potential")

        st.markdown("**What your soil needs:**")
        for a in soil_r.get("amendments", []):
            if "healthy" in a.lower() or "no correction" in a.lower():
                st.markdown(f'<div class="alert-green">{a}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-orange">{a}</div>', unsafe_allow_html=True)

        if soil_r.get("avoid_crops", []):
            st.markdown(f"**Avoid this season:** {', '.join(soil_r.get('avoid_crops', [])[:3])}")

    with c2:
        # Nutrient radar
        cats = ["Nitrogen", "Phosphorus", "Potassium", "Organic Matter"]
        vals = [float(soil_r.get("nutrient_scores", {})["Nitrogen"].split("/")[0]),
                float(soil_r.get("nutrient_scores", {})["Phosphorus"].split("/")[0]),
                float(soil_r.get("nutrient_scores", {})["Potassium"].split("/")[0]),
                float(soil_r.get("nutrient_scores", {})["Organic Matter"].split("/")[0])]
        vals_c = vals + [vals[0]]; cats_c = cats + [cats[0]]
        fig = go.Figure(go.Scatterpolar(
            r=vals_c, theta=cats_c, fill="toself",
            fillcolor="rgba(46,125,50,0.25)", line=dict(color="#2E7D32", width=2)
        ))
        fig.add_trace(go.Scatterpolar(
            r=[60]*5, theta=cats_c, mode="lines",
            line=dict(color="orange", dash="dash", width=1), name="Minimum needed"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(range=[0,100], tickfont_size=9)),
            height=360, title="Soil Nutrient Levels",
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"**Expected revenue for {soil_r.get('best_crop', crop)}:** "
                f"Rs {soil_r.get('expected_revenue_per_acre', 50000):,}/acre")

# ════════════════════════════════════════════════════════════
# TAB 3 — WATER
# ════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("💧 Irrigation Plan — When to water, when to save")

    dec = irr_r.get("decision", "Monitor soil moisture")
    if "SKIP" in dec:
        st.success(f"✅ **{dec}** — {irr_r.get('reason', 'Check soil moisture')}")
    elif "LIGHT" in dec:
        st.warning(f"💧 **{dec}** — {irr_r.get('reason', 'Check soil moisture')}")
    else:
        st.error(f"🚿 **{dec}** — {irr_r.get('reason', 'Check soil moisture')}")

    st.markdown(f"### 👉 {irr_r.get('tip', 'Monitor daily')}")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Decision", irr_r.get("decision", "Monitor soil moisture").split("—")[0].strip())
    c2.metric("Water Needed", f"{irr_r.get('water_needed_mm', 0)} mm")
    c3.metric("Pump Hours", f"{irr_r.get('pump_hours', 0)} hrs")
    c4.metric("Cost Today", format_rupees(irr_r.get("pump_cost", 0)))

    if irr_r.get("money_saved_today", 0) > 0:
        st.success(f"💰 You SAVE Rs {irr_r.get('money_saved_today', 0):,} today by not running pump!")

    # Moisture gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=soil_moisture,
        delta={"reference": 60, "valueformat": ".0f"},
        title={"text": "Soil Moisture %"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar":  {"color": "#2E7D32"},
            "steps": [
                {"range": [0,  30], "color": "#FFEBEE"},
                {"range": [30, 50], "color": "#FFF3E0"},
                {"range": [50, 75], "color": "#E8F5E9"},
                {"range": [75,100], "color": "#C8E6C9"},
            ],
            "threshold": {"line": {"color":"blue","width":3}, "value":60}
        }
    ))
    fig.update_layout(height=280)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Blue line = ideal moisture (60%). Green zone = good. Red zone = water urgently needed.")

# ════════════════════════════════════════════════════════════
# TAB 4 — PESTS
# ════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("🐛 Pest & Disease Alert")

    lvl = pest_r.get("alert_level", "LOW")
    if lvl == "HIGH":
        st.error(f"🚨 HIGH RISK — Act today or lose 30% crop!")
    elif lvl == "MEDIUM":
        st.warning(f"⚠️ MEDIUM RISK — Watch carefully this week")
    else:
        st.success(f"✅ LOW RISK — Conditions are safe today")

    st.markdown(f"**What to do right now:** {pest_r.get('immediate_action', pest_r.get('action_today', pest_r.get('recommendation', 'Monitor crop')))}")
    if pest_r.get("total_spray_cost", 0) > 0:
        st.info(f"Spray cost: Rs {pest_r.get('total_spray_cost', 0):,} | "
                f"Crop saved: {format_rupees(pest_r.get('crop_loss_prevented', 0))}")

    # Risk chart
    risks = pest_r.get("pest_risks", [])
    if risks:
        df_p  = pd.DataFrame(risks)
        fig   = px.bar(df_p, x="pest", y="risk_pct",
                       color="risk_pct", color_continuous_scale=["#4CAF50","#FFC107","#F44336"],
                       range_color=[0,100], labels={"risk_pct":"Risk %","pest":"Pest/Disease"},
                       title="Disease Risk Levels Today")
        fig.add_hline(y=40, line_dash="dash", line_color="orange",
                      annotation_text="Action needed above 40%")
        fig.add_hline(y=60, line_dash="dash", line_color="red",
                      annotation_text="High risk above 60%")
        fig.update_layout(height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Details per pest
    for r in risks:
        if r["risk_pct"] >= 30:
            color = "🔴" if r["risk_pct"] >= 60 else "🟡" if r["risk_pct"] >= 40 else "🟢"
            with st.expander(f"{color} {r['pest']} — {r['risk_pct']}% risk"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**What is it:** {r['description']}")
                    st.markdown(f"**Pesticide:** `{r['pesticide']}`")
                    st.markdown(f"**Dose:** {r['dose']}")
                with col2:
                    st.markdown(f"**When to spray:** {r['spray_timing']}")
                    st.markdown(f"**Cost:** Rs {r['cost_per_acre']:,}/acre")
                    st.markdown(f"**Organic option:** {r['organic_alt']}")
                tip = r.get("farmer_tip", "")
                if tip:
                    st.info(f"💡 Farmer Tip: {tip}")

# ════════════════════════════════════════════════════════════
# TAB 5 — YIELD
# ════════════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("📈 Yield Forecast — How much will you harvest?")

    c1,c2,c3 = st.columns(3)
    c1.metric("Yield per Acre",   f"{yield_r.get('yield_per_acre_kg', 2000):,} kg")
    c2.metric("Total Yield",      f"{yield_r.get('total_yield_kg', 10000):,} kg")
    c3.metric("Expected Revenue", format_rupees(yield_r.get("expected_revenue", 0)))

    c1,c2,c3 = st.columns(3)
    c1.metric("ML Accuracy (R²)",  f"{yield_r.get('model_r2', 0.5):.3f}")
    c2.metric("Confidence",        yield_r.get("confidence_label", "MEDIUM"))
    c3.metric("Storage Needed",    f"{yield_r.get('storage_needed_tonnes', 5)} tonnes")

    st.info(yield_r.get("storage_advice", "Store in dry place"))

    # State performance chart
    st.markdown("### How accurately does AI predict yield in your state?")
    sdf = pd.DataFrame([{"State": s, "R2": v["r2"], "Samples": v["samples"]}
                        for s,v in STATE_ML_PERFORMANCE.items()]).sort_values("R2", ascending=True)
    fig = px.bar(sdf, x="R2", y="State", orientation="h",
                 color="R2", color_continuous_scale=["#F44336","#FF9800","#4CAF50"],
                 range_color=[0,1], title="AI Accuracy by State (green = very accurate)")
    fig.add_vline(x=0.8, line_dash="dash", line_color="green", annotation_text="Excellent (0.8)")
    fig.add_vline(x=0.6, line_dash="dash", line_color="orange", annotation_text="Good (0.6)")
    fig.update_layout(height=500, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    sel = STATE_ML_PERFORMANCE.get(state, {})
    if sel.get("r2", 0) >= 0.95:
        st.success(f"**{state}:** AI is {sel['r2']*100:.0f}% accurate — very reliable for your farm!")
    elif sel.get("r2", 0) >= 0.7:
        st.info(f"**{state}:** AI is {sel['r2']*100:.0f}% accurate — good prediction")
    else:
        st.warning(f"**{state}:** AI is {sel['r2']*100:.0f}% accurate — treat as estimate, not guarantee")

# ════════════════════════════════════════════════════════════
# TAB 6 — FERTILIZER
# ════════════════════════════════════════════════════════════
with tabs[5]:
    st.subheader("🧬 Fertilizer Plan — Exact dose, no waste")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Urea needed", f"{(fert_r.get('fertilizer_plan') or {}).get('Urea_kg', 0)} kg")
    c2.metric("DAP needed",  f"{(fert_r.get('fertilizer_plan') or {}).get('DAP_kg', 0)} kg")
    c3.metric("MOP needed",  f"{(fert_r.get('fertilizer_plan') or {}).get('MOP_kg', 0)} kg")
    c4.metric("Total cost",  format_rupees(fert_r.get("total_cost", 0)))

    c1,c2 = st.columns(2)
    c1.metric("Without AI (guessing)", format_rupees(fert_r.get("without_ai_cost", 0)))
    c2.metric("You SAVE with AI",      format_rupees(fert_r.get("money_saved", 0)),
              delta=f"+{format_rupees(fert_r.get('money_saved', 0))}")

    st.markdown("### When to apply (split schedule):")
    for s in fert_r.get("schedule", []):
        st.markdown(f"📅 **{s['stage']}:** Urea {s['urea_kg']}kg | DAP {s['dap_kg']}kg | MOP {s['mop_kg']}kg")

    st.markdown("### Warnings:")
    for w in fert_r.get("warnings", []):
        if any(x in w.lower() for x in ["too much","skip","fix ph","🔴","⚠️"]):
            st.warning(f"⚠️ {w}" if not w.startswith("⚠️") else w)
        else:
            st.success(f"✅ {w}" if not w.startswith("✅") else w)

    # ── NEW: Deficiency correction from Leaf Scan ─────────────────────
    if fert_r.get("deficiency_note"):
        st.warning(fert_r.get("deficiency_note", ""))

    if fert_r.get("deficiency_addon") and fert_r["deficiency_addon"].get("deficiency_found"):
        addon = fert_r["deficiency_addon"]
        with st.expander("🔬 Deficiency Correction (detected by Leaf Scan)"):
            st.markdown(f"**Deficiency:** {addon.get('deficiency_found')}")
            st.markdown(f"**Fertilizer to add:** `{addon.get('correction_fertilizer', 'N/A')}`")
            st.markdown(f"**Dose:** {addon.get('correction_dose', 'As per label')}")
            st.markdown(f"**When:** {addon.get('spray_timing', 'Immediately')}")
            if addon.get("cost", 0) > 0:
                st.markdown(f"**Extra cost:** Rs {round(addon['cost'])}")

    # ── NEW: Nutrient availability at current pH ──────────────────────
    ph_avail = fert_r.get("nutrient_availability", {})
    if ph_avail:
        st.markdown("### 🧪 Nutrient Availability at Your pH")
        pa1, pa2, pa3 = st.columns(3)
        n_pct = ph_avail.get("N_pct", 100)
        p_pct = ph_avail.get("P_pct", 100)
        k_pct = ph_avail.get("K_pct", 100)
        with pa1:
            st.metric("Nitrogen absorbed", f"{n_pct}%",
                      delta="Good" if n_pct >= 80 else "Low — fix pH")
        with pa2:
            st.metric("Phosphorus absorbed", f"{p_pct}%",
                      delta="Good" if p_pct >= 80 else "Low — fix pH")
        with pa3:
            st.metric("Potassium absorbed", f"{k_pct}%",
                      delta="Good" if k_pct >= 80 else "Low — fix pH")

    est_ph = fert_r.get("estimated_ph_after")
    if est_ph:
        curr_ph = fert_r.get("soil_ph", soil_ph)
        ph_diff = round(float(est_ph) - float(curr_ph), 1)
        _ph_msg = (f"After applying this fertilizer plan, soil pH may change from "
                   f"**{curr_ph}** → **{est_ph}** ({'+' if ph_diff >= 0 else ''}{ph_diff}). "
                   f"Re-test soil after 30 days.")
        if est_ph < 5.8 or est_ph > 8.0:
            st.warning(f"⚠️ {_ph_msg} Consider lime or sulphur correction.")
        else:
            st.info(f"ℹ️ {_ph_msg}")

    # ── NEW: Organic options ──────────────────────────────────────────
    org_opts = fert_r.get("organic_options", [])
    if org_opts:
        with st.expander("🌿 Organic / Natural Alternatives"):
            for opt in org_opts:
                st.markdown(f"• {opt}")

    fig = go.Figure(go.Bar(
        x=["Farmer guessing", "With Farm AI"],
        y=[fert_r.get("without_ai_cost", 0), fert_r.get("total_cost", 0)],
        marker_color=["#EF5350","#66BB6A"],
        text=[format_rupees(fert_r.get("without_ai_cost", 0)), format_rupees(fert_r.get("total_cost", 0))],
        textposition="outside",
    ))
    fig.update_layout(title="Fertilizer Cost: Guessing vs AI", height=280,
                      yaxis_title="Cost (Rs)", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 7 — HARVEST
# ════════════════════════════════════════════════════════════
with tabs[6]:
    st.subheader("🌾 Harvest Timing — Best day = best money")

    sts = harv_r.get("timing_status", "On Track")
    if any(x in sts for x in ["URGENT","OVERDUE","TODAY"]):
        st.error(f"🚨 **{sts}** — {harv_r.get('advice', 'Monitor crop daily')}")
    elif "SOON" in sts:
        st.warning(f"⏰ **{sts}** — {harv_r.get('advice', 'Monitor crop daily')}")
    else:
        st.info(f"⏳ **{sts}** — {harv_r.get('advice', 'Monitor crop daily')}")

    if harv_r.get("rain_warning"):
        st.error(f"🌧️ {harv_r.get('rain_warning', '')}")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Days to Harvest", harv_r.get("days_to_harvest", 30))
    c2.metric("Mandi Price",     f"Rs {harv_r.get('expected_price', 2200)}/q")
    c3.metric("MSP Price",       f"Rs {harv_r.get('msp', 2183)}/q")
    c4.metric("Your Revenue",    format_rupees(harv_r["expected_revenue"]))

    st.markdown(f"**Moisture check:** {harv_r.get('drying_advice', 'Check moisture before storage')}")
    st.markdown(f"**Best month to sell {crop}:** {harv_r.get('best_selling_month', 'November')} "
                f"(Rs {harv_r.get('best_month_price', 2400)}/quintal)")

    # Monthly price chart
    # Temporary fix: PRICE_CALENDAR removed during v7+v9 merge
    PRICE_CALENDAR = {}
    cal = PRICE_CALENDAR.get(crop, {m: 1.0 for m in range(1,13)})
    months = [datetime.date(2024,m,1).strftime("%b") for m in range(1,13)]
    prices = [round(harv_r["msp"] * cal.get(m,1.0)) for m in range(1,13)]
    fig = px.line(x=months, y=prices, markers=True,
                  labels={"x":"Month","y":"Price (Rs/quintal)"},
                  title=f"{crop} Price by Month — best time to sell")
    fig.add_hline(y=harv_r["msp"], line_dash="dash", line_color="red",
                  annotation_text="MSP (minimum)")
    fig.update_traces(line_color="#2E7D32", marker_color="#2E7D32")
    fig.update_layout(height=300, plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 8 — MARKET
# ════════════════════════════════════════════════════════════
with tabs[7]:
    st.subheader("💰 Market Prices — Sell at the right mandi")

    c1,c2,c3 = st.columns(3)
    c1.metric("Best Mandi",        mkt_r["best_mandi"])
    c2.metric("Best Price",        f"Rs {mkt_r.get('best_price', 2200)}/quintal")
    c3.metric("vs MSP",            f"{mkt_r.get('vs_msp_pct', 0.0):+.1f}%",
              delta=f"{mkt_r.get('vs_msp_pct', 0.0):+.1f}%")

    trend = mkt_r["market_trend"]
    if trend == "Rising":   st.success(f"📈 Price is RISING — {mkt_r.get('trend_advice', 'Hold and monitor prices')}")
    elif trend == "Falling":st.error(f"📉 Price is FALLING — {mkt_r.get('trend_advice', 'Hold and monitor prices')}")
    else:                   st.info(f"➡️ Price is STABLE — {mkt_r.get('trend_advice', 'Hold and monitor prices')}")

    if mkt_r["all_prices"]:
        df_m = pd.DataFrame([{"Mandi":k,"Price":v} for k,v in mkt_r["all_prices"].items()])
        fig  = px.bar(df_m, x="Mandi", y="Price", color="Price",
                      color_continuous_scale=["#EF5350","#FFC107","#4CAF50"],
                      title=f"{crop} Prices — All Nearby Mandis (Rs/quintal)")
        fig.add_hline(y=mkt_r["msp"], line_dash="dash", line_color="red",
                      annotation_text="MSP")
        fig.update_layout(height=300, coloraxis_showscale=False, plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    if mkt_r["top_alternatives"]:
        st.markdown("### 🔄 Next season: Consider switching to...")
        for alt in mkt_r["top_alternatives"]:
            tel = CROPS.get(alt["crop"],{}).get("telugu","")
            st.success(f"🌱 **{alt['crop']}** {f'({tel})' if tel else ''} — "
                       f"Earn Rs {alt['extra_revenue']:,} MORE | "
                       f"Price: Rs {alt['price']}/quintal")
    st.info(f"**Recommendation:** {mkt_r.get('switch_advice', 'Continue current crop')}")

# ════════════════════════════════════════════════════════════
# TAB 9 — LEAF SCAN
# ════════════════════════════════════════════════════════════
# TAB 9 — LEAF SCAN (UPGRADED — Claude Vision AI)
# ════════════════════════════════════════════════════════════
with tabs[8]:
    st.subheader("📸 Leaf Scan — Upload ANY photo → Get exact medicine + fertilizer")
    st.markdown("""
    **How it works:** Upload a photo of a sick leaf → Claude AI identifies disease OR nutrient deficiency
    → You get the exact **pesticide + fertilizer + dose + cost**. Works for ANY crop, ANY photo.
    """)

    lsc1, lsc2 = st.columns([1, 1])

    with lsc1:
        st.markdown("#### 📷 Upload Leaf Photo")
        uploaded = st.file_uploader(
            "Take a close-up photo of the sick leaf (daylight is best)",
            type=["jpg", "jpeg", "png"],
            help="Clear close-up photos give best results. Capture the spots/patches clearly."
        )
        desc = st.text_area(
            "Describe what you see (optional but improves accuracy)",
            value=pest_symptoms or "",
            placeholder="e.g. yellow spots on edges, white powder, brown patches, purple underside...",
            height=80
        )
        st.markdown(f"**Soil pH in use:** `{soil_ph}` — affects deficiency diagnosis")

        scan_btn = st.button("🔍 Identify Disease / Deficiency", type="primary", use_container_width=True)

        if scan_btn:
            with st.spinner("🤖 Claude AI is analyzing your leaf photo..."):
                if uploaded:
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as _f:
                        _f.write(uploaded.read())
                        _tmp = _f.name
                    st.session_state["leaf"] = LeafScanAgent().analyze_image(
                        image_path=_tmp, symptom_description=desc,
                        crop=crop, soil_ph=soil_ph)
                else:
                    if not desc or len(desc.strip()) < 3:
                        st.warning("⚠️ Upload a photo OR describe what you see (at least a few words).")
                        st.stop()
                    st.session_state["leaf"] = LeafScanAgent().analyze_text(
                        description=desc, crop=crop, soil_ph=soil_ph)

        if uploaded and "leaf" in st.session_state:
            st.image(uploaded, caption="Your leaf photo", width=260)

        with st.expander("📌 Photo tips for best results"):
            st.markdown("""
            - 📱 **Natural daylight** — no flash, no shadows
            - 🔍 **Close-up** — spots should fill the frame
            - 🌿 **Single leaf** — not whole plant
            - 🤍 **White background** (paper/cloth) helps AI see colors
            - 📝 Adding text description improves accuracy
            """)

    with lsc2:
        res  = st.session_state.get("leaf", leaf_r)
        conf = int(res.get("confidence_pct", 0))
        disease = res.get("detected_disease", "Unknown")
        is_def  = res.get("is_deficiency", False)
        src     = res.get("source", "")

        if res.get("error"):
            st.error(f"🔴 API Error: {res['error']}")
            st.info("Add ANTHROPIC_API_KEY to .env file and run: pip install anthropic")
        elif "Healthy" in disease and conf >= 60:
            st.success(f"🟢 **Crop looks HEALTHY!** ({conf}% confident)")
        elif conf >= 75:
            if is_def:
                st.warning(f"🟡 **NUTRIENT DEFICIENCY: {disease}** ({conf}%)")
            else:
                st.error(f"🔴 **DISEASE FOUND: {disease}** ({conf}%)")
        elif conf >= 45:
            st.warning(f"🟡 **Possible: {disease}** ({conf}% — try clearer photo)")
        else:
            st.info(f"ℹ️ {disease} — confidence low. Upload a clearer photo.")

        st.caption(f"Analysis: {src}")

        if conf >= 40 and "Healthy" not in disease and "Unable" not in disease:
            dd = res.get("disease_description", "")
            if dd:
                st.markdown(f"**🔬 What is it:** {dd}")
            st.divider()

            if is_def:
                st.markdown("### 🧪 Nutrient Treatment")
                st.markdown(f"**Fertilizer:** `{res.get('fertilizer', 'See below')}`")
                st.markdown(f"**Dose:** {res.get('fert_dose', 'As per label')}")
                st.markdown(f"**When:** {res.get('spray_timing', 'Immediately')}")
            else:
                st.markdown("### 💊 Treatment")
                st.markdown(f"**Pesticide:** `{res.get('pesticide', 'Consult agri officer')}`")
                st.markdown(f"**Dose:** {res.get('pest_dose', res.get('dose', 'As per label'))}")
                st.markdown(f"**When to spray:** {res.get('spray_timing', 'Early morning')}")

            _c = res.get("cost_per_acre", 0)
            if _c:
                st.markdown(f"**Cost:** Rs {_c}/acre = Rs {round(_c * acres)} for your {acres} acres")
            st.markdown(f"**Natural option:** {res.get('organic_alternative', 'Neem oil 5ml/litre')}")

            _ph = res.get("ph_note", "")
            if _ph:
                st.divider()
                st.markdown("### 🧪 Your pH Impact")
                if any(x in _ph for x in ["⚠️", "HIGH", "LOW", "lock", "CAUSING"]):
                    st.warning(_ph)
                else:
                    st.success(_ph)

            _sev = res.get("severity", "")
            _spd = res.get("spread_risk", "")
            if _sev or _spd:
                _s1, _s2 = st.columns(2)
                with _s1: st.metric("Severity", _sev.title() if _sev else "?")
                with _s2: st.metric("Spread Risk", _spd[:25] if _spd else "?")

            _act = res.get("farmer_action", "")
            if _act:
                st.markdown(f"""
                <div style="background:#FFF3E0;border-left:4px solid #e65100;
                padding:0.8rem 1rem;border-radius:8px;margin:0.5rem 0">
                <b>🚨 Do This TODAY:</b> {_act}
                </div>
                """, unsafe_allow_html=True)

        elif conf >= 75 and "Healthy" in disease:
            st.success("✅ Great! Keep monitoring every 3 days.")
            st.markdown("**Preventive tips:**")
            st.markdown("- Spray Mancozeb 2g/litre preventively before heavy rains")
            st.markdown("- Avoid waterlogging — drains every 5 days")
            st.markdown("- Balanced fertilizer — excess N attracts pests")

        st.divider()
        st.caption("💡 This result automatically updates Pest Agent & Fertilizer Agent tabs.")

# ════════════════════════════════════════════════════════════
# TAB 10 — WHAT-IF SIMULATOR
# ════════════════════════════════════════════════════════════
with tabs[9]:
    st.subheader("🔮 What-If Simulator — Test before you spend")
    st.markdown("Test different farming decisions WITHOUT spending money. "
                "AI calculates if it will be profitable.")

    best = twin_r.get("best_scenario", {})
    worst= twin_r.get("worst_scenario", {})
    if best:
        st.success(f"✅ **Best thing to do:** {best.get('scenario','')} → {best.get('verdict','')}")
    if worst and worst.get("profit_gain",0) < -5000:
        st.warning(f"⚠️ **Avoid this:** {worst.get('scenario','')} → {worst.get('verdict','')}")

    # Scenarios chart
    sc_df = pd.DataFrame(twin_r.get("all_scenarios", []))
    if not sc_df.empty:
        fig = px.bar(sc_df, x="scenario", y="profit_gain",
                     color="profit_gain",
                     color_continuous_scale=["#F44336","#FF9800","#4CAF50"],
                     title="Which change earns you more money? (Rs)",
                     labels={"profit_gain":"Extra Profit (Rs)","scenario":"What you change"})
        fig.add_hline(y=0, line_color="black", line_width=1)
        fig.update_layout(height=320, xaxis_tickangle=-20, coloraxis_showscale=False,
                          plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Try your own what-if:")
    c1,c2 = st.columns(2)
    with c1:
        wi_n    = st.slider("What if I use more/less Nitrogen?", 0, 300, nitrogen+20)
        wi_cert = st.checkbox("What if I use certified seeds? (+8% yield)")
    with c2:
        wi_acres= st.slider("What if I expand farm size?", 0.5, 100.0, float(acres))

    if st.button("▶️ Calculate"):
        base_s   = {"crop":crop,"acres":acres,"soil_ph":soil_ph,"nitrogen":nitrogen,
                    "rainfall_mm":900,"pest_incidence":0.1}
        changes  = {"nitrogen":wi_n,"acres":wi_acres,"certified_seeds":wi_cert}
        result   = DigitalTwinAgent().simulate(base_s, changes)
        delta    = result["delta"]["profit"]
        if delta > 0:
            st.success(f"✅ Result: You earn Rs {delta:,} MORE — {result['verdict']}")
        elif delta < 0:
            st.error(f"❌ Result: You earn Rs {abs(delta):,} LESS — {result['verdict']}")
        else:
            st.info(f"➡️ Result: No big difference — {result['verdict']}")
        c1,c2 = st.columns(2)
        c1.metric("Current profit",   format_rupees(result["base"]["profit"]))
        c2.metric("New profit",       format_rupees(result["new"]["profit"]),
                  delta=f"{'+' if delta>0 else ''}{format_rupees(abs(delta))}")

# ════════════════════════════════════════════════════════════
# TAB 11 — ANALYTICS
# ════════════════════════════════════════════════════════════
with tabs[10]:
    st.subheader("📊 Farm Analytics — Big Picture")

    # Impact at scale
    st.markdown("### Social Impact: How many farmers can benefit?")
    scale = pd.DataFrame({
        "Farmers": ["100", "1,000", "10,000", "1 Lakh", "10 Lakh"],
        "Extra Income (Rs Crore)": [0.6, 6, 60, 600, 6000],
        "Label": ["Rs 60L", "Rs 6Cr", "Rs 60Cr", "Rs 600Cr", "Rs 6000Cr"],
    })
    fig = px.bar(scale, x="Farmers", y="Extra Income (Rs Crore)", text="Label",
                 title="Economic Impact of Farm AI on Indian Farmers",
                 color="Extra Income (Rs Crore)", color_continuous_scale="Greens")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=320, coloraxis_showscale=False, plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)

    # Crop profitability
    st.markdown("### Crop Profitability Comparison")
    crop_df = pd.DataFrame([
        {"Crop": c,
         "Yield (kg/acre)": info.get("avg_yield_kg_acre",0),
         "Revenue (Rs/acre)": round(info.get("avg_yield_kg_acre",0)*info.get("msp_per_quintal",0)/100),
         "Water Need": info.get("water_mm_per_week",0),
         "Grow Days": info.get("grow_days",0)}
        for c, info in CROPS.items()
    ]).sort_values("Revenue (Rs/acre)", ascending=False)

    fig2 = px.bar(crop_df, x="Crop", y="Revenue (Rs/acre)",
                  color="Revenue (Rs/acre)", color_continuous_scale="Greens",
                  title="Revenue per Acre by Crop (at MSP)")
    fig2.update_layout(height=350, xaxis_tickangle=-30, coloraxis_showscale=False,
                       plot_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("Farm AI — Built for India's 120 million farmers 🇮🇳🌾 | "
               "Made with real data from Kaggle + DSV (61,000 records, 2018-2023)")
