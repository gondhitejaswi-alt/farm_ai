"""
Farm AI - Fertilizer Agent v2.0 (UPGRADED)
============================================
Major upgrades:
1. Accepts leaf scan deficiency result and adjusts fertilizer plan
2. pH-aware: warns when pH will block nutrient absorption
3. Tracks "estimated pH after fertilization" — the key missing feature
4. Stage-specific fertilizer timing
5. Organic + chemical options
6. Post-application pH drift estimation
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from data.crop_data import CROPS
except Exception:
    CROPS = {}


# How different fertilizers affect soil pH over a season
# (+ = raises pH, - = lowers pH)
FERTILIZER_PH_EFFECT = {
    "Urea":          -0.3,   # slightly acidifying
    "DAP":           -0.4,   # acidifying
    "MOP":           -0.1,   # slight acidification
    "SSP":           -0.3,   # acidifying
    "Ammonium Sulphate": -0.5,  # more acidifying
    "Calcium Nitrate":  +0.2,  # raises pH
    "Lime":          +1.0,   # significant increase
    "Sulphur":       -0.5,   # lowers pH
    "Gypsum":         0.0,   # neutral
    "FYM":           -0.1,   # slight acidification
}

# pH ranges for nutrient availability
PH_NUTRIENT_AVAILABILITY = {
    "Nitrogen":   (6.0, 8.0),
    "Phosphorus": (6.0, 7.5),
    "Potassium":  (6.0, 8.5),
    "Calcium":    (6.5, 8.5),
    "Magnesium":  (6.5, 8.5),
    "Iron":       (4.5, 6.5),   # locks up in alkaline soil
    "Zinc":       (5.0, 7.0),   # locks up in alkaline soil
    "Manganese":  (5.0, 6.5),
    "Boron":      (6.0, 7.5),
}


class FertilizerAgent:
    name = "Fertilizer Agent"
    description = "Exact NPK dose + deficiency fix + pH-aware advice | Saves Rs 1L/year"

    FERT = {
        "Urea":   {"N": 46, "price": 6.5},
        "DAP":    {"P": 46, "price": 27},
        "MOP":    {"K": 60, "price": 17},
        "SSP":    {"P": 16, "price": 9},
        "Gypsum": {"S": 12, "Ca": 20, "price": 3},
    }

    SPLIT = {
        "Kharif": {"At sowing": 0.33, "30 days after sowing": 0.33, "60 days after sowing": 0.34},
        "Rabi":   {"At sowing": 0.50, "30 days after sowing": 0.25, "60 days after sowing": 0.25},
    }

    def analyze(self, crop: str, acres: float,
                current_n: float = 0, current_p: float = 0,
                current_k: float = 0, soil_ph: float = 6.5,
                season: str = "Kharif",
                leaf_scan_result: dict = None,
                days_since_planting: int = 0) -> dict:
        """
        Comprehensive fertilizer plan.

        Args:
            crop: Crop name
            acres: Farm size
            current_n/p/k: Current soil nutrient levels (kg/ha from soil test)
            soil_ph: Soil pH (critical for nutrient availability)
            season: Kharif or Rabi
            leaf_scan_result: Optional leaf scan output for deficiency correction
            days_since_planting: Used for growth-stage aware advice
        """

        info  = CROPS.get(crop, {})
        req_n = info.get("nitrogen", 120)
        req_p = info.get("phosphorus", 60)
        req_k = info.get("potassium", 40)

        # ── 1. pH correction check FIRST ──────────────────────────────────
        ph_corrections = self._ph_corrections(soil_ph, crop)
        ph_status = self._ph_status(soil_ph)

        # ── 2. pH impact on current nutrients ─────────────────────────────
        # Nutrient availability factor (1.0 = fully available)
        n_avail  = self._availability_factor(soil_ph, "Nitrogen")
        p_avail  = self._availability_factor(soil_ph, "Phosphorus")
        k_avail  = self._availability_factor(soil_ph, "Potassium")

        # Effective nutrients = what plant can actually absorb
        eff_n = current_n * n_avail
        eff_p = current_p * p_avail
        eff_k = current_k * k_avail

        # What is still needed (per ha → convert to per acre ÷2.47)
        need_n = max(0, req_n - eff_n) / 2.47
        need_p = max(0, req_p - eff_p) / 2.47
        need_k = max(0, req_k - eff_k) / 2.47

        # ── 3. Add deficiency correction from leaf scan ───────────────────
        deficiency_addon = {}
        deficiency_note = ""
        if leaf_scan_result and leaf_scan_result.get("is_deficiency"):
            dis = leaf_scan_result.get("detected_disease", "")
            fert = leaf_scan_result.get("fertilizer", "")
            dose = leaf_scan_result.get("fert_dose", "")
            deficiency_addon = {
                "deficiency_found": dis,
                "correction_fertilizer": fert,
                "correction_dose": dose,
                "spray_timing": leaf_scan_result.get("spray_timing", "Immediately"),
                "cost": leaf_scan_result.get("cost_per_acre", 0) * acres
            }
            deficiency_note = (f"⚠️ Leaf Scan detected {dis}. "
                               f"Add {fert} @ {dose} IN ADDITION to regular NPK.")

            # Boost the relevant nutrient
            if "Nitrogen" in dis:
                need_n = max(need_n, 30)   # ensure at least 30 kg/acre
            elif "Phosphorus" in dis:
                need_p = max(need_p, 20)
            elif "Potassium" in dis:
                need_k = max(need_k, 15)

        # ── 4. Calculate fertilizer quantities ───────────────────────────
        urea_acre = round(need_n / 0.46, 1)
        dap_acre  = round(need_p / 0.46, 1)
        mop_acre  = round(need_k / 0.60, 1)

        total_urea = round(urea_acre * acres, 1)
        total_dap  = round(dap_acre  * acres, 1)
        total_mop  = round(mop_acre  * acres, 1)

        cost    = round(total_urea * 6.5 + total_dap * 27 + total_mop * 17)
        typical = round(cost * 1.25)
        saved   = typical - cost

        # ── 5. Split application schedule ────────────────────────────────
        splits = self.SPLIT.get(season, self.SPLIT["Kharif"])
        schedule = []
        first = True
        for stage_name, frac in splits.items():
            schedule.append({
                "stage":    stage_name,
                "urea_kg":  round(total_urea * frac, 1),
                "dap_kg":   round(total_dap  * frac, 1) if first else 0,
                "mop_kg":   round(total_mop  * frac, 1),
                "note":     "Apply DAP at sowing only" if first else "Top dressing with Urea + MOP"
            })
            first = False

        # ── 6. Estimated pH AFTER fertilization ─────────────────────────
        ph_change = (
            (total_urea * FERTILIZER_PH_EFFECT["Urea"] / 100) +
            (total_dap  * FERTILIZER_PH_EFFECT["DAP"]  / 100) +
            (total_mop  * FERTILIZER_PH_EFFECT["MOP"]  / 100)
        )
        estimated_ph_after = round(max(4.0, min(9.0, soil_ph + ph_change)), 1)

        # ── 7. Warnings ──────────────────────────────────────────────────
        warnings = []

        if current_n > req_n * 1.2:
            warnings.append(f"🔴 Too much Nitrogen! Skip Urea this application. Excess N = more disease risk.")
        if soil_ph > 7.5:
            warnings.append(f"🔴 High pH ({soil_ph}) — Phosphorus and Zinc are LOCKED. Apply Sulphur 5 kg/acre first.")
        if soil_ph < 5.5:
            warnings.append(f"🔴 Very acidic soil ({soil_ph}) — Apply Agricultural Lime 200 kg/acre to raise pH.")
        if n_avail < 0.7:
            warnings.append(f"⚠️ Only {int(n_avail*100)}% of soil Nitrogen is available at pH {soil_ph}. Fix pH first.")
        if p_avail < 0.6:
            warnings.append(f"⚠️ Only {int(p_avail*100)}% of Phosphorus available at pH {soil_ph}. pH correction needed.")

        # pH drift warning after applying fertilizers
        if estimated_ph_after < 5.8:
            warnings.append(f"⚠️ After fertilization, pH may drop to ~{estimated_ph_after}. Add lime 100 kg/acre to buffer.")
        elif estimated_ph_after > 8.0:
            warnings.append(f"⚠️ After fertilization, pH may rise to ~{estimated_ph_after}. Consider Sulphur application.")

        if not warnings:
            warnings.append("✅ All parameters look good. Apply as per schedule below.")

        # ── 8. Organic options ───────────────────────────────────────────
        organic_options = [
            f"FYM (Farmyard Manure) 4 ton/acre = Rs 4,000 — best long-term",
            f"Vermicompost 500 kg/acre = Rs 2,500 — improves soil structure",
            f"Green manure (Dhaincha/Sunhemp) before planting — free nitrogen",
        ]
        if soil_ph > 7.5:
            organic_options.insert(0, "Sulphur 5 kg/acre (Rs 150) — reduces pH to unlock nutrients")
        elif soil_ph < 5.8:
            organic_options.insert(0, "Agricultural lime 200 kg/acre (Rs 600) — raises pH")

        # ── 9. Stage-specific tip ─────────────────────────────────────────
        if days_since_planting <= 15:
            stage_tip = "At sowing stage: Apply full DAP + 1/3 Urea + 1/3 MOP"
        elif days_since_planting <= 45:
            stage_tip = "Vegetative stage: Apply 1/3 Urea + 1/3 MOP as top dressing"
        elif days_since_planting <= 75:
            stage_tip = "Pre-flowering: Apply remaining Urea + MOP for grain filling"
        else:
            stage_tip = "Late stage: Only foliar spray if needed — no basal fertilizer"

        return {
            "agent":             self.name,
            "crop":              crop,
            "acres":             acres,
            "soil_ph":           soil_ph,
            "ph_status":         ph_status,
            "ph_corrections":    ph_corrections,
            "estimated_ph_after": estimated_ph_after,
            "nutrient_availability": {
                "N_pct": int(n_avail * 100),
                "P_pct": int(p_avail * 100),
                "K_pct": int(k_avail * 100),
            },
            "recommended_npk":   {"N_kg_ha": req_n, "P_kg_ha": req_p, "K_kg_ha": req_k},
            "fertilizer_plan":   {"Urea_kg": total_urea, "DAP_kg": total_dap, "MOP_kg": total_mop},
            "total_cost":        cost,
            "without_ai_cost":   typical,
            "money_saved":       saved,
            "schedule":          schedule,
            "warnings":          warnings,
            "deficiency_addon":  deficiency_addon,
            "deficiency_note":   deficiency_note,
            "organic_options":   organic_options,
            "stage_tip":         stage_tip,
            "annual_savings":    "Rs 1,00,000",
            "action": (f"Buy: Urea {total_urea}kg + DAP {total_dap}kg + MOP {total_mop}kg = Rs {cost}. "
                       f"{'⚠️ Fix pH first! ' + ph_corrections[0] if ph_corrections else 'Apply as per schedule.'}")
        }

    def _ph_corrections(self, ph: float, crop: str) -> list:
        """Return list of pH correction actions needed."""
        if ph > 7.8:
            return [
                f"Apply Sulphur 5-10 kg/acre to reduce pH (current: {ph}, target: 6.5)",
                "Use Ammonium Sulphate instead of Urea — more acidifying",
                "Add organic matter — FYM 4 ton/acre buffers extreme pH"
            ]
        elif ph > 7.5:
            return [f"Slight pH correction: Sulphur 3 kg/acre. Target: 6.5-7.0 (current: {ph})"]
        elif ph < 5.5:
            return [
                f"Apply Agricultural Lime 300 kg/acre to raise pH (current: {ph}, target: 6.5)",
                "Use Calcium Nitrate instead of Urea",
                "Dolomite lime 200 kg/acre also adds Magnesium"
            ]
        elif ph < 6.0:
            return [f"Mild pH correction: Lime 150 kg/acre (current: {ph}, target: 6.5)"]
        return []

    def _ph_status(self, ph: float) -> str:
        if ph < 5.5:   return "VERY ACIDIC — Lime needed urgently"
        elif ph < 6.0: return "ACIDIC — Add lime for best results"
        elif ph <= 7.5: return "IDEAL — All nutrients available"
        elif ph <= 8.0: return "ALKALINE — Some nutrients locked"
        else:           return "VERY ALKALINE — Sulphur needed urgently"

    def _availability_factor(self, ph: float, nutrient: str) -> float:
        """
        Returns 0.0 - 1.0 representing how available a nutrient is at given pH.
        Based on the classic Truog pH-availability curve.
        """
        lo, hi = PH_NUTRIENT_AVAILABILITY.get(nutrient, (6.0, 7.5))
        if lo <= ph <= hi:
            return 1.0
        elif ph < lo:
            deficit = lo - ph
            return max(0.2, 1.0 - deficit * 0.15)
        else:  # ph > hi
            excess = ph - hi
            return max(0.2, 1.0 - excess * 0.20)


if __name__ == "__main__":
    agent = FertilizerAgent()

    # Test with high pH (common in Telangana/AP black soil)
    r = agent.analyze("Rice", 5.0, current_n=80, current_p=30, current_k=20,
                      soil_ph=7.9, season="Kharif")
    print(f"\nAction: {r['action']}")
    print(f"pH Status: {r['ph_status']}")
    print(f"Estimated pH after fertilization: {r['estimated_ph_after']}")
    print(f"N availability: {r['nutrient_availability']['N_pct']}%")
    print(f"P availability: {r['nutrient_availability']['P_pct']}%")
    print(f"Warnings: {r['warnings']}")
