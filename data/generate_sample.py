"""
Farm AI - Sample Data Generator
Creates synthetic 50K farm dataset for training/demo
Run: python data/generate_sample.py
"""

import numpy as np
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.crop_data import CROPS, STATE_ML_PERFORMANCE


def generate_farm_dataset(n_samples=50000, save_path="data/farm_data.csv"):
    """Generate realistic synthetic farm data for 28 Indian states."""
    np.random.seed(42)
    
    states = list(STATE_ML_PERFORMANCE.keys())
    crops = list(CROPS.keys())
    seasons = ["Kharif", "Rabi", "Summer"]
    soil_types = ["Clay", "Sandy", "Loamy", "Black", "Red", "Alluvial"]
    irrigation = ["Drip", "Sprinkler", "Flood", "Rain-fed"]
    
    data = []
    samples_per_state = n_samples // len(states)
    
    print(f"🌾 Generating {n_samples:,} farm records across {len(states)} states...")
    
    for state in states:
        state_r2 = STATE_ML_PERFORMANCE[state]["r2"]
        noise_factor = 1 - state_r2  # Higher noise = lower R²
        
        for _ in range(samples_per_state):
            crop = np.random.choice(crops)
            crop_info = CROPS[crop]
            
            # Soil features
            ph = np.clip(np.random.normal(6.5, 0.8), 4.5, 9.0)
            nitrogen = np.clip(np.random.normal(crop_info["nitrogen"], 30), 0, 300)
            phosphorus = np.clip(np.random.normal(crop_info["phosphorus"], 15), 0, 150)
            potassium = np.clip(np.random.normal(crop_info["potassium"], 12), 0, 150)
            organic_matter = np.clip(np.random.normal(1.8, 0.6), 0.2, 5.0)
            
            # Weather features
            rainfall_mm = np.clip(np.random.normal(800, 300), 200, 2500)
            temperature_avg = np.clip(np.random.normal(27, 5), 10, 45)
            humidity_avg = np.clip(np.random.normal(70, 15), 20, 100)
            
            # Farm features
            farm_size = np.clip(np.random.exponential(3), 0.5, 50)
            season = np.random.choice(seasons)
            soil_type = np.random.choice(soil_types)
            irrigation_type = np.random.choice(irrigation)
            year = np.random.randint(2015, 2025)
            
            # Fertilizer inputs
            urea_applied = np.clip(np.random.normal(nitrogen * 2.17, 30), 0, 600)
            dap_applied = np.clip(np.random.normal(phosphorus * 2.17, 20), 0, 400)
            
            # Pest incidence (0-1)
            pest_incidence = np.clip(np.random.beta(2, 8), 0, 1)
            
            # Calculate base yield
            base_yield = crop_info["avg_yield_kg_acre"]
            
            # pH effect (bell curve, best at optimal)
            ph_optimal = (crop_info["ph_min"] + crop_info["ph_max"]) / 2
            ph_penalty = max(0, 1 - abs(ph - ph_optimal) * 0.3)
            
            # Nutrient effect
            n_effect = min(1.2, nitrogen / crop_info["nitrogen"])
            p_effect = min(1.1, phosphorus / crop_info["phosphorus"])
            k_effect = min(1.1, potassium / crop_info["potassium"])
            
            # Rainfall effect
            optimal_rain = crop_info["water_mm_per_week"] * (crop_info["grow_days"] / 7)
            rain_effect = min(1.15, rainfall_mm / (optimal_rain + 1))
            rain_effect = min(rain_effect, 2000 / max(rainfall_mm, 1))
            
            # Pest loss
            pest_loss = 1 - (pest_incidence * 0.4)
            
            # State-specific noise (models Bihar harder)
            noise = np.random.normal(0, noise_factor * 400)
            
            # Final yield
            yield_kg = base_yield * ph_penalty * n_effect * p_effect * k_effect * rain_effect * pest_loss
            yield_kg = max(50, yield_kg + noise)
            
            data.append({
                "state": state,
                "crop": crop,
                "season": season,
                "year": year,
                "farm_size_acres": round(farm_size, 2),
                "soil_type": soil_type,
                "irrigation_type": irrigation_type,
                "soil_ph": round(ph, 2),
                "nitrogen_kg_ha": round(nitrogen, 1),
                "phosphorus_kg_ha": round(phosphorus, 1),
                "potassium_kg_ha": round(potassium, 1),
                "organic_matter_pct": round(organic_matter, 2),
                "rainfall_mm": round(rainfall_mm, 1),
                "temperature_avg_c": round(temperature_avg, 1),
                "humidity_avg_pct": round(humidity_avg, 1),
                "urea_applied_kg": round(urea_applied, 1),
                "dap_applied_kg": round(dap_applied, 1),
                "pest_incidence": round(pest_incidence, 3),
                "yield_kg_acre": round(max(yield_kg, 0), 1),
            })
    
    df = pd.DataFrame(data)
    
    # Save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    
    print(f"✅ Dataset saved: {save_path}")
    print(f"📊 Shape: {df.shape}")
    print(f"🌾 Crops: {df['crop'].nunique()}")
    print(f"🗺️  States: {df['state'].nunique()}")
    print(f"📈 Avg Yield: {df['yield_kg_acre'].mean():.0f} kg/acre")
    
    return df


if __name__ == "__main__":
    df = generate_farm_dataset(50000, "data/farm_data.csv")
    print("\nSample records:")
    print(df.head(3).to_string())
