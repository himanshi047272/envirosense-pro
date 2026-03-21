# ============================================
# app.py — Flask Backend (EnviroSense Pro)
# ============================================

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import requests
import os
from datetime import datetime

from config import OWM_API_KEY, OWM_BASE_URL, APP_HOST, APP_PORT, DEBUG_MODE, CITIES
from alerts import generate_alerts, alert_summary
from chatbot import EnviroBot
from model import rule_based_predict, predict_disaster
from visualization import (
    plot_temperature_trend, plot_aqi_gauge,
    plot_humidity_temp, plot_7day_risk
)

# ── Flask App Setup ──────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ── Global chatbot instance ──────────────────
bot = EnviroBot()


# ════════════════════════════════════════════
#   FRONTEND ROUTES
# ════════════════════════════════════════════

@app.route("/")
def index():
    """Serve main dashboard page."""
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ════════════════════════════════════════════
#   API ROUTES — WEATHER DATA
# ════════════════════════════════════════════

@app.route("/api/weather", methods=["GET"])
def get_weather():
    """
    Fetch live weather + AQI + forecast for a city.
    Query params: lat, lon, city (optional label)
    """
    lat  = request.args.get("lat",  28.6139, type=float)
    lon  = request.args.get("lon",  77.2090, type=float)
    city = request.args.get("city", "Unknown")

    try:
        # 1. Current weather
        w_res = requests.get(
            f"{OWM_BASE_URL}/weather",
            params={"lat": lat, "lon": lon, "appid": OWM_API_KEY, "units": "metric"},
            timeout=10
        )
        if not w_res.ok:
            return jsonify({"error": f"Weather API error: {w_res.status_code}"}), 400
        w = w_res.json()

        # 2. Air quality
        aq_res = requests.get(
            f"{OWM_BASE_URL}/air_pollution",
            params={"lat": lat, "lon": lon, "appid": OWM_API_KEY},
            timeout=10
        )
        aq = aq_res.json() if aq_res.ok else {"list": [{"components": {}, "main": {"aqi": 1}}]}

        # 3. 5-day forecast (3h intervals)
        fc_res = requests.get(
            f"{OWM_BASE_URL}/forecast",
            params={"lat": lat, "lon": lon, "appid": OWM_API_KEY, "units": "metric", "cnt": 56},
            timeout=10
        )
        fc = fc_res.json() if fc_res.ok else {"list": []}

        # Parse AQI components
        components = aq["list"][0]["components"] if aq.get("list") else {}
        pm25       = components.get("pm2_5", 10)
        aqi_val    = _pm25_to_aqi(pm25)

        # Build weather dict
        weather = {
            "city":         w.get("name", city),
            "country":      w["sys"].get("country", ""),
            "lat":          lat, "lon": lon,
            "temp":         round(w["main"]["temp"]),
            "feels_like":   round(w["main"]["feels_like"]),
            "humidity":     w["main"]["humidity"],
            "pressure":     w["main"]["pressure"],
            "wind_speed":   round(w["wind"]["speed"] * 3.6),  # m/s → km/h
            "wind_deg":     w["wind"].get("deg", 0),
            "wind_dir":     _deg_to_dir(w["wind"].get("deg", 0)),
            "visibility":   round(w.get("visibility", 10000) / 1000, 1),
            "description":  w["weather"][0]["description"],
            "weather_id":   w["weather"][0]["id"],
            "dew_point":    round(w["main"]["temp"] - (100 - w["main"]["humidity"]) / 5),
            "aqi":          aqi_val,
            "pm25":         round(pm25, 1),
            "pm10":         round(components.get("pm10", 0), 1),
            "no2":          round(components.get("no2", 0), 1),
            "o3":           round(components.get("o3", 0), 1),
            "co":           round(components.get("co", 0), 1),
            "timestamp":    datetime.now().isoformat(),
        }

        # Parse forecast
        forecast = []
        for entry in fc.get("list", []):
            forecast.append({
                "dt":          entry["dt"],
                "temp":        round(entry["main"]["temp"]),
                "humidity":    entry["main"]["humidity"],
                "wind_speed":  round(entry["wind"]["speed"] * 3.6),
                "pressure":    entry["main"]["pressure"],
                "rain":        (entry.get("rain") or {}).get("3h", 0),
                "snow":        (entry.get("snow") or {}).get("3h", 0),
                "weather_id":  entry["weather"][0]["id"],
                "description": entry["weather"][0]["description"],
                "time":        datetime.fromtimestamp(entry["dt"]).strftime("%H:%M"),
                "date":        datetime.fromtimestamp(entry["dt"]).strftime("%b %d"),
                "dow":         datetime.fromtimestamp(entry["dt"]).strftime("%a"),
            })

        # Compute rain accumulation for disaster engine
        weather["rain_24h"] = sum(f["rain"] for f in forecast[:8])
        weather["rain_48h"] = sum(f["rain"] for f in forecast[:16])
        weather["rain_72h"] = sum(f["rain"] for f in forecast[:24])
        weather["pressure_drop"] = weather["pressure"] - min(
            (f["pressure"] for f in forecast[:16]), default=weather["pressure"]
        )

        # Terrain flags
        city_obj = next((c for c in CITIES if c["name"] == city), {})
        weather["is_hilly"]   = city_obj.get("hilly", False)
        weather["is_coastal"] = city_obj.get("coastal", False)

        # Run disaster engine
        disasters = generate_alerts(weather, city=weather["city"])

        # Update chatbot context
        bot.update_context(weather, forecast, weather["city"])

        return jsonify({
            "weather":   weather,
            "forecast":  forecast,
            "disasters": disasters,
            "summary":   alert_summary(disasters),
        })

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "No internet connection"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "API request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cities", methods=["GET"])
def get_cities():
    """Return list of all supported cities."""
    return jsonify({"cities": CITIES})


# ════════════════════════════════════════════
#   API ROUTES — DISASTER & ALERTS
# ════════════════════════════════════════════

@app.route("/api/alerts", methods=["POST"])
def get_alerts():
    """
    Get disaster alerts for given weather conditions.
    Body: weather dict JSON
    """
    weather = request.get_json()
    if not weather:
        return jsonify({"error": "No weather data provided"}), 400

    city     = weather.get("city", "Unknown")
    disasters = generate_alerts(weather, city=city)
    summary   = alert_summary(disasters)

    return jsonify({
        "city":      city,
        "disasters": disasters,
        "summary":   summary,
        "count":     len(disasters),
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Run ML disaster prediction on weather data.
    Body: weather dict JSON
    """
    weather = request.get_json()
    if not weather:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Try ML model first, fall back to rule-based
        try:
            result = predict_disaster(weather)
        except FileNotFoundError:
            # Model not trained yet — use rule-based
            disasters = rule_based_predict(weather)
            result = {
                "label":       disasters[0]["label"] if disasters else "Normal",
                "probability": disasters[0]["prob"]  if disasters else 5.0,
                "risk_level":  disasters[0]["level"] if disasters else "low",
                "method":      "rule-based (ML model not trained yet)",
            }

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════
#   API ROUTES — CHATBOT
# ════════════════════════════════════════════

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Send message to EnviroBot.
    Body: { "message": "..." }
    """
    body = request.get_json()
    if not body or "message" not in body:
        return jsonify({"error": "No message provided"}), 400

    user_msg = body["message"].strip()
    response = bot.chat(user_msg)

    return jsonify({
        "message":  user_msg,
        "response": response,
        "city":     bot.city,
        "time":     datetime.now().strftime("%H:%M"),
    })


@app.route("/api/chat/history", methods=["GET"])
def chat_history():
    """Return full chat history for current session."""
    return jsonify({"history": bot.history})


@app.route("/api/chat/clear", methods=["POST"])
def clear_chat():
    """Clear chat history."""
    bot.history = []
    return jsonify({"status": "cleared"})


# ════════════════════════════════════════════
#   API ROUTES — VISUALIZATIONS
# ════════════════════════════════════════════

@app.route("/api/chart/temperature", methods=["POST"])
def chart_temperature():
    """Generate and return temperature trend chart."""
    data = request.get_json()
    forecast = data.get("forecast", [])
    city     = data.get("city", "")
    path = plot_temperature_trend(forecast, city)
    return jsonify({"chart_path": f"/{path}"})


@app.route("/api/chart/aqi", methods=["POST"])
def chart_aqi():
    """Generate and return AQI gauge chart."""
    data = request.get_json()
    aqi  = data.get("aqi", 50)
    city = data.get("city", "")
    path = plot_aqi_gauge(aqi, city)
    return jsonify({"chart_path": f"/{path}"})


# ════════════════════════════════════════════
#   STATIC FILES
# ════════════════════════════════════════════

@app.route("/static/plots/<filename>")
def serve_plot(filename):
    return send_from_directory("static/plots", filename)


# ════════════════════════════════════════════
#   UTILITY FUNCTIONS
# ════════════════════════════════════════════

def _pm25_to_aqi(pm: float) -> int:
    """Convert PM2.5 concentration to US AQI."""
    if pm <= 12:    return int(50 / 12 * pm)
    if pm <= 35.4:  return int(50  + (pm - 12)   / (35.4 - 12)   * 50)
    if pm <= 55.4:  return int(100 + (pm - 35.4) / (55.4 - 35.4) * 50)
    if pm <= 150.4: return int(150 + (pm - 55.4) / (150.4 - 55.4)* 100)
    if pm <= 250.4: return int(200 + (pm - 150.4)/ 100            * 100)
    return min(500, int(300 + (pm - 250.4) * 0.8))


def _deg_to_dir(deg: float) -> str:
    """Convert wind degree to compass direction."""
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[round(deg / 22.5) % 16]


# ════════════════════════════════════════════
#   HEALTH CHECK
# ════════════════════════════════════════════

@app.route("/health")
def health():
    return jsonify({
        "status":    "running",
        "app":       "EnviroSense Pro",
        "version":   "3.0.0",
        "timestamp": datetime.now().isoformat(),
    })


# ════════════════════════════════════════════
#   RUN
# ════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("  🛰️  EnviroSense Pro — Flask Backend")
    print(f"  Running at http://{APP_HOST}:{APP_PORT}")
    print("=" * 50)
    app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG_MODE)
