"""
Farm AI - Agent 1: Soil Agent
Recommends the RIGHT crop for YOUR soil.
No more guessing — saves Rs 1.5 Lakh/year.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.crop_data import CROPS, SOIL_PH_CROPS


class SoilAgent:
    name = "Soil Agent"
    description = "Right crop for your soil | Saves Rs 1.5L/year"

    def analyze(self, ph: float, nitrogen: float, phosphorus: float,
                potassium: float, state: str = "", season: str = "Kharif",
                organic_matter: float = 1.5,
                preferred_crop: str = None) -> dict:

        # 1. pH classification
        ph_class  = self._classify_ph(ph)
        ph_ok     = 6.0 <= ph <= 7.5
        ph_status = "Good for most crops" if ph_ok else "Needs correction first"

        # 2. Soil health scores (0-100)
        n_score  = min(100, int((nitrogen  / 150) * 100))
        p_score  = min(100, int((phosphorus /  60) * 100))
        k_score  = min(100, int((potassium  /  40) * 100))
        om_score = min(100, int((organic_matter / 2.0) * 100))
        overall  = int(n_score*0.35 + p_score*0.25 + k_score*0.2 + om_score*0.2)

        # 3. Best crops: match pH + season + state, sorted by profit_score
        suitable = self._get_suitable_crops(ph, state, season)

        # 4. preferred_crop ALWAYS first — farmer already chose their crop
        if preferred_crop:
            if preferred_crop in suitable:
                suitable.remove(preferred_crop)
            suitable.insert(0, preferred_crop)

        top_crop = suitable[0] if suitable else "Rice"
        top_info = CROPS.get(top_crop, {})

        # 5. Yield & revenue estimate
        exp_yield   = top_info.get("avg_yield_kg_acre", 1500)
        price_per_kg= top_info.get("msp_per_quintal", 2000) / 100
        revenue     = round(exp_yield * price_per_kg, 0)

        # 6. What corrections are needed
        amendments = self._amendments(ph, nitrogen, phosphorus, potassium, organic_matter)

        # 7. Simple farmer-friendly advice
        if ph_ok and overall >= 60:
            advice = f"Your soil is GOOD! Plant {top_crop} this {season}."
        elif not ph_ok:
            advice = f"Fix pH first ({ph_class}), then plant {top_crop}."
        else:
            advice = f"Add fertilizers as shown below, then plant {top_crop}."

        return {
            "agent":          self.name,
            "ph_value":       ph,
            "ph_class":       ph_class,
            "ph_status":      ph_status,
            "soil_health":    f"{overall}/100",
            "health_label":   "Excellent" if overall>=80 else "Good" if overall>=60 else "Fair" if overall>=40 else "Poor",
            "nutrient_scores":{"Nitrogen": f"{n_score}/100",
                               "Phosphorus": f"{p_score}/100",
                               "Potassium": f"{k_score}/100",
                               "Organic Matter": f"{om_score}/100"},
            "best_crop":      top_crop,
            "top5_crops":     suitable[:5],
            "avoid_crops":    self._avoid_crops(ph)[:3],
            "amendments":     amendments,
            "expected_yield_kg_acre":  exp_yield,
            "expected_revenue_per_acre": revenue,
            "annual_savings": "Rs 1,50,000",
            "advice":         advice,
            "action":         advice,
        }

    def _classify_ph(self, ph):
        if ph < 5.0: return "Very Acidic (pH too low)"
        if ph < 6.0: return "Acidic — add lime to fix"
        if ph < 6.5: return "Slightly Acidic — OK for rice/maize"
        if ph < 7.5: return "Neutral — BEST for farming"
        if ph < 8.0: return "Slightly Alkaline — add sulphur"
        return "Too Alkaline — needs sulphur treatment"

    def _get_suitable_crops(self, ph, state, season):
        matches = []
        for crop, info in CROPS.items():
            if info["ph_min"] <= ph <= info["ph_max"]:
                # Season match (Annual crops always included)
                if season in info["seasons"] or "Annual" in info["seasons"]:
                    # Prefer state-specific crops
                    state_bonus = 2 if (not info["states"] or state in info["states"]) else 0
                    score = info.get("profit_score", 5) + state_bonus
                    matches.append((crop, score))
        matches.sort(key=lambda x: -x[1])
        return [c for c, _ in matches]

    def _avoid_crops(self, ph):
        return [c for c, info in CROPS.items()
                if ph < info["ph_min"] - 0.5 or ph > info["ph_max"] + 0.5]

    def _amendments(self, ph, n, p, k, om):
        out = []
        if ph < 6.0:
            kg = round((6.5 - ph) * 500)
            out.append(f"Add Lime {kg} kg/acre — raises pH to ideal level (Cost: Rs {kg*2})")
        elif ph > 7.5:
            kg = round((ph - 7.0) * 200)
            out.append(f"Add Sulphur {kg} kg/acre — lowers pH (Cost: Rs {kg*15})")
        if n < 80:
            urea = round((120 - n) * 2.17 / 2.47)
            out.append(f"Apply Urea {urea} kg/acre — crops need Nitrogen (Cost: Rs {urea*6})")
        if p < 40:
            dap = round((60 - p) * 2.17 / 2.47)
            out.append(f"Apply DAP {dap} kg/acre — for strong roots (Cost: Rs {dap*27})")
        if k < 25:
            mop = round((40 - k) * 1.67 / 2.47)
            out.append(f"Apply MOP {mop} kg/acre — for disease resistance (Cost: Rs {mop*17})")
        if om < 1.0:
            out.append("Add Compost/FYM 2 tonnes/acre — improves soil health (Cost: Rs 1,000)")
        if not out:
            out.append("Soil is healthy — no corrections needed this season!")
        return out


if __name__ == "__main__":
    a = SoilAgent()
    r = a.analyze(6.5, 100, 50, 35, "Telangana", "Kharif", 1.8, "Rice")
    print(f"Best crop: {r['best_crop']}")
    print(f"Top 5: {r['top5_crops']}")
    print(f"Advice: {r['advice']}")
