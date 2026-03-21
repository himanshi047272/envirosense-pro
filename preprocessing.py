# ============================================
# preprocessing.py — Data Cleaning & Features
# ============================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import joblib
import os
from config import CLEANED_DATA_PATH, SCALER_PATH


# ── 1. Load Raw Data ─────────────────────────
def load_data(filepath: str) -> pd.DataFrame:
    """Load CSV dataset and return DataFrame."""
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    print(f"[INFO] Loaded {len(df)} rows from {filepath}")
    return df


# ── 2. Inspect Data ──────────────────────────
def inspect_data(df: pd.DataFrame) -> dict:
    """Print basic statistics about the dataset."""
    info = {
        "shape":         df.shape,
        "columns":       list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "dtypes":        df.dtypes.astype(str).to_dict(),
        "numeric_stats": df.describe().to_dict(),
    }
    print("\n📊 Dataset Info:")
    print(f"  Rows: {info['shape'][0]}, Columns: {info['shape'][1]}")
    print(f"  Columns: {info['columns']}")
    print(f"  Missing Values:\n  {info['missing_values']}")
    return info


# ── 3. Handle Missing Values ─────────────────
def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strategy:
    - Numeric columns  → fill with median
    - Category columns → fill with mode
    - Drop rows missing >50% values
    """
    # Drop rows with too many missing values
    thresh = int(0.5 * len(df.columns))
    df = df.dropna(thresh=thresh)

    # Numeric → median imputation
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        imp = SimpleImputer(strategy="median")
        df[num_cols] = imp.fit_transform(df[num_cols])

    # Categorical → mode imputation
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for col in cat_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)

    print(f"[INFO] Missing values handled. Remaining: {df.isnull().sum().sum()}")
    return df


# ── 4. Remove Duplicates ─────────────────────
def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"[INFO] Removed {before - after} duplicate rows.")
    return df


# ── 5. Feature Engineering ───────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new meaningful features from raw data.
    """
    # Temperature features
    if "temperature" in df.columns:
        df["temp_squared"]    = df["temperature"] ** 2
        df["is_heatwave"]     = (df["temperature"] >= 38).astype(int)
        df["is_cold"]         = (df["temperature"] <= 8).astype(int)
        df["is_extreme_temp"] = ((df["temperature"] >= 40) | (df["temperature"] <= 4)).astype(int)

    # Humidity features
    if "humidity" in df.columns:
        df["high_humidity"] = (df["humidity"] >= 85).astype(int)
        df["low_humidity"]  = (df["humidity"] <= 25).astype(int)

    # Wind features
    if "wind_speed" in df.columns:
        df["strong_wind"]  = (df["wind_speed"] >= 40).astype(int)
        df["severe_wind"]  = (df["wind_speed"] >= 60).astype(int)

    # AQI features
    if "aqi" in df.columns:
        df["aqi_category"] = pd.cut(
            df["aqi"],
            bins=[0, 50, 100, 150, 200, 300, 500],
            labels=["Good", "Moderate", "Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
        ).astype(str)
        df["dangerous_aqi"] = (df["aqi"] >= 200).astype(int)

    # Rainfall features
    if "rainfall" in df.columns:
        df["heavy_rain"]   = (df["rainfall"] >= 20).astype(int)
        df["extreme_rain"] = (df["rainfall"] >= 50).astype(int)

    # Pressure features (storm indicator)
    if "pressure" in df.columns:
        df["low_pressure"] = (df["pressure"] <= 1000).astype(int)

    # Combined risk features
    if all(c in df.columns for c in ["temperature", "humidity", "wind_speed"]):
        df["heat_stress_index"] = df["temperature"] * (df["humidity"] / 100) + df["wind_speed"] * 0.1

    if all(c in df.columns for c in ["rainfall", "humidity"]):
        df["flood_risk_index"] = df["rainfall"] * 0.6 + df["humidity"] * 0.4

    print(f"[INFO] Feature engineering done. New shape: {df.shape}")
    return df


# ── 6. Encode Categorical Columns ────────────
def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Label-encode all string/object columns."""
    le = LabelEncoder()
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for col in cat_cols:
        df[col] = le.fit_transform(df[col].astype(str))
        print(f"[INFO] Encoded: {col}")
    return df


# ── 7. Scale Numeric Features ────────────────
def scale_features(
    df: pd.DataFrame,
    target_col: str = "disaster_type",
    save_scaler: bool = True
) -> tuple:
    """
    Standardize numeric features. Returns (X_scaled, y, scaler).
    """
    # Separate features and target
    if target_col in df.columns:
        X = df.drop(columns=[target_col])
        y = df[target_col]
    else:
        X = df.copy()
        y = None

    # Only scale numeric columns
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    scaler = StandardScaler()
    X[num_cols] = scaler.fit_transform(X[num_cols])

    # Save scaler for later use in predictions
    if save_scaler:
        os.makedirs("models", exist_ok=True)
        joblib.dump(scaler, SCALER_PATH)
        print(f"[INFO] Scaler saved to {SCALER_PATH}")

    return X, y, scaler


# ── 8. Full Pipeline ─────────────────────────
def preprocess_pipeline(
    filepath: str,
    target_col: str = "disaster_type",
    save: bool = True
) -> tuple:
    """
    Run complete preprocessing pipeline:
    load → inspect → clean → engineer → encode → scale
    Returns: (X, y, scaler)
    """
    print("\n🔄 Starting preprocessing pipeline...")

    df = load_data(filepath)
    if df.empty:
        raise FileNotFoundError(f"Could not load: {filepath}")

    inspect_data(df)
    df = handle_missing(df)
    df = remove_duplicates(df)
    df = engineer_features(df)
    df = encode_categoricals(df)

    if save:
        os.makedirs("data", exist_ok=True)
        df.to_csv(CLEANED_DATA_PATH, index=False)
        print(f"[INFO] Cleaned data saved to {CLEANED_DATA_PATH}")

    X, y, scaler = scale_features(df, target_col=target_col)
    print("✅ Preprocessing complete.\n")
    return X, y, scaler


# ── 9. Load Existing Scaler ──────────────────
def load_scaler() -> StandardScaler:
    """Load saved scaler from disk."""
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}. Run preprocessing first.")
    return joblib.load(SCALER_PATH)


# ── 10. Prepare Live API Data ────────────────
def prepare_live_data(weather_dict: dict) -> pd.DataFrame:
    """
    Convert live OpenWeatherMap API response into a
    DataFrame row ready for model prediction.
    """
    row = {
        "temperature":  weather_dict.get("temp", 0),
        "feels_like":   weather_dict.get("feels_like", 0),
        "humidity":     weather_dict.get("humidity", 0),
        "pressure":     weather_dict.get("pressure", 1013),
        "wind_speed":   weather_dict.get("wind_speed", 0),
        "rainfall":     weather_dict.get("rainfall", 0),
        "aqi":          weather_dict.get("aqi", 50),
        "pm25":         weather_dict.get("pm25", 10),
        "visibility":   weather_dict.get("visibility", 10),
    }
    df = pd.DataFrame([row])
    df = engineer_features(df)

    # Scale using saved scaler
    try:
        scaler = load_scaler()
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        df[num_cols] = scaler.transform(df[num_cols])
    except FileNotFoundError:
        print("[WARN] Scaler not found — using unscaled features.")

    return df


# ── Run standalone ───────────────────────────
if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else "data/environment_data.csv"
    X, y, scaler = preprocess_pipeline(filepath)
    print(f"Final feature shape: {X.shape}")
    if y is not None:
        print(f"Target classes: {y.unique()}")
