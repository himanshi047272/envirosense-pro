# ============================================
# main.py — EnviroSense Pro Entry Point
# ============================================
#
#  Usage:
#    python main.py                → Start full Flask app
#    python main.py --train        → Train ML model
#    python main.py --preprocess   → Run data pipeline only
#    python main.py --alert Delhi  → Run alerts for a city
#    python main.py --demo         → Demo mode (no API key)
#
# ============================================

import sys
import os
import argparse

def run_app():
    """Start the Flask web server."""
    from app import app
    from config import APP_HOST, APP_PORT, DEBUG_MODE
    print("=" * 55)
    print("  🛰️  EnviroSense Pro — Starting Server")
    print(f"  Dashboard: http://localhost:{APP_PORT}")
    print(f"  API Docs:  http://localhost:{APP_PORT}/health")
    print("=" * 55)
    app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG_MODE)


def run_training():
    """Train the ML disaster prediction model."""
    from model import (
        train_all_models, evaluate_models, split_data,
        save_model, detailed_report, feature_importance
    )
    from preprocessing import preprocess_pipeline

    data_path = "data/environment_data.csv"
    if not os.path.exists(data_path):
        print(f"[ERROR] Dataset not found: {data_path}")
        print("  Please place your CSV file in the data/ folder.")
        print("  Expected columns: temperature, humidity, wind_speed,")
        print("                    pressure, rainfall, aqi, disaster_type")
        sys.exit(1)

    print("🤖 Starting ML Training Pipeline...")
    X, y, scaler     = preprocess_pipeline(data_path)
    X_train, X_test, y_train, y_test = split_data(X, y)
    all_models       = train_all_models(X_train, y_train)
    results_df       = evaluate_models(all_models, X_test, y_test)

    print("\n", results_df.to_string(index=False))

    best_name  = results_df.iloc[0]["Model"]
    best_model = all_models[best_name]
    detailed_report(best_model, X_test, y_test, best_name)
    feature_importance(best_model, list(X.columns))
    save_model(best_model)
    print(f"\n✅ Training complete! Best model: {best_name}")


def run_preprocessing():
    """Run only the data preprocessing pipeline."""
    from preprocessing import preprocess_pipeline
    data_path = "data/environment_data.csv"
    X, y, scaler = preprocess_pipeline(data_path)
    print(f"\n✅ Done. Features shape: {X.shape}")


def run_alert_demo(city_name: str):
    """Run the alert system for a given city (requires API key)."""
    import requests
    from config import OWM_API_KEY, OWM_BASE_URL, CITIES
    from alerts import generate_alerts, print_all_alerts, alert_summary

    city_obj = next((c for c in CITIES if c["name"].lower() == city_name.lower()), None)
    if not city_obj:
        print(f"[ERROR] City '{city_name}' not found.")
        print(f"  Available: {[c['name'] for c in CITIES]}")
        return

    print(f"\n🌍 Fetching live data for {city_obj['name']}...")
    try:
        w_res  = requests.get(f"{OWM_BASE_URL}/weather",
                               params={"lat": city_obj["lat"], "lon": city_obj["lon"],
                                       "appid": OWM_API_KEY, "units": "metric"}, timeout=10)
        aq_res = requests.get(f"{OWM_BASE_URL}/air_pollution",
                               params={"lat": city_obj["lat"], "lon": city_obj["lon"],
                                       "appid": OWM_API_KEY}, timeout=10)
        fc_res = requests.get(f"{OWM_BASE_URL}/forecast",
                               params={"lat": city_obj["lat"], "lon": city_obj["lon"],
                                       "appid": OWM_API_KEY, "units": "metric", "cnt": 24}, timeout=10)

        if not w_res.ok:
            print(f"[ERROR] API returned {w_res.status_code}. Check your API key.")
            return

        w  = w_res.json()
        aq = aq_res.json()
        fc = fc_res.json()

        pm25 = aq["list"][0]["components"].get("pm2_5", 10)
        forecast_list = fc.get("list", [])

        weather = {
            "temp":          round(w["main"]["temp"]),
            "feels_like":    round(w["main"]["feels_like"]),
            "humidity":      w["main"]["humidity"],
            "pressure":      w["main"]["pressure"],
            "wind_speed":    round(w["wind"]["speed"] * 3.6),
            "rain_24h":      sum((f.get("rain") or {}).get("3h", 0) for f in forecast_list[:8]),
            "rain_48h":      sum((f.get("rain") or {}).get("3h", 0) for f in forecast_list[:16]),
            "rain_72h":      sum((f.get("rain") or {}).get("3h", 0) for f in forecast_list[:24]),
            "pressure_drop": w["main"]["pressure"] - min(
                (f["main"]["pressure"] for f in forecast_list[:16]), default=w["main"]["pressure"]
            ),
            "aqi":           int(50 / 12 * pm25) if pm25 <= 12 else min(500, int(100 + pm25 * 0.5)),
            "pm25":          round(pm25, 1),
            "is_hilly":      city_obj.get("hilly", False),
            "is_coastal":    city_obj.get("coastal", False),
        }

        print(f"\n📊 Current Conditions — {city_obj['name']}:")
        print(f"  🌡️  Temperature:  {weather['temp']}°C (feels {weather['feels_like']}°C)")
        print(f"  💧  Humidity:    {weather['humidity']}%")
        print(f"  💨  Wind Speed:  {weather['wind_speed']} km/h")
        print(f"  😷  AQI:         {weather['aqi']}")
        print(f"  🌧️  Rain 24h:    {weather['rain_24h']:.1f} mm")

        alerts = generate_alerts(weather, city=city_obj["name"])
        print_all_alerts(alerts, city=city_obj["name"])

        s = alert_summary(alerts)
        print(f"\n📋 Summary: {s['status']}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] No internet connection.")
    except Exception as e:
        print(f"[ERROR] {e}")


def run_demo():
    """Demo mode with simulated data — no API key needed."""
    from alerts import generate_alerts, print_all_alerts, alert_summary
    from chatbot import EnviroBot

    print("\n🎮 DEMO MODE — Simulated Srinagar Winter")
    print("=" * 45)

    demo_weather = {
        "temp": 2, "feels_like": -4, "humidity": 88,
        "pressure": 1004, "pressure_drop": 9,
        "wind_speed": 42, "rain_24h": 28,
        "rain_48h": 55, "rain_72h": 80,
        "aqi": 75, "pm25": 22,
        "is_hilly": True, "is_coastal": False,
    }

    print(f"📍 City: Srinagar, Kashmir")
    print(f"🌡️  Temp: {demo_weather['temp']}°C · Wind: {demo_weather['wind_speed']} km/h")
    print(f"🌧️  Rain 24h: {demo_weather['rain_24h']}mm · AQI: {demo_weather['aqi']}")

    alerts = generate_alerts(demo_weather, city="Srinagar")
    print_all_alerts(alerts, "Srinagar")

    # Demo chatbot
    bot = EnviroBot()
    bot.update_context(demo_weather, [], "Srinagar")

    print("\n🤖 CHATBOT DEMO:")
    print("-" * 35)
    for q in ["Is it safe to go outside?", "Storm risk?", "Tell me about disasters"]:
        print(f"\n👤 {q}")
        print(f"🤖 {bot.chat(q)}")


# ── Argument Parser ───────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EnviroSense Pro — Smart Environmental Monitoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                   # Start Flask web app
  python main.py --train           # Train ML model
  python main.py --preprocess      # Preprocess data only
  python main.py --alert Srinagar  # Show alerts for city
  python main.py --demo            # Demo mode (no API key)
        """
    )

    parser.add_argument("--train",       action="store_true",  help="Train ML model")
    parser.add_argument("--preprocess",  action="store_true",  help="Run preprocessing only")
    parser.add_argument("--alert",       type=str, metavar="CITY", help="Get alerts for city")
    parser.add_argument("--demo",        action="store_true",  help="Run demo (no API key)")

    args = parser.parse_args()

    if args.train:
        run_training()
    elif args.preprocess:
        run_preprocessing()
    elif args.alert:
        run_alert_demo(args.alert)
    elif args.demo:
        run_demo()
    else:
        run_app()
