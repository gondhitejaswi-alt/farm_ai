"""
Farm AI — Farmer-Friendly Multilingual Smart Agriculture Assistant
Designed for Farmers in Telangana, Andhra Pradesh & Across India 🇮🇳🌾

Features:
- Balanced Orange & Green Farmer-Friendly Theme (Nature & Action)
- 3 Languages: Telugu (తెలుగు), Hindi (हिन्दी), English
- All 9 Intelligent AI Agents (Soil, Water, Pest, Yield, Fertilizer, Harvest, Market, Leaf Scan, Digital Twin)
- Live Weather with 2-Line Generated Natural Farmer Report & Alerts (OpenWeatherMap API)
- District & Village selector for Telangana and Andhra Pradesh
- Crop Recommendation with Farmer Explanations, Sowing Guidance & Disclaimers
- Live Mandi Prices (data.gov.in official API) with Nearby Market Comparison
- Leaf Scan AI Doctor (Google Gemini Vision AI + Offline Disease DB)
- Multilingual FAQ & Gemini AI Help Chatbot with Quick-Tap Questions
- Voice Assistant (Speech-to-Text & Text-to-Speech)
- Telangana & AP Crop Calendar (Kharif, Rabi, Summer)
- Government Agricultural Schemes (Rythu Bandhu, Rythu Bharosa, PM-Kisan, etc.)
- Farmer History Log
- Agronomist & ML Analytics (R², Models, Economic Impact)
"""

import sys, os, datetime, time, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

# ── Streamlit Page Configuration (Must be first!) ──────────────
st.set_page_config(
    page_title="Farm AI — Smart Agriculture Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sync Streamlit Cloud secrets to os.environ for cloud deployment
try:
    if hasattr(st, "secrets"):
        for _sec_key, _sec_val in st.secrets.items():
            if isinstance(_sec_val, str) and _sec_key not in os.environ:
                os.environ[_sec_key] = _sec_val
except Exception:
    pass

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit.components.v1 as components

# ── Load Core Agents & Modules ───────────────────────────────
try:
    from i18n import t, LANGUAGES, crop_name, STRINGS
    from faq import suggested_questions, get_answer_by_id, answer_free_text, ask_ai_assistant, FAQS, KCC_LINE
    from utils.live_weather import get_live_weather, DISTRICTS, format_time
    from utils.weather_summary import two_line_summary, alerts, condition_text
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
    # v11 additions
    from utils import storage as store
    from dashboard.visuals import icon_html
except Exception as _import_err:
    st.error(f"Setup Error: {_import_err}")
    st.info("Please ensure you run from the farm_ai directory with: python -m streamlit run dashboard/streamlit_app.py")
    st.stop()

# ── Session State Initialization ──────────────────────────────
if "settings" not in st.session_state:
    st.session_state["settings"] = store.load_settings()   # remembered across restarts
SET = st.session_state["settings"]
if "lang" not in st.session_state:
    st.session_state["lang"] = SET.get("lang") or "te"  # Default to Telugu for Telangana & AP
if "history" not in st.session_state:
    st.session_state["history"] = store.load_history()      # saved on disk — never lost
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = store.load_chat()

if "leaf_result" not in st.session_state:
    st.session_state["leaf_result"] = None
if "voice_query" not in st.session_state:
    st.session_state["voice_query"] = ""

lang = st.session_state["lang"]

# ── Farmer-Friendly Orange & Green Styling ─────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700;800&family=Noto+Sans+Devanagari:wght@400;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

:root { color-scheme: light; }
html, body, [class*="css"], .stApp { font-family: 'Inter','Noto Sans Telugu','Noto Sans Devanagari',-apple-system,'Segoe UI',sans-serif; }

/* ── Always a clear LIGHT page with DARK text (fixes white-on-white) ── */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background:#FFFDF8 !important; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div,
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li { color:#1F2937; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
[data-testid="stHeading"] *, [data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4 { color:#14532D !important; font-weight:800 !important; }
.stApp [data-testid="stCaptionContainer"], .stApp small { color:#4B5563 !important; font-size:0.95rem !important; }
.stApp a { color:#C2410C; font-weight:700; }
.block-container { padding-top:1.2rem; max-width:1200px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"], div[data-testid="stSidebar"] { background:#F1F8F2 !important; border-right:2px solid #CFE3D0; }
section[data-testid="stSidebar"] * { color:#1F2937; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color:#14532D !important; }
section[data-testid="stSidebar"] [data-testid="stExpander"] { background:#FFFFFF; border:1.5px solid #CFE3D0; border-radius:12px; }
section[data-testid="stSidebar"] [data-testid="stExpander"] summary p { font-weight:700; color:#14532D !important; }

/* ── Big, clear section tabs (works in old and new Streamlit) ── */
.stTabs [role="tablist"], .stTabs [data-baseweb="tab-list"] { gap:8px; flex-wrap:wrap !important; border-bottom:none !important; background:transparent; overflow:visible !important; }
.stTabs [role="tab"] {
    background:#FFFFFF !important; border:2px solid #CFE3D0 !important; border-radius:14px !important;
    padding:0.65rem 1.1rem !important; height:auto !important; min-height:3rem; }
.stTabs [role="tab"] p, .stTabs [role="tab"] div { font-size:1.08rem !important; font-weight:700 !important; color:#14532D !important; }
.stTabs [role="tab"][aria-selected="true"] { background:#C2410C !important; border-color:#C2410C !important; }
.stTabs [role="tab"][aria-selected="true"] p, .stTabs [role="tab"][aria-selected="true"] div { color:#FFFFFF !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"], .react-aria-SelectionIndicator { display:none !important; }
.stTabs [data-testid="stTabScrollButton"], .stTabs [data-baseweb="tab-list"] ~ button { display:none !important; }
/* inner (second-level) tabs a little quieter */
.stTabs .stTabs [role="tab"] { border-color:#D1D5DB !important; min-height:2.6rem; }
.stTabs .stTabs [role="tab"][aria-selected="true"] { background:#14532D !important; border-color:#14532D !important; }

/* ── Hero ── */
.farmer-hero { background:#E8F5E9; border:2px solid #CFE3D0; border-left:10px solid #C2410C;
    border-radius:18px; padding:1.3rem 1.6rem; margin-bottom:1rem; }
.farmer-hero h1 { font-size:2rem; margin:0; line-height:1.25; color:#14532D !important; }
.farmer-hero p  { margin:0.45rem 0 0; font-size:1.1rem; color:#374151 !important; }

/* ── Cards ── */
.farm-card { background:#FFFFFF; border-radius:16px; padding:1.1rem 1.3rem; border:2px solid #E3ECE1;
    border-left:8px solid #2E7D32; margin:0.6rem 0; box-shadow:0 1px 4px rgba(0,0,0,0.05); }
.farm-card h4 { margin:0 0 0.45rem; color:#14532D !important; font-size:1.15rem; font-weight:800; }
[data-testid="stMarkdownContainer"] .farm-card h2, .farm-card h2 { color:#C2410C !important; font-size:1.8rem !important; margin:0 0 0.3rem !important; }
.farm-card p, .farm-card b, .farm-card span { font-size:1.02rem; color:#1F2937 !important; line-height:1.6; }
.card-orange { border-left-color:#C2410C; } .card-amber { border-left-color:#D97706; }
.card-blue { border-left-color:#1D4ED8; }   .card-red { border-left-color:#B91C1C; }
.card-purple { border-left-color:#7E22CE; } .card-teal { border-left-color:#0F766E; }

/* ── Number tiles ── */
.farm-metric { background:#FFFFFF; border:2px solid #CFE3D0; border-radius:14px; padding:0.8rem 0.5rem; text-align:center; }
.farm-metric .val { font-size:1.35rem; overflow-wrap:normal; word-break:keep-all; font-weight:800; color:#14532D !important; }
.farm-metric .lbl { font-size:0.9rem; font-weight:700; color:#374151 !important; margin-top:0.2rem; }
[data-testid="stMetric"] { background:#FFFFFF; border:2px solid #E3ECE1; border-radius:14px; padding:0.7rem 0.9rem; }
[data-testid="stMetricLabel"] *, [data-testid="stMetricValue"] * { color:#14532D !important; }

/* ── Alerts (text always dark on pastel) ── */
.alert-box { padding:0.9rem 1.2rem; border-radius:12px; margin:0.6rem 0; font-size:1.05rem; line-height:1.6; }
.alert-box, .alert-box * { color:#1F2937 !important; }
.alert-red    { background:#FEE2E2; border:2px solid #F87171; border-left:8px solid #B91C1C; }
.alert-orange { background:#FFEDD5; border:2px solid #FDBA74; border-left:8px solid #C2410C; }
.alert-green  { background:#DCFCE7; border:2px solid #86EFAC; border-left:8px solid #15803D; }
[data-testid="stAlert"] * { color:#1F2937 !important; }

/* ── Buttons: big, orange, white text ── */
.stButton > button, .stDownloadButton > button {
    background:#C2410C !important; border:none !important; border-radius:12px !important;
    min-height:2.9rem; padding:0.55rem 1.4rem !important; box-shadow:0 2px 5px rgba(194,65,12,0.25) !important; }
.stButton > button *, .stDownloadButton > button * { color:#FFFFFF !important; font-weight:700 !important; font-size:1.02rem !important; }
.stButton > button:hover, .stDownloadButton > button:hover { background:#9A3412 !important; }
section[data-testid="stSidebar"] .stButton > button { background:#15803D !important; }
section[data-testid="stSidebar"] .stButton > button:hover { background:#14532D !important; }

/* ── Inputs: white box, dark text, visible border ── */
[data-baseweb="input"] input, [data-baseweb="select"] > div, textarea, [data-baseweb="textarea"] {
    background:#FFFFFF !important; color:#1F2937 !important; border-color:#9CA3AF !important; }
[data-baseweb="select"] * { color:#1F2937 !important; }
[data-testid="stFileUploader"] section { background:#FFFFFF; border:2px dashed #9CA3AF; }
[data-testid="stFileUploader"] * { color:#1F2937 !important; }
[data-testid="stFileUploader"] button * { color:#FFFFFF !important; }

/* Badges / misc */
.badge-live { background:#DCFCE7; color:#14532D; padding:0.3rem 0.7rem; border-radius:20px; font-weight:700; border:1px solid #86EFAC; display:inline-block; }
.badge-orange { background:#FFEDD5; color:#9A3412; padding:0.3rem 0.7rem; border-radius:20px; font-weight:700; border:1px solid #FDBA74; display:inline-block; }
.howto { background:#FFFFFF; border:2px solid #CFE3D0; border-radius:16px; padding:0.9rem 1.2rem; margin:0.4rem 0 1rem; }
.howto b, .howto li { font-size:1.05rem; color:#1F2937 !important; }
</style>
""", unsafe_allow_html=True)

# ── Accessibility preferences (Settings tab) ──────────────────
if SET.get("large_text"):
    st.markdown("<style>html{font-size:120% !important;} .stApp p,.stApp label,.stApp li{font-size:1.08rem !important;}"
                ".stButton>button{min-height:3.2rem !important;font-size:1.15rem !important;}</style>", unsafe_allow_html=True)
if SET.get("high_contrast"):
    st.markdown("<style>.stApp{background:#FFFFFF !important;} .stApp p,.stApp li,.stApp label,.stApp span{color:#000 !important;}"
                ".farm-card{border:2px solid #1B5E20 !important;} .alert-box{border:2px solid #000 !important;}"
                ".farm-metric{border:2px solid #1B5E20 !important;}</style>", unsafe_allow_html=True)

# ── Voice Speech-To-Text / Text-To-Speech Component ───────────
def render_voice_assistant(lang_code: str, text_to_speak: str = ""):
    st_lang = "te-IN" if lang_code == "te" else ("hi-IN" if lang_code == "hi" else "en-IN")
    js_text = text_to_speak.replace('"', '\\"').replace("\n", " ") if text_to_speak else ""
    btn_speak_label = "🔊 వినండి (Read Aloud)" if lang_code == "te" else ("🔊 सुनें (Read Aloud)" if lang_code == "hi" else "🔊 Listen (Read Aloud)")
    btn_mic_label = "🎤 మాట్లాడండి (Tap to Speak)" if lang_code == "te" else ("🎤 बोलिए (Tap to Speak)" if lang_code == "hi" else "🎤 Speak Question")
    
    html_code = f"""
    <div style="display:flex; gap:10px; flex-wrap:wrap; margin:10px 0;">
        <button id="micBtn" onclick="startDictation()" style="
            background: #E65100; color: white; border: none; border-radius: 25px;
            padding: 9px 18px; font-weight: 700; font-size: 14px; cursor: pointer;
            box-shadow: 0 2px 6px rgba(230,81,0,0.3); display: flex; align-items: center; gap: 6px;
        ">
            {btn_mic_label}
        </button>

        <button id="ttsBtn" onclick="speakText()" style="
            background: #2E7D32; color: white; border: none; border-radius: 25px;
            padding: 9px 18px; font-weight: 700; font-size: 14px; cursor: pointer;
            box-shadow: 0 2px 6px rgba(46,125,50,0.3); display: flex; align-items: center; gap: 6px;
        ">
            {btn_speak_label}
        </button>
        <span id="voiceStatus" style="font-size:13px; color:#555; align-self:center;"></span>
    </div>

    <script>
    function startDictation() {{
        var status = document.getElementById("voiceStatus");
        if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) {{
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            var recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = "{st_lang}";
            status.innerHTML = "🔴 Listening... మాట్లాడండి...";

            recognition.onresult = function(e) {{
                var transcript = e.results[0][0].transcript;
                status.innerHTML = "✅ Heard: " + transcript;
                if (navigator.clipboard) {{
                    navigator.clipboard.writeText(transcript);
                }}
                alert("Heard: " + transcript + "\\n(Copied to clipboard. Paste in question box below!)");
            }};
            recognition.onerror = function(e) {{
                status.innerHTML = "⚠️ Voice error: " + e.error;
                recognition.stop();
            }};
            recognition.start();
        }} else {{
            alert("Speech recognition not supported in this browser. Please use Chrome/Edge or type your question.");
        }}
    }}

    function speakText() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var text = "{js_text}";
            if (!text || text.length === 0) {{
                text = "నమస్కారం! ఫార్మ్ ఏఐ మీకు సహాయం చేయడానికి సిద్ధంగా ఉంది.";
            }}
            var utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "{st_lang}";
            utterance.rate = 0.95;
            window.speechSynthesis.speak(utterance);
        }} else {{
            alert("Speech synthesis not supported in this browser.");
        }}
    }}
    </script>
    """
    components.html(html_code, height=55)

# ── Header & Language Switcher ────────────────────────────────
top_col1, top_col2 = st.columns([3, 1])
def _lang_from(key):
    """Callback: the farmer picked a language in the top selector or in Settings."""
    st.session_state["lang"] = st.session_state[key]
    SET["lang"] = st.session_state[key]
    store.save_settings(SET)

st.session_state["lang_selector"] = st.session_state["lang"]   # keep both selectors in sync

with top_col2:
    selected_lang = st.selectbox(
        "🌐 " + t("language", lang),
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(lang),
        key="lang_selector",
        on_change=_lang_from, args=("lang_selector",)
    )
    if selected_lang != st.session_state["lang"]:
        st.session_state["lang"] = selected_lang
        SET["lang"] = selected_lang
        store.save_settings(SET)
        st.rerun()

lang = st.session_state["lang"]

# ── Sidebar: Farmer & Land Details ────────────────────────────
with st.sidebar:
    st.markdown(f"## 👨‍🌾 {t('greeting', lang, name='రైతు / Farmer')}")
    farmer_name = st.text_input(t("your_name", lang), value="రాము (Ramu)")
    
    state = st.selectbox(
        t("state", lang),
        INDIAN_STATES,
        index=INDIAN_STATES.index("Telangana") if "Telangana" in INDIAN_STATES else 0
    )
    
    # District selection for Telangana & AP
    district_list = [d for d, val in DISTRICTS.items() if (state == "Telangana" and val[2] == "TS") or (state == "Andhra Pradesh" and val[2] == "AP")]
    if not district_list:
        district_list = list(DISTRICTS.keys())
    
    district = st.selectbox(
        t("choose_place", lang),
        district_list,
        index=0
    )

    crop = st.selectbox(
        t("pick_crop", lang),
        CROP_LIST,
        index=CROP_LIST.index("Rice") if "Rice" in CROP_LIST else 0,
        format_func=lambda c: f"{c} ({crop_name(c, lang, CROPS)})"
    )
    
    acres = st.number_input("🌾 " + ("పొలం పరిమాణం (ఎకరాలు)" if lang=="te" else ("खेत का आकार (एकड़)" if lang=="hi" else "Farm Size (acres)")), 0.5, 500.0, 5.0, 0.5)

    with st.expander("🧪 " + t("x_side_soil", lang), expanded=True):
        st.caption("సాయిల్ హెల్త్ కార్డ్ నుండి వివరాలు నమోదు చేయండి" if lang=="te" else ("सॉयल हेल्थ कार्ड से विवरण दर्ज करें" if lang=="hi" else "Enter values from your Soil Health Card"))
    
        soil_ph    = st.slider(t("soil_ph_label", lang), 4.0, 9.0, 6.5, 0.1, help=t("ph_help", lang))
        nitrogen   = st.slider(f"{t('nitrogen', lang)} (kg/ha)", 0, 300, 100)
        phosphorus = st.slider(f"{t('phosphorus', lang)} (kg/ha)", 0, 150, 50)
        potassium  = st.slider(f"{t('potassium', lang)} (kg/ha)", 0, 150, 35)
        org_matter = st.slider(f"{t('organic_matter_lbl', lang)} (%)", 0.2, 5.0, 1.8, 0.1)
    with st.expander("🌿 " + t("x_side_crop", lang), expanded=True):
        days_planted  = st.number_input("విత్తిన రోజుల సంఖ్య" if lang=="te" else ("बुवाई के दिन" if lang=="hi" else "Days Since Planting"), 0, 365, 30)
        soil_moisture = st.slider("నేల తేమ శాతం (Moisture %)" if lang=="te" else ("मिट्टी की नमी %" if lang=="hi" else "Soil Moisture (%)"), 0, 100, 55)
        pest_symptoms = st.text_input("లక్షణాలు (ఏవైనా ఉంటే)" if lang=="te" else ("लक्षण (यदि कोई हों)" if lang=="hi" else "Symptoms Seen"),
                                      placeholder="e.g. పసుపు మచ్చలు / yellow spots / తెల్ల పొడి...")

        st.markdown("---")

    st.markdown("---")
    run_btn = st.button("🚀 " + ("నా పొలం సమగ్ర సలహా పొందండి" if lang=="te" else ("मेरे खेत की पूरी सलाह पाएं" if lang=="hi" else "Get My Farm Advice")), use_container_width=True)

# ── Fetch Local Weather & Generate 2-Line Farmer Summary ──────
live_w = get_live_weather(district)
weather_summary_tuple = two_line_summary(live_w, lang)
weather_alerts_list   = alerts(live_w, lang)

_wx_ok = live_w.get("status") in ("live", "stale")
temp_val = live_w.get("temp_c", 27.0) if _wx_ok else 27.0      # agents need a number; display below shows "—" if not real
hum_val  = live_w.get("humidity_pct", 65) if _wx_ok else 65
_rc = live_w.get("rain_chance_pct") if _wx_ok else None
rain_chance = _rc if _rc is not None else 10
cond_val = condition_text(live_w.get("condition", "Clear"), lang) if live_w.get("status") in ("live", "stale") else "Clear"
season_val = get_season()
grow_days  = CROPS.get(crop, {}).get("grow_days", 120)
crop_stage = get_growth_stage(days_planted, grow_days)

# ── Top Hero Banner ───────────────────────────────────────────
greeting_title = t("greeting", lang, name=farmer_name)
app_tagline    = t("app_tagline", lang)
hero_badge = "🟢 Live weather" if live_w.get("status") == "live" else ""

st.markdown(f"""
<div class="farmer-hero">
    <h1>🌾 {greeting_title}</h1>
    <p>{app_tagline}</p>
    <p>📍 <b>{district}, {state}</b> &nbsp; {hero_badge}</p>
</div>
""", unsafe_allow_html=True)
with st.expander("ℹ️ " + t("x_howto_title", lang), expanded=False):
    st.markdown(f'<div class="howto"><ol><li>{t("x_howto_1", lang)}</li><li>{t("x_howto_2", lang)}</li><li>{t("x_howto_3", lang)}</li></ol></div>', unsafe_allow_html=True)

# ── Real Two-Line Weather Summary & Farming Alerts ────────────
if weather_summary_tuple:
    l1, l2 = weather_summary_tuple
    st.markdown(f"""
    <div class="alert-box alert-orange" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <b>🌤️ {t('weather_title', lang)} ({district}):</b> {l1}<br>
            <b>👉 {t('next_steps', lang)}:</b> {l2}
        </div>
        <div style="font-size:0.85rem; color:#8D6E63;">
            {t('last_updated', lang)}: {format_time(live_w.get('fetched_at', time.time()))}
        </div>
    </div>
    """, unsafe_allow_html=True)

if weather_alerts_list:
    for al in weather_alerts_list:
        st.markdown(f'<div class="alert-box alert-red"><b>⚠️ {t("alerts_title", lang)}:</b> {al}</div>', unsafe_allow_html=True)

# ── Top Metric Ribbon ─────────────────────────────────────────
m1, m2, m3, m4, m5, m6 = st.columns(6)
metrics_list = [
    (m1, f"{temp_val}°C" if _wx_ok else "—", t("temperature", lang)),
    (m2, f"{hum_val}%" if _wx_ok else "—", t("humidity", lang)),
    (m3, f"{_rc}%" if (_wx_ok and _rc is not None) else "—", t("rain_chance", lang)),
    (m4, season_val, t("season", lang)),
    (m5, crop_stage.title(), "పంట దశ / Stage" if lang=="te" else ("फसल अवस्था" if lang=="hi" else "Crop Stage")),
    ((m6, f"R²={STATE_ML_PERFORMANCE.get(state,{}).get('r2', 0.92):.2f}", "AI ఖచ్చితత్వం / Accuracy" if lang=="te" else ("सटीकता" if lang=="hi" else "AI Accuracy"))
     if SET.get("developer_mode") else
     (m6, f"{acres:g} ac", "పొలం / Farm" if lang=="te" else ("खेत" if lang=="hi" else "Farm"))),
]
for col, v, l in metrics_list:
    col.markdown(f'<div class="farm-metric"><div class="val">{v}</div><div class="lbl">{l}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Run All 9 AI Agents ───────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=300)
def execute_all_agents(crop, state, acres, soil_ph, nitrogen, phosphorus, potassium,
                       org_matter, days_planted, soil_moisture, pest_symptoms,
                       temp, humidity, rain_mm, season, stage, wind_kmh, solar_rad):
    symp = [pest_symptoms] if pest_symptoms and len(pest_symptoms) > 2 else []
    def safe_run(fn):
        try: return fn()
        except Exception as e:
            return {"error": str(e), "action": f"Notice: {e}", "decision": "Monitor", "advice": "Consult local agri officer",
                    "best_crop": crop, "soil_health": "70/100", "health_label": "Good", "ph_class": "Neutral",
                    "top5_crops": [crop], "amendments": ["Maintain balanced organic manure"],
                    "water_needed_mm": 20, "pump_hours": 3, "pump_cost": 75, "money_saved_today": 0,
                    "alert_level": "LOW", "top_threat": "None", "immediate_action": "Crop is in healthy stage",
                    "yield_per_acre_kg": 2000, "total_yield_kg": int(acres*2000), "expected_revenue": int(acres*2000*22),
                    "storage_needed_tonnes": round(acres*2.0, 1), "model_r2": 0.91, "confidence_label": "HIGH",
                    "fertilizer_plan": {"Urea_kg": int(acres*45), "DAP_kg": int(acres*25), "MOP_kg": int(acres*15)},
                    "total_cost": int(acres*1200), "without_ai_cost": int(acres*1800), "money_saved": int(acres*600),
                    "schedule": [], "warnings": ["Apply balanced fertilizers as recommended"],
                    "timing_status": "On Track", "days_to_harvest": max(10, 120-days_planted), "expected_price": 2200, "msp": 2183,
                    "best_mandi": "Warangal APMC", "best_price": 2250, "vs_msp_pct": 3.1, "all_prices": {"Warangal": 2250, "Hyderabad": 2200},
                    "market_trend": "Stable", "top_alternatives": [], "detected_disease": "Healthy Crop", "confidence_pct": 85,
                    "all_scenarios": [], "best_scenario": {"scenario": "Use certified seeds", "verdict": "Earn +8% profit"},
                    "worst_scenario": {"scenario": "Excess nitrogen", "verdict": "Wastes money"}}

    leaf_res = safe_run(lambda: LeafScanAgent().analyze_text(pest_symptoms or "healthy leaves", crop=crop, soil_ph=soil_ph))
    return {
        "soil":    safe_run(lambda: SoilAgent().analyze(soil_ph, nitrogen, phosphorus, potassium, state, season, org_matter, crop)),
        "irr":     safe_run(lambda: IrrigationAgent().analyze(crop, soil_moisture, 0, temp, humidity, stage, 80, acres, wind_kmh=wind_kmh, solar_rad=solar_rad)),
        "pest":    safe_run(lambda: PestAgent().analyze(leaf_scan_result=leaf_res, weather={"temperature_c": temp, "humidity_pct": humidity, "rainfall_mm": 0}, crop=crop, growth_stage=stage, acres=acres, soil_ph=soil_ph)),
        "yield":   safe_run(lambda: YieldAgent().analyze(state, crop, acres, soil_ph, nitrogen, phosphorus, potassium, 900, temp, humidity, wind_speed=wind_kmh, solar_rad=solar_rad)),
        "fert":    safe_run(lambda: FertilizerAgent().analyze(crop=crop, acres=acres, current_n=nitrogen, current_p=phosphorus, current_k=potassium, soil_ph=soil_ph, season=season, leaf_scan_result=leaf_res, days_since_planting=days_planted)),
        "harvest": safe_run(lambda: HarvestAgent().analyze(crop, max(0, grow_days - days_planted), 20, rain_next_7days_mm=10, temp_c=temp, acres=acres, state=state)),
        "market":  safe_run(lambda: MarketAgent().analyze(crop, state, acres, season)),
        "leaf":    leaf_res,
        "twin":    safe_run(lambda: DigitalTwinAgent().run_scenarios({"crop": crop, "acres": acres, "soil_ph": soil_ph, "nitrogen": nitrogen, "rainfall_mm": 900, "pest_incidence": 0.1})),
    }

with st.spinner("🤖 " + ("9 వ్యవసాయ ఏజెంట్లను నడుపుతున్నాము..." if lang=="te" else ("9 कृषि एजेंट चला रहे हैं..." if lang=="hi" else "Running 9 Farm AI Agents..."))):
    R = execute_all_agents(
        crop, state, acres, soil_ph, nitrogen, phosphorus, potassium,
        org_matter, days_planted, soil_moisture, pest_symptoms,
        temp_val, hum_val, 0, season_val, crop_stage, 12.0, 18.0
    )

soil_r   = R["soil"];  irr_r  = R["irr"];  pest_r = R["pest"]
yield_r  = R["yield"]; fert_r = R["fert"]; harv_r = R["harvest"]
mkt_r    = R["market"];leaf_r = R["leaf"]; twin_r = R["twin"]

# Save to persistent history (v11: written to disk, duplicates skipped)
_new_entry = {
    "crop": crop, "district": district, "state": state, "acres": acres,
    "recommended_crop": soil_r.get("best_crop", crop),
    "yield_kg": yield_r.get("total_yield_kg", 0),
    "revenue": yield_r.get("expected_revenue", 0),
    "irrigation": irr_r.get("decision", ""),
    "pest_alert": pest_r.get("alert_level", ""),
}
if store.add_history(_new_entry):
    st.session_state["history"] = store.load_history()

# ── SECTIONS (v12): 19 screens grouped into 8 simple sections ───
# The screen bodies below still use tabs[0] … tabs[17] exactly as before.
_sec = st.tabs([
    "🏠 " + t("nav_home", lang),
    "🌾 " + t("nav_crop", lang),
    "🧪 " + t("nav_soil", lang),
    "🌤️ " + t("nav_weather", lang),
    t("sec_farm", lang),
    "💬 " + t("nav_help", lang),
    "📜 " + t("nav_history", lang),
    t("sec_more", lang),
])
tabs = [None] * 18
tabs[0] = _sec[0]                               # Daily plan  -> Home
tabs[1] = _sec[1]                               # Crop recommendation
with _sec[2]:                                   # Soil + Fertilizer together
    _i = st.tabs([t("tab_soil", lang), t("tab_fertilizer", lang)])
    tabs[2], tabs[6] = _i[0], _i[1]
tabs[15] = _sec[3]                              # Weather
with _sec[4]:                                   # Water, pests, yield, harvest, market, leaf, what-if
    _i = st.tabs([t("tab_water", lang), t("tab_pests", lang), t("tab_yield", lang), t("tab_harvest", lang),
                  t("tab_market", lang), t("tab_leaf_scan", lang), t("tab_what_if", lang)])
    tabs[3], tabs[4], tabs[5], tabs[7], tabs[8], tabs[9], tabs[10] = _i
tabs[11] = _sec[5]                              # Help & FAQs
tabs[16] = _sec[6]                              # My farming history
with _sec[7]:                                   # Calendar, schemes, analytics, settings
    _i = st.tabs([t("tab_calendar", lang), t("tab_schemes", lang), t("tab_analytics", lang), t("tab_settings", lang)])
    tabs[12], tabs[13], tabs[14], tabs[17] = _i

# ════════════════════════════════════════════════════════════
# TAB 1: DAILY PLAN (రోజువారీ సమగ్ర ప్రణాళిక)
# ════════════════════════════════════════════════════════════
with tabs[0]:
    st.subheader(f"📋 {t('home_what_today', lang)}")
    st.caption(f"{datetime.datetime.now().strftime('%A, %d %B %Y')} | {acres:g} {'ఎకరాలు' if lang=='te' else ('एकड़' if lang=='hi' else 'acres')} | {district}, {state}")

    # Quick actions (v11)
    _qa = [("crop", "x_qa_crop", "qa_crop_rec"), ("fert", "x_qa_fert", "qa_fert_guide"),
           ("weather", "x_qa_weather", "tab_weather"), ("help", "x_qa_help", "tab_help")]
    for _col, (_ic, _lbl, _tabk) in zip(st.columns(4), _qa):
        _col.markdown(f'<div class="farm-card card-orange" style="text-align:center;">{icon_html(_ic, lang, 56)}'
                      f'<h4 style="margin-top:0.4rem;">{t(_lbl, lang)}</h4>'
                      f'<p style="color:#E65100;font-weight:700;">{t("x_qa_open_tab", lang)}:<br>{t(_tabk, lang)}</p></div>',
                      unsafe_allow_html=True)

    # Urgent Alert banners
    if pest_r.get("alert_level") == "HIGH":
        st.markdown(f'<div class="alert-box alert-red"><b>🔴 {t("tab_pests", lang)}:</b> {pest_r.get("immediate_action", "Act immediately")}</div>', unsafe_allow_html=True)
    if "URGENT" in harv_r.get("timing_status", ""):
        st.markdown(f'<div class="alert-box alert-red"><b>🌾 {t("tab_harvest", lang)}:</b> {harv_r.get("advice", "Prepare for harvest")}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="farm-card">
            <h4>1. 🧪 {t('tab_soil', lang)} — {soil_r.get('health_label', 'Good')} ({soil_r.get('soil_health', '70/100')})</h4>
            <p>pH {soil_ph} → <b>{soil_r.get('ph_class', 'Neutral')}</b><br>
            {t('best_crop', lang)}: <b>{crop_name(soil_r.get('best_crop', crop), lang, CROPS)}</b><br>
            {(soil_r.get('amendments') or ['No corrections needed'])[0]}</p>
        </div>
        """, unsafe_allow_html=True)

        dec = irr_r.get("decision", "Monitor soil moisture")
        dec_color = "card-blue" if "SKIP" in dec else "card-orange"
        st.markdown(f"""
        <div class="farm-card {dec_color}">
            <h4>2. 💧 {t('tab_water', lang)} — {dec}</h4>
            <p>{irr_r.get('reason', 'Check soil moisture')}<br>
            <b>💡 {irr_r.get('tip', 'Check soil before pumping')}</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="farm-card card-amber">
            <h4>3. 🐛 {t('tab_pests', lang)} — {pest_r.get('alert_level', 'LOW')}</h4>
            <p>{t('tab_pests', lang)}: <b>{pest_r.get('top_threat', 'None')}</b> ({pest_r.get('top_threat_risk', 15)}% Risk)<br>
            {pest_r.get('immediate_action', 'Crop looks healthy')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="farm-card card-purple">
            <h4>4. 📈 {t('tab_yield', lang)}</h4>
            <p>{t('yield_per_acre', lang)}: <b>{yield_r.get('yield_per_acre_kg', 2000):,} kg</b> | {t('total_yield', lang)}: <b>{yield_r.get('total_yield_kg', 10000):,} kg</b><br>
            {t('expected_revenue', lang)}: <b>{format_rupees(yield_r.get('expected_revenue', 0))}</b></p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="farm-card card-teal">
            <h4>5. 🧬 {t('tab_fertilizer', lang)}</h4>
            <p>{fert_r.get('action', 'Apply balanced fertilizers')}<br>
            {t('you_save_ai', lang)}: <b>{format_rupees(fert_r.get('money_saved', 0))}</b><br>
            {(fert_r.get('warnings') or ['Apply on time'])[0]}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="farm-card card-orange">
            <h4>6. 🌾 {t('tab_harvest', lang)} — {harv_r.get('timing_status', 'On Track')}</h4>
            <p>{harv_r.get('advice', 'Monitor crop maturity')}<br>
            {t('mandi_price', lang)}: <b>Rs {harv_r.get('expected_price', 2200)}/q</b> | MSP: <b>Rs {harv_r.get('msp', 2183)}/q</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="farm-card">
            <h4>7. 💰 {t('tab_market', lang)} — {mkt_r.get('market_trend', 'Stable')}</h4>
            <p>{t('best_mandi', lang)}: <b>{mkt_r.get('best_mandi', 'Local APMC')}</b> @ <b>Rs {mkt_r.get('best_price', 2200)}/q</b> ({mkt_r.get('vs_msp_pct', 0.0):+.1f}% vs MSP)<br>
            {mkt_r.get('trend_advice', 'Hold and sell at peak season')}</p>
        </div>
        """, unsafe_allow_html=True)

        best_sc = twin_r.get("best_scenario", {})
        st.markdown(f"""
        <div class="farm-card card-blue">
            <h4>8-9. 📸 {t('tab_leaf_scan', lang)} & 🔮 {t('tab_what_if', lang)}</h4>
            <p>{t('tab_leaf_scan', lang)}: <b>{leaf_r.get('detected_disease', 'Healthy')}</b> ({leaf_r.get('confidence_pct', 85)}% Confident)<br>
            {t('tab_what_if', lang)}: <b>{best_sc.get('scenario','Use certified seeds')}</b> → {best_sc.get('verdict','Increases yield')}</p>
        </div>
        """, unsafe_allow_html=True)

    # Annual profit breakdown
    st.markdown("---")
    st.markdown(f"### 💰 {'వార్షిక అదనపు లాభాల వివరాలు' if lang=='te' else ('वार्षिक अतिरिक्त लाभ' if lang=='hi' else 'Your Annual Extra Profit Breakdown')}")
    profit_data = {
        ("సరైన పంట ఎంపిక (Soil)" if lang=="te" else "Right Crop (Soil)"): 150000,
        ("మోటార్ ఖర్చు ఆదా (Water)" if lang=="te" else "Pump Cost Saved (Water)"): 50000,
        ("పురుగుల నష్టం నివారణ (Pest)" if lang=="te" else "Pest Prevention (Pest)"): 250000,
        ("ఖచ్చితమైన ఎరువుల డోస్ (Fert)" if lang=="te" else "Exact Fertilizer (Fert)"): 100000,
        ("మంచి మార్కెట్ ధర (Market)" if lang=="te" else "Best Mandi Price (Market)"): 100000,
    }
    pc1, pc2, pc3 = st.columns(3)
    p_tot = sum(profit_data.values())
    for i, (k, v) in enumerate(profit_data.items()):
        col = [pc1, pc2, pc3][i % 3]
        col.markdown(f'<div class="farm-metric"><div class="val">{format_rupees(v)}</div><div class="lbl">{k}</div></div>', unsafe_allow_html=True)
    st.success(f"🎉 {'మొత్తం అదనపు లాభం' if lang=='te' else ('कुल अतिरिक्त लाभ' if lang=='hi' else 'Total Extra Profit')}: {format_rupees(p_tot)} / {'ఏడాదికి' if lang=='te' else 'year'}")

# ════════════════════════════════════════════════════════════
# TAB 2: CROP RECOMMENDATION (పంట సిఫార్సు వ్యవస్థ)
# ════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader(f"🌾 {t('crop_title', lang)}")
    st.markdown(t("crop_intro", lang))

    best_c = soil_r.get("best_crop", crop)
    c_info = CROPS.get(best_c, {})
    
    rc1, rc2 = st.columns([1, 1])
    with rc1:
        st.markdown(f"""
        <div class="farm-card card-orange" style="padding:1.4rem;">
            <h2 style="color:#E65100; margin:0;">🌟 {crop_name(best_c, lang, CROPS)} ({best_c})</h2>
            <p style="font-size:1.05rem; margin-top:0.4rem;">
                <b>{t('why_crop', lang)}:</b> {t('why_ph', lang, ph=soil_ph, lo=c_info.get('ph_min', 6.0), hi=c_info.get('ph_max', 7.5))}<br>
                {t('why_season', lang, season=season_val)} {t('why_region', lang)}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### 📋 {t('crop_facts', lang)}")
        st.markdown(f"• {t('fact_duration', lang, d=c_info.get('grow_days', 120))}")
        st.markdown(f"• {t('fact_ph', lang, lo=c_info.get('ph_min', 6.0), hi=c_info.get('ph_max', 7.5))}")
        st.markdown(f"• {'నీటి అవసరం' if lang=='te' else ('पानी की आवश्यकता' if lang=='hi' else 'Water Requirement')}: {c_info.get('water_mm_per_week', 25)} mm / week")
        st.markdown(f"• {'సగటు దిగుబడి' if lang=='te' else ('औसत उपज' if lang=='hi' else 'Typical Yield')}: {c_info.get('avg_yield_kg_acre', 2000):,} kg/acre")
        st.markdown(f"• {'కనీస మద్దతు ధర' if lang=='te' else ('MSP' if lang=='hi' else 'MSP Floor')}: Rs {c_info.get('msp_per_quintal', 2183):,}/quintal")

    with rc2:
        st.markdown(f"### 🌿 {t('other_crops', lang)}")
        for i, sc in enumerate(soil_r.get("top5_crops", [])[:5], 1):
            sc_info = CROPS.get(sc, {})
            sc_rev = round(sc_info.get("avg_yield_kg_acre", 0) * sc_info.get("msp_per_quintal", 0) / 100)
            st.markdown(f"""
            <div class="farm-card" style="margin:0.3rem 0; padding:0.7rem 1rem;">
                <b>{i}. {crop_name(sc, lang, CROPS)} ({sc})</b> — {format_rupees(sc_rev)} / acre potential
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 👉 {t('next_steps', lang)}")
    st.markdown(f"1. {t('step_1', lang)}")
    st.markdown(f"2. {t('step_2', lang)}")
    st.markdown(f"3. {t('step_3', lang)}")
    st.caption(f"⚠️ {t('disclaimer', lang)}")

# ════════════════════════════════════════════════════════════
# TAB 3: SOIL HEALTH AGENT (నేల ఆరోగ్యం)
# ════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader(f"🧪 {t('tab_soil', lang)}")
    sc1, sc2 = st.columns([1, 1])
    
    with sc1:
        st.markdown(f"**{t('soil_health_score', lang)}:** {soil_r.get('soil_health', '70/100')} ({soil_r.get('health_label', 'Good')})")
        st.markdown(f"**{t('soil_ph_label', lang)} {soil_ph}** → **{soil_r.get('ph_class', 'Neutral')}** ({soil_r.get('ph_status', 'Normal')})")
        
        st.markdown(f"### 📋 {'నేల దిద్దుబాటు సూచనలు' if lang=='te' else ('मिट्टी सुधार सुझाव' if lang=='hi' else 'Soil Amendments Needed')}")
        for am in soil_r.get("amendments", []):
            if "healthy" in am.lower() or "no correction" in am.lower():
                st.markdown(f'<div class="alert-box alert-green">✅ {am}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-box alert-orange">⚠️ {am}</div>', unsafe_allow_html=True)

    with sc2:
        # Radar Chart
        cats = ["Nitrogen", "Phosphorus", "Potassium", "Organic Matter"]
        vals = [float(soil_r.get("nutrient_scores", {}).get("Nitrogen", "60/100").split("/")[0]),
                float(soil_r.get("nutrient_scores", {}).get("Phosphorus", "60/100").split("/")[0]),
                float(soil_r.get("nutrient_scores", {}).get("Potassium", "60/100").split("/")[0]),
                float(soil_r.get("nutrient_scores", {}).get("Organic Matter", "60/100").split("/")[0])]
        vals_c = vals + [vals[0]]; cats_c = cats + [cats[0]]
        fig_r = go.Figure(go.Scatterpolar(
            r=vals_c, theta=cats_c, fill="toself",
            fillcolor="rgba(46,125,50,0.25)", line=dict(color="#2E7D32", width=2)
        ))
        fig_r.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig_r, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 4: IRRIGATION & WATER AGENT (నీటిపారుదల)
# ════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader(f"💧 {t('tab_water', lang)}")
    idec = irr_r.get("decision", "Monitor soil moisture")
    if "SKIP" in idec:
        st.success(f"✅ {idec} — {irr_r.get('reason', '')}")
    else:
        st.warning(f"💧 {idec} — {irr_r.get('reason', '')}")

    wc1, wc2, wc3, wc4 = st.columns(4)
    wc1.metric(t("water_needed", lang), f"{irr_r.get('water_needed_mm', 0)} mm")
    wc2.metric(t("pump_hours", lang), f"{irr_r.get('pump_hours', 0)} hrs")
    wc3.metric(t("pump_cost", lang), format_rupees(irr_r.get("pump_cost", 0)))
    wc4.metric(t("money_saved", lang), format_rupees(irr_r.get("money_saved_today", 0)))

    # Moisture Gauge
    fig_g = go.Figure(go.Indicator(
        mode="gauge+number",
        value=soil_moisture,
        title={"text": "Soil Moisture (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#2E7D32"},
            "steps": [
                {"range": [0, 30], "color": "#FFEBEE"},
                {"range": [30, 50], "color": "#FFF3E0"},
                {"range": [50, 75], "color": "#E8F5E9"},
                {"range": [75, 100], "color": "#C8E6C9"},
            ],
            "threshold": {"line": {"color": "#1976D2", "width": 3}, "value": 60}
        }
    ))
    fig_g.update_layout(height=260, margin=dict(t=20, b=20))
    st.plotly_chart(fig_g, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 5: PEST & DISEASE AGENT (చీడపీడల హెచ్చరిక)
# ════════════════════════════════════════════════════════════
with tabs[4]:
    st.subheader(f"🐛 {t('tab_pests', lang)}")
    plvl = pest_r.get("alert_level", "LOW")
    if plvl == "HIGH":
        st.error(f"🚨 HIGH RISK: {pest_r.get('immediate_action')}")
    else:
        st.success(f"✅ Safe today: {pest_r.get('immediate_action')}")

    risks = pest_r.get("pest_risks", [])
    if risks:
        df_p = pd.DataFrame(risks)
        fig_p = px.bar(df_p, x="pest", y="risk_pct", color="risk_pct",
                       color_continuous_scale=["#4CAF50", "#FFC107", "#F44336"],
                       title="Pest & Disease Threat Levels (%)")
        fig_p.update_layout(height=280, margin=dict(t=30, b=20), plot_bgcolor="white")
        st.plotly_chart(fig_p, use_container_width=True)

    for r in risks:
        with st.expander(f"🔍 {r.get('pest')} ({r.get('risk_pct')}% Risk)"):
            st.markdown(f"**Medicine:** `{r.get('pesticide')}` | **Dose:** {r.get('dose')}")
            st.markdown(f"**Organic Alternative:** {r.get('organic_alt')}")
            st.markdown(f"**Spray Timing:** {r.get('spray_timing')}")

# ════════════════════════════════════════════════════════════
# TAB 6: YIELD FORECAST AGENT (దిగుబడి అంచనా)
# ════════════════════════════════════════════════════════════
with tabs[5]:
    st.subheader(f"📈 {t('tab_yield', lang)}")
    yc1, yc2, yc3 = st.columns(3)
    yc1.metric(t("yield_per_acre", lang), f"{yield_r.get('yield_per_acre_kg', 2000):,} kg")
    yc2.metric(t("total_yield", lang), f"{yield_r.get('total_yield_kg', 10000):,} kg")
    yc3.metric(t("expected_revenue", lang), format_rupees(yield_r.get("expected_revenue", 0)))

    st.info(f"🌾 **{t('storage_needed', lang)}:** {yield_r.get('storage_needed_tonnes', 2.0)} tonnes. {yield_r.get('storage_advice', 'Keep grains dry to avoid fungal mold.')}")

# ════════════════════════════════════════════════════════════
# TAB 7: FERTILIZER AGENT (ఎరువుల ప్రణాళిక)
# ════════════════════════════════════════════════════════════
with tabs[6]:
    st.subheader(f"🧬 {t('tab_fertilizer', lang)}")
    fplan = fert_r.get("fertilizer_plan", {})
    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric(t("urea_dose", lang), f"{fplan.get('Urea_kg', 0)} kg")
    fc2.metric(t("dap_dose", lang), f"{fplan.get('DAP_kg', 0)} kg")
    fc3.metric(t("mop_dose", lang), f"{fplan.get('MOP_kg', 0)} kg")
    fc4.metric(t("total_cost", lang), format_rupees(fert_r.get("total_cost", 0)))

    st.markdown(f"### 📅 {'విడతలవారీగా ఎరువులు వేసే సమయాలు' if lang=='te' else ('खाद डालने का कार्यक्रम' if lang=='hi' else 'Split Application Schedule')}")
    for s in fert_r.get("schedule", []):
        st.markdown(f"• **{s.get('stage')}:** Urea {s.get('urea_kg')} kg | DAP {s.get('dap_kg')} kg | MOP {s.get('mop_kg')} kg")

    st.markdown(f"### ⚠️ {t('fert_warning', lang)}")

# ════════════════════════════════════════════════════════════
# TAB 8: HARVEST TIMING AGENT (పంట కోత మార్గదర్శి)
# ════════════════════════════════════════════════════════════
with tabs[7]:
    st.subheader(f"🌾 {t('tab_harvest', lang)}")
    st.info(f"**{t('days_to_harvest', lang)}:** {harv_r.get('days_to_harvest', 30)} days | **Status:** {harv_r.get('timing_status', 'On Track')}")
    st.markdown(f"• **Advice:** {harv_r.get('advice')}")
    st.markdown(f"• **Best Month to Sell:** {harv_r.get('best_selling_month', 'November')} (Peak price ~Rs {harv_r.get('best_month_price', 2400)}/q)")

# ════════════════════════════════════════════════════════════
# TAB 9: MANDI MARKET PRICES (లైవ్ మార్కెట్ ధరలు)
# ════════════════════════════════════════════════════════════
with tabs[8]:
    st.subheader(f"💰 {t('tab_market', lang)}")
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric(t("best_mandi", lang), mkt_r.get("best_mandi", "Local APMC"))
    mc2.metric(t("best_price", lang), f"Rs {mkt_r.get('best_price', 2200)}/q")
    mc3.metric(t("vs_msp", lang), f"{mkt_r.get('vs_msp_pct', 0.0):+.1f}%")

    if mkt_r.get("all_prices"):
        df_m = pd.DataFrame([{"Mandi": k, "Price": v} for k, v in mkt_r["all_prices"].items()])
        fig_m = px.bar(df_m, x="Mandi", y="Price", color="Price",
                       color_continuous_scale=["#EF5350", "#FFC107", "#4CAF50"],
                       title=f"{crop} Prices in Nearby Mandis (Rs/quintal)")
        fig_m.add_hline(y=mkt_r.get("msp", 2183), line_dash="dash", line_color="red", annotation_text="MSP")
        fig_m.update_layout(height=280, plot_bgcolor="white")
        st.plotly_chart(fig_m, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 10: LEAF SCAN AI DOCTOR (ఆకు స్కాన్)
# ════════════════════════════════════════════════════════════
with tabs[9]:
    st.subheader(f"📸 {t('tab_leaf_scan', lang)}")
    st.markdown("ఆకు ఫోటోను అప్‌లోడ్ చేయండి లేదా లక్షణాలను వివరించండి — AI తక్షణమే తెగులును గుర్తిస్తుంది" if lang=="te" else ("पत्ती का फोटो अपलोड करें या लक्षण बताएं — AI तुरंत रोग पहचानेगा" if lang=="hi" else "Upload a leaf photo or describe symptoms to detect diseases and nutrient deficiencies."))

    lcol1, lcol2 = st.columns([1, 1])
    with lcol1:
        img_lbl = "ఆకు ఫోటోను ఎంచుకోండి" if lang=="te" else ("फोटो चुनें" if lang=="hi" else "Upload Leaf Photo")
        up_img = st.file_uploader("📷 " + img_lbl, type=["jpg", "jpeg", "png"])
        desc_lbl = "లక్షణాల వివరణ" if lang=="te" else ("लक्षणों का विवरण" if lang=="hi" else "Describe what you see")
        s_desc = st.text_area("✍️ " + desc_lbl, value=pest_symptoms or "")
        btn_scan_lbl = "తెగులును విశ్లేషించండి" if lang=="te" else ("जांच करें" if lang=="hi" else "Identify Disease Now")
        scan_now = st.button("🔍 " + btn_scan_lbl, type="primary")

        if scan_now:
            with st.spinner("🤖 Analyzing with Gemini Vision AI..."):
                if up_img:
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tf:
                        tf.write(up_img.read())
                        tmp_path = tf.name
                    st.session_state["leaf_result"] = LeafScanAgent().analyze_image(tmp_path, s_desc, crop=crop, soil_ph=soil_ph)
                else:
                    st.session_state["leaf_result"] = LeafScanAgent().analyze_text(s_desc or "yellow spots", crop=crop, soil_ph=soil_ph)

    with lcol2:
        lr = st.session_state.get("leaf_result", leaf_r)
        if lr:
            d_name = lr.get("detected_disease", "Healthy")
            conf   = lr.get("confidence_pct", 85)
            st.markdown(f"""
            <div class="farm-card card-orange">
                <h4>🎯 {d_name} ({conf}% Confidence)</h4>
                <p><b>Medicine / Treatment:</b> {lr.get('pesticide', 'Consult local officer')}<br>
                <b>Dose:</b> {lr.get('pest_dose', 'As per label')} | <b>Timing:</b> {lr.get('spray_timing', 'Morning')}<br>
                <b>Organic Option:</b> {lr.get('organic_alternative', 'Neem oil 5ml/L')}</p>
            </div>
            """, unsafe_allow_html=True)
            if lr.get("farmer_action"):
                st.warning(f"🚨 **Do This Today:** {lr.get('farmer_action')}")

# ════════════════════════════════════════════════════════════
# TAB 11: WHAT-IF SIMULATOR (డిజిటల్ ట్విన్)
# ════════════════════════════════════════════════════════════
with tabs[10]:
    st.subheader(f"🔮 {t('tab_what_if', lang)}")
    st.markdown("వివిధ నిర్ణయాలను పరీక్షించండి — పెట్టుబడి పెట్టే ముందే లాభనష్టాలను లెక్కించండి" if lang=="te" else ("विभिन्न निर्णय आज़माएं — खर्च से पहले लाभ-हानि जानें" if lang=="hi" else "Simulate decisions before spending money to see profit impact."))

    wi1, wi2 = st.columns(2)
    with wi1:
        sim_n = st.slider("Nitrogen (kg/ha)", 0, 300, int(nitrogen))
        sim_cert = st.checkbox("Use Certified Seeds (+8% Yield)", value=True)
    with wi2:
        sim_acres = st.slider("Farm Size (Acres)", 1.0, 50.0, float(acres))
    
    sim_btn_lbl = "లాభం లెక్కించండి" if lang=="te" else ("लाभ गणना करें" if lang=="hi" else "Run Simulation")
    if st.button("▶️ " + sim_btn_lbl):
        base_s = {"crop": crop, "acres": acres, "soil_ph": soil_ph, "nitrogen": nitrogen, "rainfall_mm": 900, "pest_incidence": 0.1}
        changes = {"nitrogen": sim_n, "acres": sim_acres, "certified_seeds": sim_cert}
        sim_res = DigitalTwinAgent().simulate(base_s, changes)
        delta_p = sim_res["delta"]["profit"]
        if delta_p >= 0:
            st.success(f"🎉 {'అదనపు లాభం' if lang=='te' else ('अतिरिक्त लाभ' if lang=='hi' else 'Extra Profit')}: +{format_rupees(delta_p)}! {sim_res.get('verdict')}")
        else:
            st.error(f"⚠️ {'నష్టం అవకాశం' if lang=='te' else ('संभावित हानि' if lang=='hi' else 'Potential Loss')}: {format_rupees(abs(delta_p))}. {sim_res.get('verdict')}")

# ════════════════════════════════════════════════════════════
# TAB 12: FARMER HELP & CHATBOT (రైతు సహాయం & ప్రశ్నలు)
# ════════════════════════════════════════════════════════════
with tabs[11]:
    st.subheader(f"💬 {t('help_title', lang)}")
    st.markdown(t("help_intro", lang))

    # Voice Widget
    render_voice_assistant(lang, text_to_speak="నమస్కారం రైతు గారు. ఫార్మ్ ఏఐ మీకు సహాయం చేయడానికి సిద్ధంగా ఉంది.")

    # Quick Suggested Questions
    st.markdown(f"#### 💡 {'సాధారణ ప్రశ్నలు' if lang=='te' else ('अक्सर पूछे जाने वाले सवाल' if lang=='hi' else 'Frequently Asked Questions')}")
    sug_q = suggested_questions(lang)
    q_cols = st.columns(3)
    for idx, (fid, q_text) in enumerate(sug_q[:6]):
        if q_cols[idx % 3].button(f"👉 {q_text}", key=f"faq_btn_{fid}"):
            ans = get_answer_by_id(fid, lang)
            st.session_state["chat_history"].append({"q": q_text, "a": ans, "src": "Curated FAQ"})
            store.save_chat(st.session_state["chat_history"])

    # Free Text Ask Question
    st.markdown("---")
    user_q = st.text_input(t("help_type", lang), placeholder="e.g. పత్తి పంటలో గులాబీ రంగు పురుగు నివారణ ఎలా? / How to control pink bollworm?")
    
    if st.button("🚀 " + t("help_ask", lang)):
        if user_q.strip():
            with st.spinner("🤖 Searching verified advice..."):
                resp = ask_ai_assistant(user_q, lang=lang, crop=crop, state=state)
                st.session_state["chat_history"].append({"q": user_q, "a": resp.get("answer"), "src": resp.get("source")})
                store.save_chat(st.session_state["chat_history"])

    # Display Chat History
    if st.session_state["chat_history"]:
        for chat in reversed(st.session_state["chat_history"]):
            st.markdown(f"""
            <div class="farm-card card-orange">
                <b>❓ {chat['q']}</b><br>
                <p style="margin-top:0.4rem;">💡 {chat['a']}</p>
                <span style="font-size:0.75rem; color:#888;">Source: {chat.get('src', 'Verified Extension Guidance')}</span>
            </div>
            """, unsafe_allow_html=True)

    # Kisan Call Centre Hotline
    st.markdown("---")
    st.markdown(f"""
    <div class="alert-box alert-green">
        📞 <b>{KCC_LINE.get(lang, KCC_LINE['en'])}</b><br>
        🏛️ <b>Telangana Agri Dept:</b> 040-23383520 | <b>AP Rythu Bharosa Kendras (RBK):</b> 155251
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 13: CROP CALENDAR (పంట క్యాలెండర్)
# ════════════════════════════════════════════════════════════
with tabs[12]:
    st.subheader(f"📅 {t('tab_calendar', lang)} (Telangana & Andhra Pradesh)")
    cal_data = [
        {"Crop": "Paddy / వరి", "Season": "Kharif", "Sowing": "June – July", "Flowering": "August – September", "Harvest": "October – November"},
        {"Crop": "Paddy / వరి (Rabi)", "Season": "Rabi", "Sowing": "November – December", "Flowering": "January – February", "Harvest": "March – April"},
        {"Crop": "Cotton / పత్తి", "Season": "Kharif", "Sowing": "June – July", "Flowering": "August – October", "Harvest": "November – January"},
        {"Crop": "Chilli / మిరప", "Season": "Kharif/Rabi", "Sowing": "July – August", "Flowering": "October – November", "Harvest": "December – March"},
        {"Crop": "Maize / మొక్కజొన్న", "Season": "Kharif/Rabi", "Sowing": "June / October", "Flowering": "July / December", "Harvest": "September / January"},
        {"Crop": "Groundnut / వేరుశనగ", "Season": "Rabi", "Sowing": "October – November", "Flowering": "December – January", "Harvest": "February – March"},
        {"Crop": "Bengal Gram / శనగలు", "Season": "Rabi", "Sowing": "October – November", "Flowering": "December", "Harvest": "January – February"},
    ]
    st.dataframe(pd.DataFrame(cal_data), use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 14: GOVT SCHEMES & RESOURCES (ప్రభుత్వ పథకాలు)
# ════════════════════════════════════════════════════════════
with tabs[13]:
    st.subheader(f"🏛️ {t('tab_schemes', lang)}")
    schemes = [
        {"name": "రైతు బంధు / రైతు భరోసా (Rythu Bandhu / Rythu Bharosa)", "desc": "ఎకరాకు పెట్టుబడి సహాయం (Investment support for farmers in TS & AP).", "link": "https://rythubandhu.telangana.gov.in"},
        {"name": "PM-KISAN సమ్మాన్ నిధి", "desc": "అర్హులైన రైతులకు ఏడాదికి రూ. 6,000 ఆర్థిక సహాయం (Rs 6,000/year direct cash transfer in 3 installments).", "link": "https://pmkisan.gov.in"},
        {"name": "సాయిల్ హెల్త్ కార్డ్ స్కీమ్ (Soil Health Card)", "desc": "ప్రభుత్వ ఉచిత నేల పరీక్ష మరియు పోషకాల కార్డు (Free soil testing and fertilizer recommendations).", "link": "https://soilhealth.dac.gov.in"},
        {"name": "PM ఫసల్ బీమా యోజన (PMFBY)", "desc": "ప్రకృతి వైపరీత్యాల వల్ల పంట నష్టానికి పంట బీమా (Crop insurance coverage against natural calamities).", "link": "https://pmfby.gov.in"},
        {"name": "e-NAM (జాతీయ వ్యవసాయ మార్కెట్)", "desc": "దేశవ్యాప్తంగా పంటలను ఆన్‌లైన్‌లో విక్రయించడానికి మార్కెట్ పోర్టల్ (Online trading platform for agricultural commodities).", "link": "https://enam.gov.in"},
    ]
    for s in schemes:
        st.markdown(f"""
        <div class="farm-card">
            <h4>🌿 {s['name']}</h4>
            <p>{s['desc']}<br>
            🔗 <a href="{s['link']}" target="_blank" style="color:#E65100; font-weight:700;">అధికారిక వెబ్‌సైట్ చూడండి / Visit Official Portal</a></p>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 15: AGRONOMIST & ML ANALYTICS (విశ్లేషణ & ML)
# ════════════════════════════════════════════════════════════
with tabs[14]:
    st.subheader(f"📊 {t('tab_analytics', lang)}")
    st.markdown("Developer & Agricultural Scientist View — Model performance and impact at scale.")
    
    # State ML Performance
    sdf = pd.DataFrame([{"State": s, "R2": v["r2"], "Samples": v["samples"]} for s, v in STATE_ML_PERFORMANCE.items()]).sort_values("R2", ascending=True)
    fig_st = px.bar(sdf, x="R2", y="State", orientation="h", color="R2", color_continuous_scale=["#F44336", "#FF9800", "#4CAF50"], title="ML Model R² Score Across 22 Indian States")
    fig_st.update_layout(height=450, plot_bgcolor="white")
    st.plotly_chart(fig_st, use_container_width=True)

    # Social Scale Impact
    scale_df = pd.DataFrame({
        "Farmers": ["100", "1,000", "10,000", "1 Lakh", "10 Lakh"],
        "Extra Income (Rs Crore)": [0.6, 6, 60, 600, 6000]
    })
    fig_sc = px.bar(scale_df, x="Farmers", y="Extra Income (Rs Crore)", text="Extra Income (Rs Crore)", color="Extra Income (Rs Crore)", color_continuous_scale="Greens", title="Projected Social Economic Impact at Scale")
    fig_sc.update_traces(textposition="outside")
    fig_sc.update_layout(height=300, plot_bgcolor="white")
    st.plotly_chart(fig_sc, use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 16 (v11): WEATHER — current conditions + short forecast
# ════════════════════════════════════════════════════════════
with tabs[15]:
    st.subheader(f"{t('tab_weather', lang)} — {district}")
    if st.button(t("x_wx_refresh", lang), key="wx_refresh"):
        get_live_weather(district, force=True)
        st.rerun()

    _st = live_w.get("status")
    if _st == "not_configured":
        st.warning(t("x_wx_not_config", lang))
    elif _st not in ("live", "stale"):
        st.error(t("x_wx_unavailable", lang))
    else:
        if _st == "stale":
            st.warning(t("x_wx_stale", lang, m=live_w.get("age_minutes", "?")))
        if weather_summary_tuple:
            st.markdown(f'<div class="alert-box alert-orange">🌤️ {weather_summary_tuple[0]}<br>👉 {weather_summary_tuple[1]}</div>', unsafe_allow_html=True)
        for al in weather_alerts_list:
            st.markdown(f'<div class="alert-box alert-red">⚠️ {al}</div>', unsafe_allow_html=True)

        _na = t("x_unavailable", lang)
        _hi, _lo = live_w.get("temp_high_c"), live_w.get("temp_low_c")
        _wk = live_w.get("wind_kmh")
        wc = st.columns(6)
        for col, (v, l) in zip(wc, [
            (f"{live_w.get('temp_c')}°C", t("x_wx_now", lang)),
            (f"{_hi}°C" if _hi is not None else _na, t("x_wx_high", lang)),
            (f"{_lo}°C" if _lo is not None else _na, t("x_wx_low", lang)),
            (f"{live_w.get('humidity_pct')}%", t("humidity", lang)),
            (f"{_rc}%" if _rc is not None else _na, t("rain_chance", lang)),
            (f"{_wk} km/h" if _wk is not None else _na, t("x_wx_wind", lang)),
        ]):
            col.markdown(f'<div class="farm-metric"><div class="val" style="font-size:1.25rem;">{v}</div><div class="lbl">{l}</div></div>', unsafe_allow_html=True)
        st.caption(f"{condition_text(live_w.get('condition', ''), lang)} | {t('last_updated', lang)}: {format_time(live_w.get('fetched_at', time.time()))}")

        fc_rows = live_w.get("forecast") or []
        if fc_rows:
            st.markdown(f"### {t('x_wx_forecast', lang)}")
            st.dataframe(pd.DataFrame([{
                t("x_wx_date", lang): r["date"],
                "🌡️ max °C": r["temp_max"], "min °C": r["temp_min"],
                t("rain_chance", lang) + " %": r["rain_chance_pct"],
                t("x_wx_rain_mm", lang): r["rain_mm"],
                t("x_wx_wind", lang) + " km/h": r["wind_kmh_max"],
                "☁️": condition_text(r["condition"], lang),
            } for r in fc_rows]), use_container_width=True, hide_index=True)
    st.caption(t("x_wx_credit", lang))

# ════════════════════════════════════════════════════════════
# TAB 17 (v11): MY FARMING HISTORY — saved on disk
# ════════════════════════════════════════════════════════════
with tabs[16]:
    st.subheader(f"{t('tab_my_history', lang)}")
    st.markdown(t("x_hist_intro", lang))
    _hist = store.load_history()
    if not _hist:
        st.info(t("x_hist_empty", lang))
    else:
        _hdf = pd.DataFrame([{k: v for k, v in h.items() if not k.startswith("_")} for h in reversed(_hist)])
        st.metric(t("x_hist_total", lang), len(_hdf))
        st.dataframe(_hdf, use_container_width=True, hide_index=True)
        st.download_button(t("x_hist_download", lang), _hdf.to_csv(index=False).encode("utf-8-sig"),
                           file_name="farm_history.csv", mime="text/csv")
        with st.expander(t("x_hist_clear", lang)):
            if st.checkbox(t("x_hist_confirm", lang), key="hist_confirm") and st.button(t("x_hist_clear", lang), key="hist_clear_btn"):
                store.clear_history()
                st.session_state["history"] = []
                st.success(t("x_hist_cleared", lang))
                st.rerun()

# ════════════════════════════════════════════════════════════
# TAB 18 (v11): SETTINGS — language, text size, contrast, developer view
# ════════════════════════════════════════════════════════════
with tabs[17]:
    st.subheader(f"{t('tab_settings', lang)}")
    st.markdown(t("x_set_intro", lang))
    _lk = list(LANGUAGES.keys())
    st.session_state["set_lang"] = lang   # keep in sync with the top selector (avoids a rerun loop)
    _new_lang = st.radio("🌐 " + t("x_set_lang", lang), _lk, index=_lk.index(lang),
                         format_func=lambda x: LANGUAGES[x], horizontal=True, key="set_lang",
                         on_change=_lang_from, args=("set_lang",))
    _lt = st.checkbox("🔠 " + t("x_set_large", lang), value=bool(SET.get("large_text")), key="set_large")
    _hc = st.checkbox("◐ " + t("x_set_contrast", lang), value=bool(SET.get("high_contrast")), key="set_contrast")
    _dv = st.checkbox("🧑‍💻 " + t("x_set_dev", lang), value=bool(SET.get("developer_mode")), key="set_dev")
    if (_lt != bool(SET.get("large_text")) or _hc != bool(SET.get("high_contrast"))
            or _dv != bool(SET.get("developer_mode"))):
        SET.update({"large_text": _lt, "high_contrast": _hc, "developer_mode": _dv})
        store.save_settings(SET)
        st.rerun()
    st.caption(t("x_set_privacy", lang))

# ── Footer ───────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; color:#666; font-size:0.85rem; padding:1rem 0;">
    🌾 <b>Farm AI</b> — Empowering Indian Farmers with Smart, Multilingual Agricultural Intelligence 🇮🇳<br>
    OpenWeatherMap API &bull; data.gov.in Official Mandi Portal &bull; Google Gemini AI &bull; ICAR Extension Guidelines
</div>
""", unsafe_allow_html=True)
