"""Farm AI - Helper utilities"""
import datetime, os, sys

def format_rupees(amount: float) -> str:
    amount = int(amount)
    if amount >= 10000000: return f"Rs {amount/10000000:.1f} Cr"
    if amount >= 100000:   return f"Rs {amount/100000:.1f} L"
    if amount >= 1000:     return f"Rs {amount/1000:.0f}K"
    return f"Rs {amount}"

def get_season(month: int = None) -> str:
    m = month or datetime.datetime.now().month
    if m in [6, 7, 8, 9, 10]: return "Kharif"
    if m in [11, 12, 1, 2, 3]: return "Rabi"
    return "Summer"

def get_growth_stage(days: int, grow_days: int) -> str:
    if grow_days <= 0: return "vegetative"
    p = days / grow_days
    if p < 0.15: return "seedling"
    if p < 0.40: return "vegetative"
    if p < 0.65: return "flowering"
    if p < 0.85: return "grain_fill"
    return "maturity"

def format_rupees_v(amount):
    if amount >= 100000:   return f"Rs {amount/100000:.1f}L"
    if amount >= 1000:     return f"Rs {amount/1000:.0f}K"
    return f"Rs {int(amount)}"

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Meghalaya", "Odisha",
    "Punjab", "Rajasthan", "Tamil Nadu", "Telangana", "Uttar Pradesh",
    "Uttarakhand", "West Bengal",
]

# All 42 crops — imported from crop_data to stay in sync
def _get_crop_list():
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from data.crop_data import CROPS
        return sorted(CROPS.keys())
    except Exception:
        return [
            "Rice", "Wheat", "Maize", "Jowar", "Bajra", "Ragi", "Barley",
            "Cotton", "Sugarcane", "Jute", "Tobacco",
            "Groundnut", "Soybean", "Mustard", "Sunflower", "Sesame", "Linseed", "Castor",
            "Chickpea", "Pigeonpea", "Moong", "Urad", "Lentil", "Cowpea",
            "Tomato", "Onion", "Potato", "Brinjal", "Chilli", "Okra",
            "Turmeric", "Ginger", "Garlic", "Coriander", "Cardamom", "Black Pepper",
            "Banana", "Mango", "Coconut", "Pomegranate", "Papaya", "Grapes", "Flower Crops",
        ]

CROP_LIST = _get_crop_list()
