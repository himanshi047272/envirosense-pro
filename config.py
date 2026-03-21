# ============================================
# config.py — EnviroSense Pro Configuration
# ============================================
# ⚠️  DO NOT commit real API keys to GitHub!
#     Use a .env file for production.
#     This file shows the structure only.
# ============================================

import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file if present

# ── OpenWeatherMap API ──────────────────────
OWM_API_KEY = os.getenv("OWM_API_KEY", "29a29f1546b0c03d6760d9b17821d667")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"
OWM_GEO_URL  = "https://api.openweathermap.org/geo/1.0"

# ── App Settings ────────────────────────────
APP_HOST      = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT      = int(os.getenv("APP_PORT", 5000))
DEBUG_MODE    = os.getenv("DEBUG", "True") == "True"
SECRET_KEY    = os.getenv("SECRET_KEY", "envirosense-secret-change-in-prod")

# ── Data Paths ──────────────────────────────
DATA_DIR          = "data"
RAW_DATA_PATH     = "data/environment_data.csv"
CLEANED_DATA_PATH = "data/cleaned_data.csv"

# ── Model Paths ─────────────────────────────
MODEL_DIR         = "models"
MODEL_PATH        = "models/trained_model.pkl"
SCALER_PATH       = "models/scaler.pkl"

# ── Disaster Thresholds ─────────────────────
THRESHOLDS = {
    "storm": {
        "wind_speed_kmh": 40,       # km/h
        "pressure_drop_hpa": 8,     # hPa
        "humidity_pct": 80,         # %
    },
    "flood": {
        "rain_24h_mm": 20,          # mm
        "humidity_pct": 85,         # %
        "rain_48h_mm": 50,          # mm
    },
    "heatwave": {
        "temp_celsius": 38,         # °C
        "feels_like_diff": 4,       # °C above actual
    },
    "coldwave": {
        "temp_celsius": 8,          # °C
        "sudden_drop_celsius": 5,   # °C drop
    },
    "pollution": {
        "aqi_value": 150,           # AQI index
        "pm25_ugm3": 60,            # µg/m³
    },
    "landslide": {
        "rain_24h_mm": 20,          # mm (hilly areas only)
        "rain_72h_mm": 40,          # mm
        "humidity_pct": 80,         # %
    },
}

# ── Alert Weights for Scoring ────────────────
WEIGHTS = {
    "wind_speed":       {"w60+": 40, "w40_60": 25},
    "forecast_wind":    {"w55+": 20},
    "pressure_drop":    {"p8+": 15},
    "humidity":         {"h80+": 10},
    "rain_24h":         {"r15+": 10, "r30+": 40},
    "temperature":      {"t44+": 50, "t40": 35, "t38": 22},
    "heat_index_diff":  {"d4+": 12},
    "aqi":              {"a300+": 60, "a200": 45, "a150": 28},
}

# ── City Database ────────────────────────────
CITIES = [
    {"name": "New Delhi",     "lat": 28.6139, "lon": 77.2090, "hilly": False, "coastal": False},
    {"name": "Mumbai",        "lat": 19.0760, "lon": 72.8777, "hilly": False, "coastal": True},
    {"name": "Srinagar",      "lat": 34.0837, "lon": 74.7973, "hilly": True,  "coastal": False},
    {"name": "Shimla",        "lat": 31.1048, "lon": 77.1734, "hilly": True,  "coastal": False},
    {"name": "Bhubaneswar",   "lat": 20.2961, "lon": 85.8245, "hilly": False, "coastal": True},
    {"name": "Chennai",       "lat": 13.0827, "lon": 80.2707, "hilly": False, "coastal": True},
    {"name": "Bengaluru",     "lat": 12.9716, "lon": 77.5946, "hilly": False, "coastal": False},
    {"name": "Kolkata",       "lat": 22.5726, "lon": 88.3639, "hilly": False, "coastal": True},
    {"name": "Hyderabad",     "lat": 17.3850, "lon": 78.4867, "hilly": False, "coastal": False},
    {"name": "Jaipur",        "lat": 26.9124, "lon": 75.7873, "hilly": False, "coastal": False},
    {"name": "Patna",         "lat": 25.5941, "lon": 85.1376, "hilly": False, "coastal": False},
    {"name": "Guwahati",      "lat": 26.1445, "lon": 91.7362, "hilly": False, "coastal": False},
    {"name": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185, "hilly": False, "coastal": True},
    {"name": "Kochi",         "lat":  9.9312, "lon": 76.2673, "hilly": False, "coastal": True},
    {"name": "Lucknow",       "lat": 26.8467, "lon": 80.9462, "hilly": False, "coastal": False},
    {"name": "Dehradun",      "lat": 30.3165, "lon": 78.0322, "hilly": True,  "coastal": False},
]
