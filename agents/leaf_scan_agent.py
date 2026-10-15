"""
Farm AI - Leaf Scan Agent v2.1 (GEMINI VERSION — 100% FREE)
=============================================================
Uses Google Gemini Vision API — FREE 1500 requests/day
Get your free key at: https://aistudio.google.com/app/apikey
(Sign in with Google → Create API Key → Copy → paste in .env)

Add to your .env file:
GEMINI_API_KEY=your_key_here

No credit card. No payment. Completely free.
"""

import os, sys, base64, json, tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    from data.crop_data import PESTS, CROPS
except Exception:
    PESTS = {}; CROPS = {}

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ══════════════════════════════════════════════════════════
# DISEASE DATABASE — used as fallback when no internet
# ══════════════════════════════════════════════════════════
DISEASE_DB = {
    "Blast": {
        "pesticide": "Tricyclazole 75 WP", "pest_dose": "2g per litre water",
        "fertilizer": "Reduce Nitrogen, Apply MOP 25 kg/acre", "fert_dose": "MOP 25 kg/acre",
        "spray_timing": "Early morning. Spray twice, 7 days apart.",
        "cost_per_acre": 350, "organic_alt": "Pseudomonas fluorescens 2.5 kg/ha",
        "description": "Water-soaked white/grey diamond-shaped lesions with brown margins on rice leaves.",
        "is_deficiency": False
    },
    "Brown Spot": {
        "pesticide": "Mancozeb 75 WP or Propiconazole 25 EC", "pest_dose": "2g per litre",
        "fertilizer": "Apply Potassium (MOP)", "fert_dose": "MOP 20 kg/acre",
        "spray_timing": "Spray at first sign. Repeat after 10 days.",
        "cost_per_acre": 280, "organic_alt": "Cow urine spray 10%",
        "description": "Small oval brown spots with yellow halo. Worse when Potassium is low.",
        "is_deficiency": False
    },
    "Powdery Mildew": {
        "pesticide": "Sulphur 80 WP or Carbendazim 50 WP", "pest_dose": "2g per litre",
        "fertilizer": "Reduce Nitrogen. Add Calcium.", "fert_dose": "Calcium nitrate 5g/litre foliar",
        "spray_timing": "Spray on dry sunny day. Avoid when rain expected.",
        "cost_per_acre": 200, "organic_alt": "Baking soda 5g + soap 3ml per litre",
        "description": "White powdery coating on leaf surface. Worsens in humid weather.",
        "is_deficiency": False
    },
    "Rust": {
        "pesticide": "Propiconazole 25 EC", "pest_dose": "1ml per litre",
        "fertilizer": "Balanced NPK. Add Zinc 25 kg/ha.", "fert_dose": "ZnSO4 25 kg/ha",
        "spray_timing": "Spray immediately at first symptoms. Repeat in 7-10 days.",
        "cost_per_acre": 320, "organic_alt": "Garlic extract 50g/litre spray",
        "description": "Orange-yellow pustules on leaf surface. Spreads fast in cool humid weather.",
        "is_deficiency": False
    },
    "Late Blight": {
        "pesticide": "Mancozeb + Cymoxanil or Metalaxyl MZ", "pest_dose": "2.5g per litre",
        "fertilizer": "Reduce irrigation. Apply MOP 30 kg/acre.", "fert_dose": "MOP 30 kg/acre",
        "spray_timing": "URGENT: Spray every 5-7 days in rainy weather.",
        "cost_per_acre": 500, "organic_alt": "Copper oxychloride 3g/litre",
        "description": "Dark water-soaked lesions spreading fast. White mold under leaf.",
        "is_deficiency": False
    },
    "Early Blight": {
        "pesticide": "Mancozeb 75 WP or Chlorothalonil", "pest_dose": "2g per litre",
        "fertilizer": "Add Calcium and Phosphorus.", "fert_dose": "SSP 50 kg/acre + Calcium 3g/litre",
        "spray_timing": "Preventive spray in wet season.",
        "cost_per_acre": 250, "organic_alt": "Copper oxychloride 3g/litre",
        "description": "Target-shaped spots (concentric rings) on older leaves.",
        "is_deficiency": False
    },
    "Yellow Mosaic": {
        "pesticide": "Imidacloprid 70 WG (kills whitefly vector)", "pest_dose": "0.3g per litre",
        "fertilizer": "Balanced NPK foliar spray", "fert_dose": "19:19:19 @ 5g/litre",
        "spray_timing": "Spray early morning. Remove infected plants first.",
        "cost_per_acre": 450, "organic_alt": "Yellow sticky traps + Neem oil 5ml/litre",
        "description": "Mosaic yellow pattern on young leaves. Caused by virus spread by whitefly.",
        "is_deficiency": False
    },
    "Fall Armyworm": {
        "pesticide": "Emamectin Benzoate 5 SG", "pest_dose": "0.4g per litre",
        "fertilizer": "Balanced NPK — avoid excess Nitrogen", "fert_dose": "As per soil test",
        "spray_timing": "Spray in evening. Check stem/whorl for larvae.",
        "cost_per_acre": 600, "organic_alt": "Bt (Bacillus thuringiensis) 2ml/litre",
        "description": "Caterpillar eating holes with sawdust frass. Window-pane damage on leaves.",
        "is_deficiency": False
    },
    "Bacterial Leaf Blight": {
        "pesticide": "Streptocycline 1g + Copper oxychloride 3g per litre", "pest_dose": "As above",
        "fertilizer": "Reduce Nitrogen applications till recovery.", "fert_dose": "No new Nitrogen",
        "spray_timing": "Spray in morning. Keep field drained.",
        "cost_per_acre": 380, "organic_alt": "Pseudomonas fluorescens foliar spray",
        "description": "Yellow lesions from leaf tips/margins. Caused by Xanthomonas bacteria.",
        "is_deficiency": False
    },
    # ── Nutrient Deficiencies ──────────────────────────────
    "Nitrogen Deficiency": {
        "pesticide": "None needed", "pest_dose": "No pesticide",
        "fertilizer": "Urea foliar spray + soil application", "fert_dose": "Urea 2% foliar (20g/litre) + 30-40 kg/acre soil",
        "spray_timing": "Foliar early morning. Soil before irrigation.",
        "cost_per_acre": 300, "organic_alt": "Farmyard Manure 4 ton/acre",
        "description": "Yellowing from older/lower leaves upward. Stunted pale green plants.",
        "is_deficiency": True
    },
    "Phosphorus Deficiency": {
        "pesticide": "None needed", "pest_dose": "No pesticide",
        "fertilizer": "DAP or SSP", "fert_dose": "DAP 50 kg/acre OR SSP 125 kg/acre",
        "spray_timing": "Mix in irrigation water or broadcast before watering.",
        "cost_per_acre": 1200, "organic_alt": "Bone meal 250 kg/acre",
        "description": "Purple-red color on leaf undersides and stems. Stunted plants.",
        "is_deficiency": True
    },
    "Potassium Deficiency": {
        "pesticide": "None needed", "pest_dose": "No pesticide",
        "fertilizer": "MOP (Muriate of Potash)", "fert_dose": "MOP 30-40 kg/acre",
        "spray_timing": "Broadcast and water in immediately.",
        "cost_per_acre": 800, "organic_alt": "Wood ash 500 kg/acre",
        "description": "Yellowing/browning of leaf edges and tips. Weak stems.",
        "is_deficiency": True
    },
    "Iron Deficiency": {
        "pesticide": "None needed", "pest_dose": "No pesticide",
        "fertilizer": "Ferrous Sulphate foliar spray", "fert_dose": "FeSO4 0.5% (5g/litre) twice",
        "spray_timing": "Early morning spray. Mix with lime water.",
        "cost_per_acre": 150, "organic_alt": "Vermicompost 500 kg/acre",
        "description": "Yellowing between veins (interveinal chlorosis) on NEW young leaves. Veins stay green.",
        "is_deficiency": True
    },
    "Magnesium Deficiency": {
        "pesticide": "None needed", "pest_dose": "No pesticide",
        "fertilizer": "Magnesium Sulphate (Epsom Salt)", "fert_dose": "MgSO4 2% (20g/litre) twice",
        "spray_timing": "2 sprays, 10 days apart.",
        "cost_per_acre": 120, "organic_alt": "Dolomite lime 200 kg/acre",
        "description": "Yellowing between veins on OLD lower leaves first. V-shaped yellow pattern.",
        "is_deficiency": True
    },
    "Zinc Deficiency": {
        "pesticide": "None needed", "pest_dose": "No pesticide",
        "fertilizer": "Zinc Sulphate", "fert_dose": "ZnSO4 25 kg/ha soil + 0.5% foliar",
        "spray_timing": "2-3 foliar sprays from seedling stage.",
        "cost_per_acre": 200, "organic_alt": "FYM 4 ton/acre",
        "description": "Pale white stripes on young leaves. Stunted plants. Khaira in rice.",
        "is_deficiency": True
    },
}

KEYWORD_MAP = {
    "Blast":                 ["blast", "diamond spot", "gray center", "rice blast", "grey lesion"],
    "Brown Spot":            ["brown spot", "oval brown", "small brown", "brown oval"],
    "Powdery Mildew":        ["white powder", "white coat", "flour", "mildew", "powdery"],
    "Rust":                  ["rust", "orange powder", "orange spot", "yellow stripe rust"],
    "Late Blight":           ["late blight", "water soak", "dark spread", "white mold"],
    "Early Blight":          ["early blight", "concentric ring", "target spot", "circular brown"],
    "Yellow Mosaic":         ["yellow mosaic", "mottl", "golden", "yellow patch mosaic"],
    "Fall Armyworm":         ["army worm", "caterpillar", "window pane", "hole", "frass", "larvae"],
    "Bacterial Leaf Blight": ["bacterial", "water soak tip", "yellow margin", "tip die"],
    "Nitrogen Deficiency":   ["pale yellow", "overall yellow", "light green", "stunted pale", "uniform yellow"],
    "Potassium Deficiency":  ["edge yellow", "margin burn", "tip burn", "scorch edge", "brown edge"],
    "Iron Deficiency":       ["between vein yellow new", "interveinal young", "vein green rest yellow new"],
    "Magnesium Deficiency":  ["between vein old", "lower leaf yellow", "v shape yellow", "old leaf vein"],
    "Phosphorus Deficiency": ["purple", "red stem", "violet", "dark green purple"],
    "Zinc Deficiency":       ["white stripe", "pale stripe", "stunted small", "khaira"],
}


def _ph_note(soil_ph: float, disease: str = None) -> str:
    if soil_ph > 7.8:
        base = f"⚠️ Your pH {soil_ph} is HIGH — Iron and Zinc are LOCKED in soil. Apply Sulphur 5 kg/acre."
        if disease and "Iron" in str(disease):
            return base + " This HIGH pH is CAUSING your Iron deficiency."
        if disease and "Zinc" in str(disease):
            return base + " Fix pH to make Zinc available."
        return base
    elif soil_ph > 7.5:
        return f"Your pH {soil_ph} is slightly alkaline. Zinc and Iron may be partially unavailable."
    elif soil_ph < 5.5:
        return f"⚠️ pH {soil_ph} is LOW — Phosphorus and Calcium are unavailable. Apply lime 200 kg/acre."
    elif soil_ph < 6.0:
        return f"pH {soil_ph} slightly acidic. Apply lime 100 kg/acre for best nutrient availability."
    return f"✅ pH {soil_ph} is ideal — all nutrients are available."


def _normalize(r: dict) -> dict:
    defaults = {
        "detected_disease": "Unknown", "disease_description": "",
        "confidence_pct": 50, "confidence_label": "MEDIUM", "is_deficiency": False,
        "pesticide": "Consult agri officer", "pest_dose": "As per label",
        "fertilizer": "Balanced NPK", "fert_dose": "As per soil test",
        "spray_timing": "Early morning", "cost_per_acre": 0,
        "organic_alternative": "Neem oil 5ml/litre", "ph_note": "",
        "farmer_action": "Monitor crop closely", "action": "Monitor crop closely", "severity": "unknown",
        "spread_risk": "unknown", "source": "Analysis"
    }
    for k, v in defaults.items():
        if k not in r:
            r[k] = v
    if "action" not in r or not r["action"]:
        r["action"] = r.get("farmer_action", "Monitor crop closely")
    c = int(r.get("confidence_pct", 50))
    r["confidence_label"] = "HIGH" if c >= 80 else ("MEDIUM" if c >= 50 else "LOW")
    return r


def _encode_image(image_path: str):
    """Returns (base64_string, mime_type) after resizing if needed."""
    if not os.path.exists(image_path):
        return None, None
    ext = Path(image_path).suffix.lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
    if PIL_AVAILABLE:
        try:
            img = Image.open(image_path)
            if max(img.size) > 1024:
                r = 1024 / max(img.size)
                img = img.resize((int(img.width*r), int(img.height*r)), Image.LANCZOS)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            img.convert("RGB").save(tmp.name, "JPEG", quality=85)
            image_path = tmp.name
            mime = "image/jpeg"
        except Exception:
            pass
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8"), mime


def _call_gemini_vision(image_path: str, crop: str, soil_ph: float,
                        symptom_description: str = "") -> dict:
    """Call Google Gemini Vision API (FREE - 1500 requests/day)."""
    import urllib.request, urllib.error

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return {"error": "GEMINI_API_KEY not set. Get free key at https://aistudio.google.com/app/apikey"}

    b64, mime = _encode_image(image_path)
    if not b64:
        return {"error": "Could not read image file"}

    extra = f"Farmer says: {symptom_description}" if symptom_description else ""

    prompt = f"""You are an expert agricultural scientist with 30 years experience in Indian farming.
Analyze this leaf photo carefully.

Crop: {crop}
Soil pH: {soil_ph}
{extra}

Reply ONLY with a valid JSON object (no markdown, no extra text):
{{
  "detected_disease": "exact disease or deficiency name",
  "disease_description": "2-sentence description of what it is",
  "confidence_pct": 85,
  "is_deficiency": false,
  "pesticide": "exact product name available at Indian agri shops",
  "pest_dose": "e.g. 2ml per litre water",
  "fertilizer": "fertilizer to apply if deficiency found, else None",
  "fert_dose": "dose for fertilizer",
  "spray_timing": "when exactly to spray",
  "cost_per_acre": 350,
  "organic_alternative": "natural/organic option",
  "ph_note": "how soil pH {soil_ph} affects this specific problem",
  "farmer_action": "single most important step to do TODAY",
  "severity": "mild or moderate or severe",
  "spread_risk": "how fast it spreads"
}}

If healthy, set detected_disease to "Healthy Crop" and confidence_pct to 90.
If it is a NUTRIENT deficiency (yellowing, color change without fungal spots), set is_deficiency to true.
Always give Indian product names. Always consider pH {soil_ph} impact."""

    payload = json.dumps({
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": mime, "data": b64}},
                {"text": prompt}
            ]
        }]
    }).encode("utf-8")

    models_to_try = ["gemini-flash-lite-latest", "gemini-2.5-flash", "gemini-flash-latest", "gemini-1.5-flash"]
    last_err = ""
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(raw)
            result["source"] = f"Gemini Vision AI ({model_name})"
            return result
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            last_err = f"Gemini API error {e.code}: {body[:200]}"
            if e.code == 404:
                continue
            return {"error": last_err}
        except json.JSONDecodeError:
            return {"error": f"Could not parse Gemini response: {raw[:300]}"}
        except Exception as e:
            last_err = str(e)
            continue
    return {"error": f"Gemini request failed: {last_err}"}


def _call_gemini_text(description: str, crop: str, soil_ph: float) -> dict:
    """Call Gemini text API for description-only analysis (no image)."""
    import urllib.request, urllib.error

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return {}  # Fall through to keyword matching

    prompt = f"""Expert Indian farm scientist. Farmer describes their crop problem:

Crop: {crop}
Soil pH: {soil_ph}
Description: "{description}"

Reply ONLY with valid JSON:
{{
  "detected_disease": "disease or deficiency name",
  "disease_description": "brief 2-sentence description",
  "confidence_pct": 70,
  "is_deficiency": false,
  "pesticide": "product name",
  "pest_dose": "dose",
  "fertilizer": "fertilizer if deficiency else None",
  "fert_dose": "dose",
  "spray_timing": "when to apply",
  "cost_per_acre": 300,
  "organic_alternative": "natural option",
  "ph_note": "pH {soil_ph} impact",
  "farmer_action": "immediate step",
  "severity": "mild/moderate/severe",
  "spread_risk": "spread description"
}}"""

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")
    models_to_try = ["gemini-flash-lite-latest", "gemini-2.5-flash", "gemini-flash-latest", "gemini-1.5-flash"]
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(raw)
            result["source"] = f"Gemini Text AI ({model_name})"
            return result
        except Exception:
            continue
    return {}


def _keyword_fallback(description: str, crop: str, soil_ph: float) -> dict:
    """Pure keyword matching. Works 100% offline."""
    desc = description.lower() if description else ""
    best, best_score = None, 0
    for disease, keywords in KEYWORD_MAP.items():
        score = sum(1 for kw in keywords if kw in desc)
        if score > best_score:
            best_score = score
            best = disease

    if best and best_score > 0:
        db = DISEASE_DB.get(best, {})
        return {
            "detected_disease": best,
            "disease_description": db.get("description", ""),
            "confidence_pct": min(80, 50 + best_score * 10),
            "is_deficiency": db.get("is_deficiency", False),
            "pesticide": db.get("pesticide", "Consult agri officer"),
            "pest_dose": db.get("pest_dose", "As per label"),
            "fertilizer": db.get("fertilizer", "Balanced NPK"),
            "fert_dose": db.get("fert_dose", "As per soil test"),
            "spray_timing": db.get("spray_timing", "Early morning"),
            "cost_per_acre": db.get("cost_per_acre", 300),
            "organic_alternative": db.get("organic_alt", "Neem oil 5ml/litre"),
            "ph_note": _ph_note(soil_ph, best),
            "farmer_action": f"Buy {db.get('pesticide', 'recommended product')} from agri shop and apply today",
            "severity": "moderate",
            "spread_risk": "Moderate - act within 48 hours",
            "source": "Keyword Matching (offline)"
        }
    return {
        "detected_disease": "Cannot Identify — Upload a Clear Photo",
        "disease_description": "No match found. Please upload a clear leaf photo for accurate AI diagnosis.",
        "confidence_pct": 20, "is_deficiency": False,
        "pesticide": "Cannot recommend without diagnosis",
        "pest_dose": "Consult local Krishi officer",
        "fertilizer": "Balanced NPK as maintenance",
        "fert_dose": "Urea 30kg + DAP 25kg + MOP 15kg per acre",
        "spray_timing": "After proper identification",
        "cost_per_acre": 0,
        "organic_alternative": "Neem oil 5ml/litre as general protection",
        "ph_note": _ph_note(soil_ph),
        "farmer_action": "Visit nearest Krishi Vigyan Kendra with leaf sample for FREE diagnosis",
        "severity": "unknown", "spread_risk": "unknown",
        "source": "No Match"
    }


# ══════════════════════════════════════════════════════════
# MAIN AGENT CLASS
# ══════════════════════════════════════════════════════════
class LeafScanAgent:
    name = "Leaf Scan Agent"
    description = "📸 Upload ANY leaf photo → Gemini AI identifies disease/deficiency → Exact pesticide + fertilizer + dose (FREE API)"

    def analyze_image(self, image_path: str = None, symptom_description: str = "",
                      crop: str = "Rice", soil_ph: float = 6.5) -> dict:
        """
        Analyze a leaf photo using Gemini Vision (FREE).
        Falls back to keyword matching if no API key.
        """
        if image_path and os.path.exists(image_path):
            result = _call_gemini_vision(image_path, crop, soil_ph, symptom_description)
            if "error" not in result:
                if not result.get("ph_note"):
                    result["ph_note"] = _ph_note(soil_ph, result.get("detected_disease"))
                return _normalize(result)
            else:
                print(f"[LeafScan] Gemini error: {result['error']}")

        # No image or API failed → text analysis
        return self.analyze_text(symptom_description, crop, soil_ph)

    def analyze_text(self, description: str, crop: str = "Rice",
                     soil_ph: float = 6.5) -> dict:
        """Analyze using text description. Tries Gemini first, then keyword matching."""
        if description and len(description.strip()) > 5:
            result = _call_gemini_text(description, crop, soil_ph)
            if result and "error" not in result:
                if not result.get("ph_note"):
                    result["ph_note"] = _ph_note(soil_ph, result.get("detected_disease"))
                return _normalize(result)

        # Pure keyword fallback (no API needed)
        result = _keyword_fallback(description, crop, soil_ph)
        return _normalize(result)


# ══════════════════════════════════════════════════════════
# QUICK TEST
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    agent = LeafScanAgent()
    print("=== Testing Leaf Scan Agent ===")

    # Test 1: text description
    r = agent.analyze_text("yellow spots on rice leaves, brown at edges", "Rice", soil_ph=7.9)
    print(f"\nTest 1 (Text):")
    print(f"  Disease:    {r['detected_disease']}")
    print(f"  Confidence: {r['confidence_pct']}% ({r['confidence_label']})")
    print(f"  Pesticide:  {r['pesticide']} @ {r['pest_dose']}")
    print(f"  Fertilizer: {r['fertilizer']} @ {r['fert_dose']}")
    print(f"  pH Note:    {r['ph_note']}")
    print(f"  Action:     {r['farmer_action']}")
    print(f"  Source:     {r['source']}")
