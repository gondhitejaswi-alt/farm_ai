"""
Farm AI - Dataset Merger
Merges Kaggle CSV (1966-2017) + DSV XLS (2018-2023) into one clean dataset.
Run: python data/merge_datasets.py

Inputs:
  data/Custom_Crops_yield_Historical_Dataset.csv  (from Kaggle)
  data/horizontal_crop_vertical_year_report.xls   (from DSV website)

Output:
  data/merged_farm_data.csv  (61K rows, 42 crops, 28 states, 1966-2022)
"""

import pandas as pd, numpy as np, re, os, subprocess, sys

BASE = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE, "Custom_Crops_yield_Historical_Dataset.csv")
XLS_PATH = os.path.join(BASE, "horizontal_crop_vertical_year_report.xls")
OUT_PATH = os.path.join(BASE, "merged_farm_data.csv")

CROP_MAP = {
    "Cotton(lint)": "Cotton", "Maize": "Maize", "Groundnut": "Groundnut",
    "Wheat": "Wheat", "Gram": "Chickpea", "Jowar": "Jowar", "Ragi": "Ragi",
    "Turmeric": "Turmeric", "Onion": "Onion", "Potato": "Potato",
    "Sugarcane": "Sugarcane", "Arhar/Tur": "Arhar",
    "Rapeseed &Mustard": "Mustard", "Sunflower": "Sunflower",
    "Sesamum": "Sesamum", "Castor seed": "Castor", "Ginger": "Ginger",
    "Dry chillies": "Chilli", "Banana": "Banana",
    "Coconut": "Coconut", "Mango": "Mango",
}
STATE_FIX = {"Orissa": "Odisha"}


def parse_xls(xls_path: str) -> pd.DataFrame:
    """Convert XLS wide format -> long format."""
    tmp = "/tmp/_xls_converted.csv"
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "csv", xls_path, "--outdir", "/tmp/"],
        capture_output=True, timeout=60
    )
    converted = tmp.replace("_xls_converted.csv",
                            os.path.basename(xls_path).replace(".xls", ".csv"))
    if not os.path.exists(converted):
        raise FileNotFoundError("LibreOffice conversion failed")
    raw = pd.read_csv(converted, header=None)

    # Build crop->(area_col, prod_col, yield_col) map
    row0, row2 = raw.iloc[0], raw.iloc[2]
    crop_cols = {}
    cur = None
    for i, val in enumerate(row0):
        if pd.notna(val) and i >= 3:
            cur = str(val).strip()
    for i, val in enumerate(row2):
        if i < 3: continue
        if pd.notna(row0.iloc[i]):
            cur = str(row0.iloc[i]).strip()
        if "Yield" in str(val) and cur:
            crop_cols[cur] = (i-2, i-1, i)

    data = raw.iloc[3:].copy()
    data.columns = range(len(data.columns))
    data[0] = data[0].ffill()
    data[1] = data[1].ffill()
    data[0] = data[0].apply(lambda x: re.sub(r'^\d+\.\s*', '', str(x)).strip())
    data = data[data[2].notna() & data[2].astype(str).str.match(r'\d{4}')]

    records = []
    for _, row in data.iterrows():
        state = str(row[0]).strip()
        dist  = str(row[1]).strip()
        year_m = re.match(r'(\d{4})', str(row[2]))
        if not year_m: continue
        year = int(year_m.group(1))
        for crop, (ac, pc, yc) in crop_cols.items():
            try:
                y = float(str(row[yc]).replace(",", ""))
                a = float(str(row[ac]).replace(",", ""))
                if y <= 0 or a <= 0 or y > 40: continue  # filter nuts/bales outliers
                records.append({"state": state, "district": dist, "year": year,
                                "crop": CROP_MAP.get(crop, crop),
                                "area_ha": a, "yield_kg_ha": y * 1000})
            except: pass
    return pd.DataFrame(records)


def main():
    print("Farm AI - Merging Real Datasets")
    print("=" * 50)

    # ── Kaggle CSV ─────────────────────────────────────────
    if not os.path.exists(CSV_PATH):
        print(f"Missing: {CSV_PATH}")
        print("Download from: https://www.kaggle.com/datasets/zoya77/indian-historical-crop-yield-and-weather-data")
        sys.exit(1)
    df_csv = pd.read_csv(CSV_PATH)
    df1 = pd.DataFrame({
        "state": df_csv["State Name"].replace(STATE_FIX),
        "district": df_csv["Dist Name"],
        "year": df_csv["Year"],
        "crop": df_csv["Crop"].str.title(),
        "area_ha": df_csv["Area_ha"],
        "yield_kg_ha": df_csv["Yield_kg_per_ha"],
        "nitrogen": df_csv["N_req_kg_per_ha"],
        "phosphorus": df_csv["P_req_kg_per_ha"],
        "potassium": df_csv["K_req_kg_per_ha"],
        "temperature_c": df_csv["Temperature_C"],
        "humidity_pct": df_csv["Humidity_%"],
        "soil_ph": df_csv["pH"],
        "rainfall_mm": df_csv["Rainfall_mm"],
        "wind_speed": df_csv["Wind_Speed_m_s"],
        "solar_rad": df_csv["Solar_Radiation_MJ_m2_day"],
        "source": "kaggle_1966_2017",
    })
    print(f"Kaggle CSV: {len(df1):,} rows | {df1['year'].min()}-{df1['year'].max()}")

    # ── XLS ────────────────────────────────────────────────
    if not os.path.exists(XLS_PATH):
        print(f"Missing: {XLS_PATH}")
        print("Download from DSV website (2018-2023 data)")
        df2 = pd.DataFrame()
    else:
        df_xls = parse_xls(XLS_PATH)
        df2 = df_xls.assign(source="dsv_2018_2023")
        for col in ["nitrogen","phosphorus","potassium","temperature_c",
                    "humidity_pct","soil_ph","rainfall_mm","wind_speed","solar_rad"]:
            df2[col] = np.nan
        print(f"XLS data:   {len(df2):,} rows | {df2['year'].min()}-{df2['year'].max()}")

    # ── Merge ──────────────────────────────────────────────
    df = pd.concat([df1, df2], ignore_index=True)
    df = df[(df["yield_kg_ha"] > 0) & (df["area_ha"] > 0)]
    df.to_csv(OUT_PATH, index=False)

    print(f"\nMerged: {len(df):,} rows saved to {OUT_PATH}")
    print(f"States: {df['state'].nunique()} | Crops: {df['crop'].nunique()}")
    print(f"Years: {df['year'].min()} - {df['year'].max()}")


if __name__ == "__main__":
    main()
