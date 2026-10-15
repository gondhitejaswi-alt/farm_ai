"""
============================================================
FARM AI v9 → v10 UPGRADE PATCH
============================================================
This file contains REPLACEMENT CODE for streamlit_app.py.

HOW TO APPLY:
1. Open: farm_ai/dashboard/streamlit_app.py
2. Follow the steps below — find the old code, replace with new.

STEP 1: Add ANTHROPIC_API_KEY to .env
STEP 2: pip install anthropic
STEP 3: Replace 3 sections in streamlit_app.py (shown below)
STEP 4: Run app normally: py -m streamlit run dashboard/streamlit_app.py
============================================================
"""

# ============================================================
# SECTION A — Replace the run_agents() function (around line 230)
# FIND this block:
#
#   "pest":    safe(lambda: PestAgent().analyze(crop, temp, humidity, rain, stage, symp, acres)),
#
# REPLACE the ENTIRE "pest" and "leaf" lines with:
# ============================================================

SECTION_A_OLD = '''        "pest":    safe(lambda: PestAgent().analyze(crop, temp, humidity, rain, stage, symp, acres)),'''

SECTION_A_NEW = '''        # Leaf scan runs first (text-based, no image upload at this stage)
        "leaf":    safe(lambda: LeafScanAgent().analyze_text(
                           pest_symptoms or "healthy leaves", crop,
                           soil_ph=soil_ph)),
        # Pest agent now uses leaf scan result + weather
        "pest":    safe(lambda: PestAgent().analyze(
                           leaf_scan_result=_leaf_tmp,
                           weather={"temperature_c": temp, "humidity_pct": humidity, "rainfall_mm": rain},
                           crop=crop, growth_stage=stage, acres=acres, soil_ph=soil_ph)),'''

# NOTE: Also update the run_agents function signature to handle the dependency:
# After the line:   "leaf": safe(lambda: ...) 
# The pest agent needs the leaf result. Because of caching, we do it slightly differently.
# See SECTION_A_FULL below for the complete replacement.

SECTION_A_FULL_OLD = '''@st.cache_data(show_spinner=False, ttl=300)
def run_agents(crop, state, acres, soil_ph, nitrogen, phosphorus, potassium,
               org_matter, days_planted, soil_moisture, pest_symptoms,
               temp, humidity, rain, season, stage, wind_kmh, solar_rad):
    symp = [pest_symptoms] if pest_symptoms and len(pest_symptoms) > 2 else []
    def safe(fn):
        try: return fn()
        except Exception as e: return {\"error\": str(e), \"action\": f\"Agent error: {e}\",
                                       \"advice\":\"\", \"decision\":\"\", \"reason\":\"\",
                                       \"tip\":\"\", \"alert_level\":\"LOW\",
                                       \"top_threat\":\"None\",\"top_threat_risk\":0,
                                       \"immediate_action\":\"No data\",\"pest_risks\":[],
                                       \"high_risk_pests\":[],\"total_spray_cost\":0,'''

# ============================================================
# SECTION B — Complete replacement for run_agents function
# Find the ENTIRE run_agents function and replace with this:
# ============================================================

SECTION_B_COMPLETE = '''
@st.cache_data(show_spinner=False, ttl=300)
def run_agents(crop, state, acres, soil_ph, nitrogen, phosphorus, potassium,
               org_matter, days_planted, soil_moisture, pest_symptoms,
               temp, humidity, rain, season, stage, wind_kmh, solar_rad):
    """Run all 9 farm AI agents. Leaf scan and pest agent are now integrated."""

    def safe(fn, fallback=None):
        try:
            return fn()
        except Exception as e:
            base = {"error": str(e), "action": f"Agent error: {e}",
                    "advice": "", "decision": "", "reason": "",
                    "tip": "", "alert_level": "LOW",
                    "top_threat": "None", "top_threat_risk": 0,
                    "immediate_action": "No data", "pest_risks": [],
                    "high_risk_pests": [], "total_spray_cost": 0,
                    "risk_level": "LOW", "detected_disease": "Error",
                    "pesticide": "N/A", "dose": "N/A", "confidence": 0,
                    "recommendation": "Agent error — restart app",
                    "action_today": "Restart the application",
                    "weather_notes": [], "stage_watch": [],
                    "source": "Error"}
            if fallback:
                base.update(fallback)
            return base

    # Run leaf scan FIRST (text-based using sidebar symptoms)
    leaf_result = safe(lambda: LeafScanAgent().analyze_text(
        pest_symptoms or "healthy leaves",
        crop=crop,
        soil_ph=soil_ph
    ))

    # Fertilizer agent now receives leaf scan result for deficiency correction
    fert_result = safe(lambda: FertilizerAgent().analyze(
        crop=crop, acres=acres,
        current_n=nitrogen, current_p=phosphorus, current_k=potassium,
        soil_ph=soil_ph, season=season,
        leaf_scan_result=leaf_result,
        days_since_planting=days_planted
    ))

    # Pest agent uses leaf scan result + weather
    pest_result = safe(lambda: PestAgent().analyze(
        leaf_scan_result=leaf_result,
        weather={"temperature_c": temp, "humidity_pct": humidity, "rainfall_mm": rain},
        crop=crop, growth_stage=stage, acres=acres, soil_ph=soil_ph
    ))

    return {
        "soil":    safe(lambda: SoilAgent().analyze(soil_ph, nitrogen, phosphorus, potassium,
                                       state, season, org_matter, crop)),
        "irr":     safe(lambda: IrrigationAgent().analyze(crop, soil_moisture, rain, temp,
                                             humidity, stage, 80, acres,
                                             wind_kmh=wind_kmh, solar_rad=solar_rad)),
        "pest":    pest_result,
        "yield":   safe(lambda: YieldAgent().analyze(state, crop, acres, soil_ph, nitrogen,
                                        phosphorus, potassium, rain, temp, humidity,
                                        wind_speed=wind_kmh, solar_rad=solar_rad)),
        "fert":    fert_result,
        "harvest": safe(lambda: HarvestAgent().analyze(crop, max(0, CROPS.get(crop,{}).get("grow_days",120) - days_planted),
                                          20, rain_next_7days_mm=rain * 2, temp_c=temp,
                                          acres=acres, state=state)),
        "market":  safe(lambda: MarketAgent().analyze(crop, state, acres, season)),
        "leaf":    leaf_result,
        "twin":    safe(lambda: DigitalTwinAgent().run_scenarios({
                       "crop": crop, "acres": acres, "soil_ph": soil_ph,
                       "nitrogen": nitrogen, "rainfall_mm": 900, "pest_incidence": 0.1})),
    }
'''

# ============================================================
# SECTION C — Replace the Leaf Scan TAB (Tab 8 / tabs[8])
# Find: "with tabs[8]:" ... up to "with tabs[9]:"
# Replace with this entire block:
# ============================================================

SECTION_C_LEAF_SCAN_TAB = '''
# ════════════════════════════════════════════════════════════
# TAB 9 — LEAF SCAN (FULLY UPGRADED with Claude Vision)
# ════════════════════════════════════════════════════════════
with tabs[8]:
    st.subheader("📸 Leaf Scan — Upload photo → Get exact medicine")
    st.markdown("""
    **How it works:** Upload a photo of a sick leaf → AI identifies the disease OR nutrient deficiency →
    You get the exact pesticide/fertilizer name, dose, and cost.
    Works for ANY crop, ANY disease, ANY photo.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📷 Upload Leaf Photo")
        uploaded = st.file_uploader(
            "Take a close-up photo of the sick leaf (any angle, daylight is best)",
            type=["jpg", "jpeg", "png"],
            help="Clear close-up photos give best results. Try to capture the spots/patches clearly."
        )

        desc = st.text_area(
            "Describe what you see (optional but helps accuracy)",
            value=pest_symptoms or "",
            placeholder="e.g. yellow spots on edges, white powder, brown patches, purple underside...",
            height=80
        )

        st.markdown(f"**Soil pH being used:** `{soil_ph}` (from sidebar — affects nutrient advice)")

        scan_btn = st.button("🔍 Identify Disease / Deficiency", type="primary", use_container_width=True)

        if scan_btn:
            with st.spinner("🤖 AI analyzing your leaf..."):
                if uploaded:
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                        f.write(uploaded.read())
                        tmp_path = f.name
                    st.session_state["leaf"] = LeafScanAgent().analyze_image(
                        image_path=tmp_path,
                        symptom_description=desc,
                        crop=crop,
                        soil_ph=soil_ph
                    )
                    st.session_state["leaf_has_image"] = True
                else:
                    if not desc or len(desc.strip()) < 3:
                        st.warning("⚠️ Please upload a photo OR describe what you see.")
                        st.stop()
                    st.session_state["leaf"] = LeafScanAgent().analyze_text(
                        description=desc,
                        crop=crop,
                        soil_ph=soil_ph
                    )
                    st.session_state["leaf_has_image"] = False

        # Show uploaded image preview
        if uploaded and "leaf" in st.session_state:
            st.image(uploaded, caption="Your uploaded leaf photo", width=280)

        # Tips
        with st.expander("📌 Tips for better results"):
            st.markdown("""
            - 📱 Take photo in **natural daylight** — avoid shadows
            - 🔍 Get **close-up** — spots/patches should be clearly visible
            - 🌿 **Single leaf** works better than whole plant
            - 🤍 **White background** (paper/cloth) helps AI identify colors
            - 📝 Adding a text description improves accuracy even further
            - 🔁 If confidence is MEDIUM, take another clearer photo
            """)

    with col2:
        res = st.session_state.get("leaf", leaf_r)
        conf = int(res.get("confidence_pct", 0))
        disease = res.get("detected_disease", "Unknown")
        is_deficiency = res.get("is_deficiency", False)
        source = res.get("source", "")

        # ── Confidence banner ─────────────────────────────────────────
        if "error" in res:
            st.error(f"🔴 API Error: {res['error']}")
            st.info("Make sure ANTHROPIC_API_KEY is in your .env file. Run: pip install anthropic")
        elif conf >= 75:
            if is_deficiency:
                st.warning(f"🟡 **NUTRIENT DEFICIENCY: {disease}** ({conf}% confident)")
            else:
                st.error(f"🔴 **DISEASE FOUND: {disease}** ({conf}% confident)")
        elif conf >= 45:
            st.warning(f"🟡 **Possible: {disease}** ({conf}% — try a clearer photo for certainty)")
        else:
            if disease in ["Healthy Crop", "Unknown / Healthy"]:
                st.success(f"🟢 **Crop looks HEALTHY** ({conf}% confident)")
            else:
                st.info(f"ℹ️ **{disease}** — low confidence. Upload a clearer photo.")

        st.caption(f"Analysis method: {source}")

        # ── Results display ───────────────────────────────────────────
        if conf >= 40 and disease not in ["Healthy Crop", "Unknown / Healthy"]:
            # Disease description
            desc_txt = res.get("disease_description", "")
            if desc_txt:
                st.markdown(f"**🔬 What is it:** {desc_txt}")

            st.divider()

            if is_deficiency:
                # NUTRIENT DEFICIENCY path
                st.markdown("### 🧪 Nutrient Treatment")
                st.markdown(f"**Fertilizer to apply:** `{res.get('fertilizer', 'See below')}`")
                st.markdown(f"**How much:** {res.get('fert_dose', 'As per label')}")
                st.markdown(f"**When to apply:** {res.get('spray_timing', 'Immediately')}")
                cost = res.get("cost_per_acre", 0)
                if cost > 0:
                    st.markdown(f"**Cost:** Rs {cost}/acre (Rs {round(cost * acres)} total for {acres} acres)")
                st.markdown(f"**Organic option:** {res.get('organic_alternative', 'Compost/FYM')}")
            else:
                # DISEASE / PEST path
                st.markdown("### 💊 Treatment")
                st.markdown(f"**Pesticide:** `{res.get('pesticide', 'Consult agri officer')}`")
                st.markdown(f"**How much:** {res.get('pest_dose', res.get('dose', 'As per label'))}")
                st.markdown(f"**When to spray:** {res.get('spray_timing', 'Early morning')}")
                cost = res.get("cost_per_acre", 0)
                if cost > 0:
                    st.markdown(f"**Cost:** Rs {cost}/acre (Rs {round(cost * acres)} for {acres} acres)")
                st.markdown(f"**Natural option:** {res.get('organic_alternative', 'Neem oil 5ml/litre')}")

            # pH Note — very important
            ph_note = res.get("ph_note", "")
            if ph_note:
                st.divider()
                st.markdown("### 🧪 pH Impact on This Problem")
                if "HIGH" in ph_note.upper() or "LOW" in ph_note.upper() or "⚠️" in ph_note:
                    st.warning(f"⚠️ {ph_note}")
                else:
                    st.success(f"✅ {ph_note}")

            # Severity + spread
            severity = res.get("severity", "")
            spread = res.get("spread_risk", "")
            if severity or spread:
                st.divider()
                sev_col, spread_col = st.columns(2)
                with sev_col:
                    st.metric("Severity", severity.title() if severity else "Unknown")
                with spread_col:
                    st.metric("Spread Risk", spread if spread else "Unknown")

            # Immediate action box
            action = res.get("farmer_action", "")
            if action:
                st.divider()
                st.markdown(f"""
                <div style="background:#FFF3E0;border-left:4px solid #e65100;
                            padding:0.8rem 1rem;border-radius:8px;margin:0.4rem 0">
                <b>🚨 Do This TODAY:</b> {action}
                </div>
                """, unsafe_allow_html=True)

        elif conf >= 75 and disease in ["Healthy Crop"]:
            st.success("✅ Your crop looks healthy! Keep monitoring every 3 days.")
            st.markdown("**Preventive tips:**")
            st.markdown("- Spray Mancozeb 2g/litre preventively if rains are heavy")
            st.markdown("- Ensure proper drainage — waterlogging causes disease")
            st.markdown("- Avoid excess Nitrogen fertilizer — attracts pests")

        # ── Integration note ──────────────────────────────────────────
        st.divider()
        st.caption("💡 **This result is automatically used by Pest Agent and Fertilizer Agent tabs** — "
                   "they update their recommendations based on what Leaf Scan finds.")
'''

# ============================================================
# SECTION D — Update Fertilizer Tab to show deficiency info
# In tabs[5] (Fertilizer tab), find the warnings display section
# and add this BELOW the existing warnings:
# ============================================================

SECTION_D_FERT_ADDON = '''
        # Show deficiency correction from Leaf Scan
        if fert_r.get("deficiency_note"):
            st.warning(fert_r["deficiency_note"])

        if fert_r.get("deficiency_addon"):
            addon = fert_r["deficiency_addon"]
            with st.expander("🔬 Deficiency Correction (from Leaf Scan)"):
                st.markdown(f"**Deficiency found:** {addon.get('deficiency_found')}")
                st.markdown(f"**Correction fertilizer:** {addon.get('correction_fertilizer')}")
                st.markdown(f"**Dose:** {addon.get('correction_dose')}")
                st.markdown(f"**Apply:** {addon.get('spray_timing')}")
                total_def_cost = addon.get("cost", 0)
                if total_def_cost > 0:
                    st.markdown(f"**Cost:** Rs {round(total_def_cost)}")

        # pH impact on nutrients
        ph_avail = fert_r.get("nutrient_availability", {})
        if ph_avail:
            st.markdown("### 🧪 Nutrient Availability at Current pH")
            pa_col1, pa_col2, pa_col3 = st.columns(3)
            with pa_col1:
                n_pct = ph_avail.get("N_pct", 100)
                color = "normal" if n_pct >= 80 else "inverse"
                st.metric("Nitrogen Available", f"{n_pct}%", delta=None)
            with pa_col2:
                p_pct = ph_avail.get("P_pct", 100)
                st.metric("Phosphorus Available", f"{p_pct}%", delta=None)
            with pa_col3:
                k_pct = ph_avail.get("K_pct", 100)
                st.metric("Potassium Available", f"{k_pct}%", delta=None)

        # Estimated pH after fertilization
        est_ph = fert_r.get("estimated_ph_after")
        if est_ph:
            curr_ph = fert_r.get("soil_ph", soil_ph)
            ph_diff = round(est_ph - curr_ph, 1)
            st.markdown(f"**Estimated pH after this fertilizer application:** `{est_ph}` "
                        f"(change: {'+' if ph_diff >= 0 else ''}{ph_diff})")
            if est_ph < 5.8 or est_ph > 8.0:
                st.warning(f"⚠️ pH may go to {est_ph} after fertilization — add lime or sulphur to correct")
'''

# ============================================================
# SECTION E — .env file addition
# Add this line to your .env file:
# ============================================================
ENV_ADDITION = '''
# ✅ CLAUDE VISION AI — For Leaf Scan photo analysis
# Get free API key from: https://console.anthropic.com
# Free tier: enough for small farm use
ANTHROPIC_API_KEY=your_key_here
'''

# ============================================================
# STEP-BY-STEP INTEGRATION GUIDE
# ============================================================
INTEGRATION_STEPS = """
============================================================
STEP-BY-STEP GUIDE TO UPGRADE FARM AI v9 → v10
============================================================

STEP 1: Install new dependency
  Open terminal in farm_ai folder and run:
  > pip install anthropic

STEP 2: Get free API key
  Go to: https://console.anthropic.com
  Sign up (free) → Create API Key → Copy it

STEP 3: Add key to .env file
  Open: farm_ai/.env
  Add this line at the bottom:
  ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

STEP 4: Replace agent files
  Copy these 3 files into farm_ai/agents/ folder:
  ✅ agents/leaf_scan_agent.py  (COMPLETE REPLACEMENT)
  ✅ agents/pest_agent.py       (COMPLETE REPLACEMENT)
  ✅ agents/fertilizer_agent.py (COMPLETE REPLACEMENT)

STEP 5: Update streamlit_app.py — 3 changes needed
  
  5a. Find the run_agents() function (around line 230).
      Replace the ENTIRE function with SECTION_B_COMPLETE
      (copy from this file, lines marked "SECTION B")

  5b. Find "with tabs[8]:" section (around line 695).
      Replace the ENTIRE tabs[8] block with SECTION_C_LEAF_SCAN_TAB
      (copy from this file, lines marked "SECTION C")

  5c. Find the Fertilizer tab "with tabs[5]:" section.
      After the existing warnings display, add SECTION_D_FERT_ADDON
      (copy from this file, lines marked "SECTION D")

STEP 6: Run the app
  > cd farm_ai
  > py -m streamlit run dashboard/streamlit_app.py

STEP 7: Test Leaf Scan
  - Open the app → go to "📸 Leaf Scan" tab
  - Upload any leaf photo
  - It should show: Disease name, Pesticide, Dose, Cost, pH note
  
============================================================
WHAT'S NEW AFTER UPGRADE:
============================================================

📸 LEAF SCAN:
  - Now uses Claude Vision AI to analyze ANY photo
  - Identifies 20+ diseases AND nutrient deficiencies
  - Tells you exact pesticide AND fertilizer to use
  - Shows pH impact (e.g. "Your high pH is causing Iron deficiency")
  - Cost per acre estimate included

🐛 PEST AGENT:
  - Now reads Leaf Scan result directly
  - Shows confidence %, severity, spread risk
  - Weather-based risk (high humidity = fungal warning)
  - Stage-specific pest watch list (what to look for now)
  - Total spray cost for your farm size

🧬 FERTILIZER AGENT:
  - Now reads deficiency from Leaf Scan and adds correction
  - Shows nutrient availability % at your current pH
  - Estimates pH AFTER fertilization (e.g. "DAP will lower pH by 0.4")
  - Warns if nutrients will be locked even after applying fertilizer
  - Stage-specific application timing

============================================================
LIMITATIONS & FUTURE IMPROVEMENTS:
============================================================

1. LEAF SCAN - No offline mode
   Problem: Without ANTHROPIC_API_KEY, uses keyword matching only
   Fix: We've kept keyword fallback — works without internet

2. LEAF SCAN - Confidence varies with photo quality
   Problem: Blurry/dark photos give uncertain results
   Fix: Added clear tips + text description option as supplement

3. FERTILIZER - pH changes are estimates, not real measurements
   Problem: We estimate pH drift after fertilization, but real drift 
            depends on soil type, irrigation, rain
   Fix: Added warning to re-test pH after 30 days

4. PEST AGENT - Cannot detect pests from photo yet (only diseases)
   Problem: Aphids, thrips, mites are not visible in current analysis
   Fix: Added stage-based watch list for stage-specific pests

5. PH TRACKING - We estimate pH drift but don't know actual current pH
   Problem: Farmer enters pH from soil test done months ago
   Fix: Added "estimated pH after fertilization" + reminder to retest

6. NO CAMERA INTEGRATION
   Problem: Farmer must save photo first, then upload
   Fix: Added st.camera_input (Streamlit supports this — add if needed)

7. LANGUAGE BARRIER
   Problem: All text in English — most farmers in AP/Telangana speak Telugu
   Fix: Add Google Translate API OR use bilingual labels

8. MANDI PRICES - Only some crops listed
   Problem: data.gov.in API doesn't have all crops
   Fix: Add fallback to AGMARKNET price scraping

9. NO HISTORY TRACKING
   Problem: Farmer can't see what disease was detected last week
   Fix: Add SQLite database to store scan history

10. YIELD PREDICTOR
    Problem: ML model uses generic data, not farm-specific history
    Fix: Add "remember my yields from previous seasons" feature

============================================================
"""

if __name__ == "__main__":
    print(INTEGRATION_STEPS)
