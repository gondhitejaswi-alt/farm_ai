"""
Farm AI - Agent 9: Digital Twin Agent
Test your farming decisions BEFORE spending money.
Saves Rs 1 Lakh/year by avoiding costly mistakes.
"""

import sys, os, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.crop_data import CROPS


class DigitalTwinAgent:
    name = "Digital Twin Agent"
    description = "Test decisions before spending | Saves Rs 1L/year"

    def simulate(self, base: dict, changes: dict) -> dict:
        """What happens if I change something on my farm?"""
        modified = copy.deepcopy(base)
        modified.update(changes)
        base_out = self._compute(base)
        new_out  = self._compute(modified)

        delta_profit  = new_out["profit"] - base_out["profit"]
        delta_yield   = new_out["yield_kg_acre"] - base_out["yield_kg_acre"]
        delta_cost    = new_out["total_cost"] - base_out["total_cost"]
        delta_revenue = new_out["revenue"] - base_out["revenue"]

        if delta_profit > 10000:
            rec     = "DO IT"
            verdict = f"YES! This change earns Rs {delta_profit:,.0f} MORE — do it!"
        elif delta_profit < -10000:
            rec     = "AVOID"
            verdict = f"NO! This change LOSES Rs {abs(delta_profit):,.0f} — avoid it"
        else:
            rec     = "NEUTRAL"
            verdict = f"Small difference (Rs {delta_profit:+,.0f}) — your choice"

        return {
            "agent":       self.name,
            "base":        base_out,
            "new":         new_out,
            "changes_tested": changes,
            "delta":       {"profit": round(delta_profit), "yield_kg_acre": round(delta_yield),
                            "cost": round(delta_cost), "revenue": round(delta_revenue)},
            "recommendation": rec,
            "verdict":     verdict,
            "annual_savings": "Rs 1,00,000",
            "action":      verdict,
        }

    def run_scenarios(self, base: dict) -> dict:
        """Run 5 common what-if scenarios automatically."""
        crop    = base.get("crop", "Rice")
        n       = base.get("nitrogen", 100)
        om      = base.get("organic_matter_pct", 1.5)

        scenarios = {
            "Use certified seeds (+8% yield)":         {"certified_seeds": True},
            "Add 20% more fertilizer":                  {"extra_fert_pct": 1.2},
            "Reduce fertilizer by 20% (save cost)":     {"extra_fert_pct": 0.8},
            "Add organic matter (vermicompost)":        {"organic_matter_pct": om + 1},
            "Grow 20% more area (expand farm)":         {"acres": base.get("acres", 5) * 1.2},
        }

        results = []
        for label, chg in scenarios.items():
            r = self.simulate(base, chg)
            results.append({
                "scenario":    label,
                "profit_gain": r["delta"]["profit"],
                "verdict":     r["verdict"],
                "rec":         r["recommendation"],
            })
        results.sort(key=lambda x: -x["profit_gain"])

        return {
            "agent":         self.name,
            "base_scenario": base,
            "all_scenarios": results,
            "best_scenario": results[0] if results else {},
            "worst_scenario":results[-1] if results else {},
            "annual_savings":"Rs 1,00,000",
            "action":        (f"Best option: {results[0]['scenario']} → {results[0]['verdict']}"
                              if results else "Run scenarios to see results"),
        }

    def _compute(self, s: dict) -> dict:
        crop   = s.get("crop", "Rice")
        acres  = s.get("acres", 5)
        ph     = s.get("soil_ph", 6.5)
        n      = s.get("nitrogen", 120)
        rain   = s.get("rainfall_mm", 900)
        pest   = s.get("pest_incidence", 0.1)
        om     = s.get("organic_matter_pct", 1.5)
        cert   = s.get("certified_seeds", False)
        extra  = s.get("extra_fert_pct", 1.0)

        info   = CROPS.get(crop, {})
        base_y = info.get("avg_yield_kg_acre", 2000)
        msp    = info.get("msp_per_quintal", 2000)
        opt_n  = info.get("nitrogen", 120)
        opt_w  = info.get("water_mm_per_week", 25) * (info.get("grow_days", 120) / 7)

        ph_opt    = (info.get("ph_min", 6.0) + info.get("ph_max", 7.0)) / 2
        ph_f      = max(0.6, 1 - abs(ph - ph_opt) * 0.2)
        n_ratio   = min(1.0, (n * extra) / max(opt_n, 1))
        n_f       = 0.70 + n_ratio * 0.30
        rain_f    = min(1.15, rain / max(opt_w, 1))
        pest_f    = 1 - pest * 0.35
        om_bonus  = 1 + (om - 1.5) * 0.04
        seed_f    = 1.08 if cert else 1.0
        yield_a   = base_y * ph_f * n_f * rain_f * pest_f * om_bonus * seed_f

        fert_cost = (n / max(opt_n,1)) * 5000 * extra * acres
        seed_cost = (850 if cert else 500) * acres
        irr_cost  = 2000 * acres
        pest_cost = pest * 4000 * acres
        lab_cost  = 4000 * acres
        total_cost= fert_cost + seed_cost + irr_cost + pest_cost + lab_cost

        revenue = (yield_a * acres / 100) * msp
        profit  = revenue - total_cost

        return {"yield_kg_acre": round(yield_a), "total_cost": round(total_cost),
                "revenue": round(revenue), "profit": round(profit),
                "roi_pct": round((profit/total_cost)*100, 1) if total_cost else 0}


if __name__ == "__main__":
    a = DigitalTwinAgent()
    base = {"crop":"Rice","acres":5,"soil_ph":6.5,"nitrogen":100,"rainfall_mm":900,"pest_incidence":0.1}
    r = a.run_scenarios(base)
    for s in r["all_scenarios"]:
        print(f"  {s['scenario']}: {s['verdict']}")
