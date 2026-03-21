# ============================================
# alerts.py — Disaster Alert & Notification System
# ============================================

from datetime import datetime
from config import THRESHOLDS
from model import rule_based_predict


# ── Alert Templates ──────────────────────────
ALERT_TEMPLATES = {
    "storm": {
        "icon":  "⛈️",
        "color": "#e53935",
        "suggestions": [
            "🏠 Stay indoors — avoid all travel",
            "🪟 Close windows, secure loose outdoor items",
            "⚡ Unplug sensitive electronics",
            "📱 Charge devices, save emergency contacts",
            "📻 Follow IMD / NDMA official bulletins",
        ],
    },
    "flood": {
        "icon":  "🌊",
        "color": "#0288d1",
        "suggestions": [
            "🚧 Avoid low-lying areas, underpasses, rivers",
            "🎒 Emergency kit: torch, water, meds, ID",
            "📞 Know nearest evacuation center location",
            "🚗 Do NOT drive through waterlogged roads",
            "📲 Register for NDMA flood SMS alerts",
        ],
    },
    "heatwave": {
        "icon":  "🔥",
        "color": "#f97316",
        "suggestions": [
            "💧 Drink 3–4 litres of water daily",
            "🕐 Avoid outdoors between 11 AM – 4 PM",
            "👕 Wear light, loose, cotton clothing",
            "❄️ Use wet towels / cool water on skin",
            "👴 Check on elderly neighbors and children",
            "🏥 Seek help for dizziness or rapid heartbeat",
        ],
    },
    "coldwave": {
        "icon":  "❄️",
        "color": "#0ea5e9",
        "suggestions": [
            "🧥 Wear thermal layers + windbreaker",
            "🔥 Use safe heating sources (NO coal indoors)",
            "🍵 Consume warm fluids frequently",
            "🐾 Bring pets indoors or provide shelter",
            "🏥 Watch for hypothermia: confusion, pale skin",
        ],
    },
    "pollution": {
        "icon":  "🌫️",
        "color": "#9e9e9e",
        "suggestions": [
            "😷 Wear N95 / FFP2 mask outdoors",
            "🏠 Keep windows closed, use HEPA air purifier",
            "🏃 Cancel / postpone outdoor exercise",
            "👶 Keep children and elderly strictly indoors",
            "🩺 See doctor if breathless or chest pain",
        ],
    },
    "landslide": {
        "icon":  "⛰️",
        "color": "#795548",
        "suggestions": [
            "🏔️ Avoid steep slopes and gorges",
            "👀 Watch for ground cracks or water seepage",
            "🚗 Avoid mountain roads during/after rain",
            "🏃 Evacuate immediately on hearing rumbling",
            "📻 Follow state disaster authority updates",
        ],
    },
    "cyclone": {
        "icon":  "🌀",
        "color": "#7c3aed",
        "suggestions": [
            "🌊 Evacuate coastal / low-lying areas now",
            "🏠 Move to strong RCC building inland",
            "📦 Stock 72-hour emergency supply kit",
            "🔌 Turn off mains electricity before evacuating",
            "📡 Follow IMD cyclone bulletins every 6 hours",
        ],
    },
}

# ── Severity Levels ──────────────────────────
SEVERITY_MAP = {
    "high":   {"label": "🔴 HIGH ALERT",   "emoji": "🚨", "priority": 3},
    "medium": {"label": "🟠 MEDIUM RISK",  "emoji": "⚠️", "priority": 2},
    "low":    {"label": "🟡 LOW RISK",     "emoji": "ℹ️", "priority": 1},
    "none":   {"label": "✅ NORMAL",       "emoji": "✅", "priority": 0},
}


# ── 1. Generate Alerts from Weather Data ─────
def generate_alerts(weather: dict, city: str = "") -> list:
    """
    Generate structured alert list from weather dict.
    Combines rule-based detection with alert templates.

    Args:
        weather: dict with temp, humidity, wind_speed, etc.
        city: city name string for alert messages

    Returns:
        List of alert dicts with full details
    """
    raw_disasters = rule_based_predict(weather)
    alerts = []

    for d in raw_disasters:
        dtype    = d["type"]
        template = ALERT_TEMPLATES.get(dtype, {})
        severity = SEVERITY_MAP.get(d["level"], SEVERITY_MAP["low"])

        alert = {
            "type":        dtype,
            "city":        city,
            "name":        d["label"],
            "icon":        template.get("icon", "⚠️"),
            "color":       template.get("color", "#666"),
            "level":       d["level"],
            "severity_label": severity["label"],
            "priority":    severity["priority"],
            "probability": round(d["prob"], 1),
            "suggestions": template.get("suggestions", []),
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "conditions":  _build_condition_string(weather, dtype),
            "window":      _estimate_window(dtype, d["prob"]),
        }
        alerts.append(alert)

    return alerts


# ── 2. Format Alert for Console ──────────────
def format_alert_text(alert: dict) -> str:
    """Return a nicely formatted text alert."""
    lines = [
        f"\n{'='*55}",
        f"  {alert['icon']}  {alert['severity_label']}",
        f"  {alert['name']} — {alert['city']}",
        f"{'='*55}",
        f"  Probability : {alert['probability']}%",
        f"  Window      : {alert['window']}",
        f"  Conditions  : {alert['conditions']}",
        f"  Time        : {alert['timestamp']}",
        f"\n  📋 What You Should Do:",
    ]
    for i, s in enumerate(alert["suggestions"], 1):
        lines.append(f"     {i}. {s}")
    lines.append("=" * 55)
    return "\n".join(lines)


# ── 3. Build Condition String ─────────────────
def _build_condition_string(weather: dict, dtype: str) -> str:
    """Build human-readable conditions string for alert."""
    parts = []
    if dtype == "storm":
        parts = [
            f"Wind: {weather.get('wind_speed', '?')} km/h",
            f"Humidity: {weather.get('humidity', '?')}%",
            f"Pressure drop: {weather.get('pressure_drop', 0):.0f} hPa",
        ]
    elif dtype == "flood":
        parts = [
            f"Rain 24h: {weather.get('rain_24h', 0):.1f}mm",
            f"Humidity: {weather.get('humidity', '?')}%",
        ]
    elif dtype == "heatwave":
        parts = [
            f"Temp: {weather.get('temp', '?')}°C",
            f"Feels like: {weather.get('feels_like', '?')}°C",
            f"Humidity: {weather.get('humidity', '?')}%",
        ]
    elif dtype == "coldwave":
        parts = [
            f"Temp: {weather.get('temp', '?')}°C",
            f"Wind chill: {weather.get('feels_like', '?')}°C",
        ]
    elif dtype == "pollution":
        parts = [
            f"AQI: {weather.get('aqi', '?')}",
            f"PM2.5: {weather.get('pm25', '?')} µg/m³",
        ]
    elif dtype == "landslide":
        parts = [
            f"Rain 24h: {weather.get('rain_24h', 0):.1f}mm",
            f"Rain 72h: {weather.get('rain_72h', 0):.1f}mm",
            f"Humidity: {weather.get('humidity', '?')}%",
        ]
    return " · ".join(parts) if parts else "Multiple parameters exceeded thresholds"


# ── 4. Estimate Alert Window ──────────────────
def _estimate_window(dtype: str, prob: float) -> str:
    windows = {
        "storm":     "Next 6–24 hours" if prob > 70 else "Next 12–36 hours",
        "flood":     "Next 24–72 hours",
        "heatwave":  "Current – 3 to 4 days",
        "coldwave":  "Next 24–48 hours",
        "pollution": "Current – may persist 2 to 4 days",
        "landslide": "During and after heavy rain",
        "cyclone":   "Next 24–48 hours",
    }
    return windows.get(dtype, "Next 24 hours")


# ── 5. Alert Summary ──────────────────────────
def alert_summary(alerts: list) -> dict:
    """
    Return high-level summary of all active alerts.
    """
    if not alerts:
        return {
            "count":        0,
            "highest_risk": "none",
            "status":       "✅ No Active Alerts — Conditions Normal",
        }

    highest = max(alerts, key=lambda a: a["priority"])
    return {
        "count":         len(alerts),
        "highest_risk":  highest["level"],
        "highest_alert": highest["name"],
        "highest_prob":  highest["probability"],
        "status":        f"{highest['icon']} {highest['severity_label']} — {highest['name']}",
        "active_types":  [a["type"] for a in alerts],
    }


# ── 6. Check Specific Threshold ───────────────
def check_threshold(weather: dict, alert_type: str) -> dict:
    """
    Check if a specific alert threshold is crossed.
    Returns { triggered: bool, value: float, threshold: float }
    """
    T = THRESHOLDS.get(alert_type, {})
    checks = {
        "storm":     ("wind_speed",  weather.get("wind_speed", 0),     T.get("wind_speed_kmh", 40)),
        "flood":     ("rain_24h",    weather.get("rain_24h", 0),        T.get("rain_24h_mm", 20)),
        "heatwave":  ("temperature", weather.get("temp", 25),           T.get("temp_celsius", 38)),
        "coldwave":  ("temperature", weather.get("temp", 25),           T.get("temp_celsius", 8)),
        "pollution": ("aqi",         weather.get("aqi", 50),            T.get("aqi_value", 150)),
        "landslide": ("rain_24h",    weather.get("rain_24h", 0),        T.get("rain_24h_mm", 20)),
    }
    if alert_type not in checks:
        return {"triggered": False}

    param, value, threshold = checks[alert_type]
    # Cold wave triggers BELOW threshold, others ABOVE
    triggered = value <= threshold if alert_type == "coldwave" else value >= threshold

    return {
        "triggered": triggered,
        "param":     param,
        "value":     value,
        "threshold": threshold,
    }


# ── 7. Print All Alerts ───────────────────────
def print_all_alerts(alerts: list, city: str = ""):
    """Print all alerts to console with formatting."""
    if not alerts:
        print(f"\n✅ No active alerts for {city}. Conditions are normal.")
        return

    print(f"\n🚨 {len(alerts)} Active Alert(s) for {city}:")
    for alert in alerts:
        print(format_alert_text(alert))


# ── Run standalone ────────────────────────────
if __name__ == "__main__":
    # Demo: simulate Srinagar winter conditions
    sample_weather = {
        "city":          "Srinagar",
        "temp":          3,
        "feels_like":    -2,
        "humidity":      88,
        "pressure":      1005,
        "pressure_drop": 7,
        "wind_speed":    35,
        "rain_24h":      18,
        "rain_48h":      35,
        "rain_72h":      55,
        "aqi":           85,
        "pm25":          30,
        "is_hilly":      True,
        "is_coastal":    False,
    }

    print("🛰️  EnviroSense Pro — Alert System Demo")
    print(f"📍 Location: {sample_weather['city']}")
    print(f"🌡️  Conditions: {sample_weather['temp']}°C, Wind: {sample_weather['wind_speed']} km/h, AQI: {sample_weather['aqi']}")

    alerts = generate_alerts(sample_weather, city=sample_weather["city"])
    print_all_alerts(alerts, city=sample_weather["city"])

    summary = alert_summary(alerts)
    print(f"\n📊 Summary: {summary['status']}")
    print(f"   Total alerts: {summary['count']}")
