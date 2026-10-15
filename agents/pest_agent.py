"""
Farm AI - Pest Agent v2.0 (UPGRADED)
======================================
Now FULLY INTEGRATED with Leaf Scan Agent.
- Uses actual leaf scan result for disease + pesticide
- Adds weather-based risk factors
- Estimates spray cost for the whole farm
- Gives stage-specific pest risk (seedling vs flowering vs harvest)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from data.crop_data import PESTS, CROPS
except Exception:
    PESTS = {}
    CROPS = {}

# Weather-based pest risk factors
WEATHER_RISK = {
    # (humidity > 80 and temp 25-35) = high fungal risk
    # (high wind) = spread risk
    # (rain > 10mm) = blast / blight risk
}

# Stage-specific pest watch list
STAGE_PEST_WATCH = {
    "Seedling": ["Damping off", "Leaf folder", "Shoot borer"],
    "Vegetative": ["Blast", "Brown Spot", "Leaf folder", "Stem borer", "Fall Armyworm"],
    "Flowering": ["Rice Gall Midge", "Bacterial Leaf Blight", "Neck Blast", "Sheath Blight"],
    "Maturity": ["False Smut", "Brown Plant Hopper", "Grain discoloration"],
    "Grain Filling": ["Leaf hopper", "Brown Plant Hopper", "Sheath rot"],
}


class PestAgent:
    name = "Pest Agent"
    description = "Disease risk + pesticide advice | Integrated with Leaf Scan"

    def analyze(self, *args, **kwargs):
        """
        Supports both calling conventions:
        1. Legacy / main.py / tests: analyze(crop, temp_c, humidity_pct, rain_mm, stage, symptoms, acres)
        2. Modern: analyze(leaf_scan_result=..., weather=..., crop=..., growth_stage=..., acres=..., soil_ph=...)
        """
        leaf_scan_result = kwargs.get("leaf_scan_result")
        weather          = kwargs.get("weather")
        crop             = kwargs.get("crop", "Rice")
        growth_stage     = kwargs.get("growth_stage", kwargs.get("stage", "Vegetative"))
        acres            = float(kwargs.get("acres", 5.0))
        soil_ph          = float(kwargs.get("soil_ph", 6.5))
        temp_c           = kwargs.get("temp_c")
        humidity_pct     = kwargs.get("humidity_pct")
        rain_mm          = kwargs.get("rain_mm")
        symptoms         = kwargs.get("symptoms")

        # Check positional args
        if args:
            if isinstance(args[0], dict):
                leaf_scan_result = args[0]
                if len(args) > 1 and isinstance(args[1], dict):
                    weather = args[1]
                if len(args) > 2: crop = args[2]
                if len(args) > 3: growth_stage = args[3]
                if len(args) > 4: acres = float(args[4])
            else:
                # Positional style from main.py & tests: (crop, temp_c, humidity_pct, rain_mm, stage, symptoms, acres)
                crop = args[0]
                if len(args) > 1: temp_c = args[1]
                if len(args) > 2: humidity_pct = args[2]
                if len(args) > 3: rain_mm = args[3]
                if len(args) > 4: growth_stage = args[4]
                if len(args) > 5: symptoms = args[5]
                if len(args) > 6: acres = float(args[6])

        # Normalize weather
        if isinstance(weather, dict):
            temp_c = weather.get("temperature_c", temp_c or 28)
            humidity_pct = weather.get("humidity_pct", humidity_pct or 70)
            rain_mm = weather.get("rainfall_mm", rain_mm or 0)
        else:
            temp_c = float(temp_c) if temp_c is not None else 28.0
            humidity_pct = float(humidity_pct) if humidity_pct is not None else 70.0
            rain_mm = float(rain_mm) if rain_mm is not None else 0.0

        if not leaf_scan_result and symptoms:
            # If farmer provided symptoms, run LeafScan text matching
            symp_txt = symptoms[0] if isinstance(symptoms, list) and symptoms else str(symptoms)
            from agents.leaf_scan_agent import LeafScanAgent
            leaf_scan_result = LeafScanAgent().analyze_text(symp_txt, crop=crop, soil_ph=soil_ph)

        # ── 1. Weather-based background risk ──────────────────────────────
        weather_risk = "LOW"
        weather_notes = []

        if humidity_pct > 80 and 25 <= temp_c <= 35:
            weather_risk = "HIGH"
            weather_notes.append(f"High humidity ({humidity_pct}%) + warm temp ({temp_c}°C) = HIGH fungal disease risk")
        elif humidity_pct > 70:
            weather_risk = "MEDIUM"
            weather_notes.append(f"Humidity {humidity_pct}% — moderate disease risk")

        if rain_mm > 10:
            weather_notes.append(f"Recent rain ({rain_mm}mm) — spray AFTER rain stops, not before")
            if weather_risk == "LOW":
                weather_risk = "MEDIUM"

        if temp_c > 38:
            weather_notes.append(f"Very hot ({temp_c}°C) — stress makes crops more disease-prone. Ensure irrigation.")

        # ── 2. Leaf Scan Integration (main diagnosis) ─────────────────────
        if (leaf_scan_result and
                leaf_scan_result.get("detected_disease") not in
                ["Unknown / Healthy", "Unknown", "Healthy", "Healthy Crop",
                 "Unable to Identify — Take Clear Photo", None, ""]):

            disease = leaf_scan_result.get("detected_disease", "Unknown")
            pesticide = leaf_scan_result.get("pesticide", "Consult agri officer")
            dose = leaf_scan_result.get("pest_dose", leaf_scan_result.get("dose", "As per label"))
            confidence = leaf_scan_result.get("confidence_pct", 70)
            is_deficiency = leaf_scan_result.get("is_deficiency", False)
            severity = leaf_scan_result.get("severity", "moderate")
            spread_risk = leaf_scan_result.get("spread_risk", "moderate")
            spray_timing = leaf_scan_result.get("spray_timing", "Early morning")
            cost_per_acre = leaf_scan_result.get("cost_per_acre", 300)
            organic_alt = leaf_scan_result.get("organic_alternative", "Neem oil 5ml/litre")

            # Risk level from confidence + weather
            if confidence >= 75 or weather_risk == "HIGH":
                risk_level = "HIGH"
            elif confidence >= 50 or weather_risk == "MEDIUM":
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            total_spray_cost = round(cost_per_acre * acres)

            if is_deficiency:
                rec = (f"NUTRIENT DEFICIENCY detected: {disease}. "
                       f"Apply {leaf_scan_result.get('fertilizer', 'balanced fertilizer')} "
                       f"@ {leaf_scan_result.get('fert_dose', 'as per label')}. "
                       f"No pesticide needed.")
                action_today = f"Buy {leaf_scan_result.get('fertilizer', 'fertilizer')} from agri shop and apply today"
            else:
                rec = (f"DISEASE FOUND: {disease} ({confidence}% confidence). "
                       f"Spray {pesticide} @ {dose}. {spray_timing}.")
                action_today = leaf_scan_result.get("farmer_action",
                                                     f"Buy {pesticide} and spray {dose} today")

            # Stage-specific additional watch
            stage_key = self._map_stage(growth_stage)
            stage_risks = STAGE_PEST_WATCH.get(stage_key, [])
            other_risks = [p for p in stage_risks if p.lower() not in disease.lower()][:2]

            ret = {
                "agent": self.name,
                "risk_level": risk_level,
                "alert_level": risk_level,
                "top_threat": disease,
                "top_threat_risk": confidence,
                "detected_disease": disease,
                "pesticide": pesticide if not is_deficiency else "Not needed",
                "dose": dose if not is_deficiency else "-",
                "fertilizer_needed": leaf_scan_result.get("fertilizer", "") if is_deficiency else "",
                "fertilizer_dose": leaf_scan_result.get("fert_dose", "") if is_deficiency else "",
                "confidence": confidence,
                "confidence_pct": confidence,
                "severity": severity,
                "spread_risk": spread_risk,
                "spray_timing": spray_timing,
                "organic_alternative": organic_alt,
                "organic_alt": organic_alt,
                "cost_per_acre": cost_per_acre,
                "total_spray_cost": total_spray_cost,
                "crop_loss_prevented": round(cost_per_acre * acres * 4),
                "weather_risk": weather_risk,
                "weather_notes": weather_notes,
                "stage_watch": other_risks,
                "recommendation": rec,
                "action_today": action_today,
                "action": action_today,
                "immediate_action": action_today,
                "ph_note": leaf_scan_result.get("ph_note", ""),
                "source": leaf_scan_result.get("source", "Leaf Scan"),
                "message": f"⚠️ {disease} detected — take action today!",
                "pest_risks": [
                    {"pest": disease, "risk_pct": confidence, "description": f"Detected: {disease}", "pesticide": pesticide, "dose": dose, "spray_timing": spray_timing, "cost_per_acre": cost_per_acre, "organic_alt": organic_alt, "farmer_tip": action_today}
                ]
            }
            return ret

        # ── 3. No leaf scan disease — use weather + stage risk ────────────
        stage_key = self._map_stage(growth_stage)
        stage_risks = STAGE_PEST_WATCH.get(stage_key, ["General pests"])

        if weather_risk == "HIGH":
            primary_risk = stage_risks[0] if stage_risks else "Fungal disease"
            return {
                "agent": self.name,
                "risk_level": "MEDIUM",
                "alert_level": "MEDIUM",
                "top_threat": primary_risk,
                "top_threat_risk": 65,
                "detected_disease": f"No disease detected yet, but {primary_risk} risk is HIGH due to weather",
                "pesticide": "Preventive: Mancozeb 2g/litre or Copper oxychloride 3g/litre",
                "dose": "2-3g per litre water",
                "confidence": 60,
                "confidence_pct": 60,
                "severity": "mild",
                "spread_risk": "Could spread fast — preventive spray recommended",
                "spray_timing": "Spray preventively when humidity > 80%",
                "organic_alternative": "Neem oil 5ml/litre as preventive",
                "organic_alt": "Neem oil 5ml/litre",
                "cost_per_acre": 150,
                "total_spray_cost": round(150 * acres),
                "crop_loss_prevented": round(150 * acres * 4),
                "weather_risk": weather_risk,
                "weather_notes": weather_notes,
                "stage_watch": stage_risks[:3],
                "recommendation": f"Weather conditions favor {primary_risk}. Apply preventive spray.",
                "action_today": "Do preventive Mancozeb spray — better safe than losing crop",
                "immediate_action": "Do preventive Mancozeb spray — better safe than losing crop",
                "ph_note": "",
                "source": "Weather + Stage Analysis",
                "message": f"Weather risk HIGH — preventive action recommended for {primary_risk}",
                "pest_risks": [
                    {"pest": primary_risk, "risk_pct": 65, "description": "Fungal threat due to humidity", "pesticide": "Mancozeb 75 WP", "dose": "2g/litre", "spray_timing": "Morning", "cost_per_acre": 150, "organic_alt": "Neem oil 5ml/L", "farmer_tip": "Spray preventively"}
                ]
            }

        # All clear
        return {
            "agent": self.name,
            "risk_level": "LOW",
            "alert_level": "LOW",
            "top_threat": "None",
            "top_threat_risk": 15,
            "detected_disease": "No disease detected — crop looks healthy",
            "pesticide": "None needed right now",
            "dose": "-",
            "confidence": 85,
            "confidence_pct": 85,
            "severity": "none",
            "spread_risk": "Low",
            "spray_timing": "No spray needed",
            "organic_alternative": "Continue monitoring every 3 days",
            "organic_alt": "Neem oil if pests appear",
            "cost_per_acre": 0,
            "total_spray_cost": 0,
            "crop_loss_prevented": 0,
            "weather_risk": weather_risk,
            "weather_notes": weather_notes if weather_notes else ["Weather conditions are favorable"],
            "stage_watch": stage_risks[:2],
            "recommendation": "Crop looks healthy. Monitor regularly especially during " +
                              ", ".join(stage_risks[:2]),
            "action_today": "Monitor crop. Look for early signs of " + (stage_risks[0] if stage_risks else "disease"),
            "immediate_action": "Crop looks healthy — keep monitoring regularly!",
            "ph_note": "",
            "source": "Weather + Stage Analysis",
            "message": "✅ Crop looks healthy — keep monitoring!",
            "pest_risks": [
                {"pest": stage_risks[0] if stage_risks else "General Pests", "risk_pct": 15, "description": "Low seasonal incidence", "pesticide": "None needed", "dose": "-", "spray_timing": "-", "cost_per_acre": 0, "organic_alt": "Sticky traps", "farmer_tip": "Monitor every 3 days"}
            ]
        }

    def _map_stage(self, stage_str: str) -> str:
        """Map various stage descriptions to standard stage names."""
        s = stage_str.lower() if stage_str else ""
        if any(x in s for x in ["seed", "sprout", "germina", "nursery"]):
            return "Seedling"
        elif any(x in s for x in ["flower", "panicle", "heading", "boot"]):
            return "Flowering"
        elif any(x in s for x in ["grain", "fill", "dough", "ripen", "matur"]):
            return "Grain Filling"
        elif any(x in s for x in ["harvest", "ready"]):
            return "Maturity"
        else:
            return "Vegetative"


if __name__ == "__main__":
    # Test with a mock leaf scan result
    mock_leaf = {
        "detected_disease": "Blast",
        "pesticide": "Tricyclazole 75 WP",
        "pest_dose": "2g per litre",
        "confidence_pct": 85,
        "spray_timing": "Early morning, twice 7 days apart",
        "cost_per_acre": 350,
        "is_deficiency": False,
        "severity": "moderate",
        "spread_risk": "Spreads fast in humid weather",
        "organic_alternative": "Pseudomonas fluorescens",
        "farmer_action": "Buy Tricyclazole and spray today morning"
    }
    agent = PestAgent()
    r = agent.analyze(leaf_scan_result=mock_leaf, crop="Rice",
                      growth_stage="Vegetative", acres=5)
    print(f"Risk: {r['risk_level']}")
    print(f"Recommendation: {r['recommendation']}")
    print(f"Total cost: Rs {r['total_spray_cost']}")
