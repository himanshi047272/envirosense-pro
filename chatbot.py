# ============================================
# chatbot.py — EnviroBot AI Assistant
# ============================================

import re
from datetime import datetime
from alerts import generate_alerts, alert_summary


# ── Intent Definitions ───────────────────────
INTENTS = {
    "safe_outside":   [r"safe.*outside", r"go.*outside", r"outside.*safe",
                       r"can.*go out", r"is it safe", r"walk.*today"],

    "temperature":    [r"temp", r"how hot", r"how cold", r"celsius",
                       r"degree", r"weather.*like", r"feels like"],

    "aqi":            [r"\baqi\b", r"air quality", r"pollution", r"pm2\.?5",
                       r"pm10", r"\bpm\b", r"smog", r"breathe", r"air.*safe"],

    "storm":          [r"storm", r"cyclone", r"wind", r"thunder", r"lightning",
                       r"gale", r"hurricane", r"typhoon"],

    "flood":          [r"flood", r"rain.*heavy", r"heavy.*rain", r"waterlog",
                       r"inundation", r"overflow"],

    "heatwave":       [r"heat.*wave", r"heatwave", r"too hot", r"extreme heat",
                       r"heat.*stroke", r"sunstroke"],

    "coldwave":       [r"cold.*wave", r"coldwave", r"freeze", r"frost",
                       r"too cold", r"extreme cold", r"hypothermia"],

    "landslide":      [r"landslide", r"mudslide", r"slope.*risk",
                       r"hill.*safe", r"mountain.*risk"],

    "disaster":       [r"disaster", r"risk", r"alert", r"danger", r"emergency",
                       r"what.*happening", r"any.*warning"],

    "forecast":       [r"forecast", r"tomorrow", r"next.*day", r"this week",
                       r"coming.*days", r"7.*day", r"week"],

    "humidity":       [r"humid", r"moisture", r"dew", r"sticky"],

    "pressure":       [r"pressure", r"barometric", r"hpa", r"low.*pressure"],

    "help":           [r"\bhelp\b", r"what.*ask", r"what.*can.*do",
                       r"commands", r"options"],

    "greeting":       [r"^hi\b", r"^hello\b", r"^hey\b", r"^namaste",
                       r"^good\s*(morning|afternoon|evening|night)"],

    "change_city":    [r"change.*city", r"switch.*to", r"check.*city",
                       r"data.*for\s+\w+", r"weather.*in\s+\w+"],
}


class EnviroBot:
    """
    Rule-based chatbot with live weather context.
    Maintains conversation history and current city state.
    """

    def __init__(self):
        self.weather_data  = {}
        self.forecast_data = []
        self.disasters     = []
        self.city          = "Unknown"
        self.history       = []  # list of {"role": "user"/"bot", "text": "..."}

    def update_context(self, weather: dict, forecast: list, city: str):
        """Update bot with latest weather data."""
        self.weather_data  = weather
        self.forecast_data = forecast
        self.city          = city
        self.disasters     = generate_alerts(weather, city)

    def chat(self, user_msg: str) -> str:
        """
        Process user message and return bot response.
        """
        user_msg = user_msg.strip()
        if not user_msg:
            return "Please type a question! Try: 'Is it safe outside?' or 'What's the AQI?'"

        self.history.append({"role": "user", "text": user_msg, "time": datetime.now().strftime("%H:%M")})

        intent  = self._classify_intent(user_msg.lower())
        response = self._generate_response(intent, user_msg)

        self.history.append({"role": "bot", "text": response, "time": datetime.now().strftime("%H:%M")})
        return response

    def _classify_intent(self, text: str) -> str:
        """Match user text to one of the defined intents."""
        for intent, patterns in INTENTS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return intent
        return "unknown"

    def _generate_response(self, intent: str, raw_msg: str) -> str:
        """Generate response based on intent and current weather data."""
        w    = self.weather_data
        city = self.city

        # No weather data loaded yet
        if not w:
            return (
                f"I don't have weather data loaded yet. "
                f"Please search for a city first, then I can answer your questions! 🌍"
            )

        temp  = w.get("temp", 25)
        feels = w.get("feels_like", 25)
        hum   = w.get("humidity", 60)
        wind  = w.get("wind_speed", 10)
        aqi   = w.get("aqi", 50)
        pm25  = w.get("pm25", 10)

        # ── GREETING ──────────────────────────
        if intent == "greeting":
            hour = datetime.now().hour
            time_of_day = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
            return (
                f"Good {time_of_day}! 👋 I'm EnviroBot, your real-time environmental assistant. "
                f"I have live data for **{city}** right now.\n\n"
                f"Current: 🌡️ {temp}°C · 😷 AQI {aqi} · 💨 {wind} km/h\n\n"
                f"Ask me: 'Is it safe to go outside?' or 'What's the storm risk?'"
            )

        # ── SAFE OUTSIDE ──────────────────────
        elif intent == "safe_outside":
            issues = []
            if aqi > 150:    issues.append(f"AQI {aqi} is Unhealthy — wear N95 mask")
            if temp > 38:    issues.append(f"Heatwave conditions ({temp}°C)")
            if temp < 8:     issues.append(f"Cold wave conditions ({temp}°C)")
            if wind > 40:    issues.append(f"Strong winds ({wind} km/h)")
            if hum > 90:     issues.append(f"Extreme humidity ({hum}%)")

            if not issues:
                return (
                    f"✅ Yes, **{city}** conditions are safe right now!\n\n"
                    f"🌡️ Temp: {temp}°C (feels {feels}°C)\n"
                    f"😷 AQI: {aqi} — {_aqi_label(aqi)}\n"
                    f"💨 Wind: {wind} km/h\n\n"
                    f"💡 Best time to go outside: early morning (6–9 AM)"
                )
            else:
                return (
                    f"⚠️ Caution advised in **{city}** right now:\n\n"
                    + "\n".join(f"  • {i}" for i in issues)
                    + f"\n\n💡 Recommendation: Limit outdoor exposure today."
                )

        # ── TEMPERATURE ───────────────────────
        elif intent == "temperature":
            status = "🔥 Heatwave conditions!" if temp > 38 else "❄️ Cold wave conditions!" if temp < 8 else "🌡️ Normal range."
            return (
                f"🌡️ **{city}** Temperature:\n\n"
                f"  Current:   {temp}°C\n"
                f"  Feels like: {feels}°C\n"
                f"  Humidity:  {hum}%\n"
                f"  Status:    {status}"
            )

        # ── AQI ───────────────────────────────
        elif intent == "aqi":
            label  = _aqi_label(aqi)
            advice = _aqi_advice(aqi)
            return (
                f"😷 **{city}** Air Quality:\n\n"
                f"  AQI: {aqi} — {label}\n"
                f"  PM2.5: {pm25:.1f} µg/m³\n\n"
                f"  💡 {advice}"
            )

        # ── STORM ─────────────────────────────
        elif intent == "storm":
            e = next((d for d in self.disasters if d["type"] == "storm"), None)
            if e:
                return (
                    f"⛈️ **Storm Alert — {city}**\n\n"
                    f"  Risk Level: {e['level'].upper()}\n"
                    f"  Probability: {e['probability']}%\n"
                    f"  Window: {e['window']}\n"
                    f"  Conditions: {e['conditions']}\n\n"
                    f"  ⚡ Action: {e['suggestions'][0]}"
                )
            return (
                f"✅ No storm risk in **{city}** right now.\n"
                f"  Wind: {wind} km/h · Pressure: {w.get('pressure','?')} hPa\n"
                f"  Conditions are within normal range."
            )

        # ── FLOOD ─────────────────────────────
        elif intent == "flood":
            e = next((d for d in self.disasters if d["type"] == "flood"), None)
            if e:
                return (
                    f"🌊 **Flood Risk — {city}**\n\n"
                    f"  Risk Level: {e['level'].upper()}\n"
                    f"  Probability: {e['probability']}%\n"
                    f"  Window: {e['window']}\n"
                    f"  Conditions: {e['conditions']}\n\n"
                    f"  🚧 Action: {e['suggestions'][0]}"
                )
            return (
                f"✅ No flood risk in **{city}** currently.\n"
                f"  Humidity: {hum}% · Rain accumulation is within normal limits."
            )

        # ── HEATWAVE ──────────────────────────
        elif intent == "heatwave":
            e = next((d for d in self.disasters if d["type"] == "heatwave"), None)
            if e:
                return (
                    f"🔥 **Heatwave Alert — {city}**\n\n"
                    f"  Temp: {temp}°C (feels {feels}°C)\n"
                    f"  Risk: {e['level'].upper()} · {e['probability']}% probability\n"
                    f"  Window: {e['window']}\n\n"
                    f"  💧 Action: {e['suggestions'][0]}\n"
                    f"  🕐 Avoid outdoors 11 AM – 4 PM"
                )
            return (
                f"✅ No heatwave in **{city}** right now.\n"
                f"  Temperature: {temp}°C (feels {feels}°C) — within normal range."
            )

        # ── COLD WAVE ─────────────────────────
        elif intent == "coldwave":
            e = next((d for d in self.disasters if d["type"] == "coldwave"), None)
            if e:
                return (
                    f"❄️ **Cold Wave Alert — {city}**\n\n"
                    f"  Temp: {temp}°C (feels {feels}°C)\n"
                    f"  Risk: {e['level'].upper()} · {e['probability']}% probability\n"
                    f"  Window: {e['window']}\n\n"
                    f"  🧥 Action: {e['suggestions'][0]}"
                )
            return (
                f"✅ No cold wave in **{city}** right now.\n"
                f"  Temperature: {temp}°C — within normal range."
            )

        # ── LANDSLIDE ─────────────────────────
        elif intent == "landslide":
            e = next((d for d in self.disasters if d["type"] == "landslide"), None)
            if e:
                return (
                    f"⛰️ **Landslide Risk — {city}**\n\n"
                    f"  Risk: {e['level'].upper()} · {e['probability']}% probability\n"
                    f"  Conditions: {e['conditions']}\n\n"
                    f"  ⚠️ Action: {e['suggestions'][0]}"
                )
            return (
                f"✅ Low landslide risk in **{city}** currently.\n"
                f"  Monitor if heavy rain is forecast in hilly areas."
            )

        # ── ALL DISASTERS ──────────────────────
        elif intent == "disaster":
            summary = alert_summary(self.disasters)
            if not self.disasters:
                return (
                    f"✅ **No active disaster risks in {city}!**\n\n"
                    f"  All parameters are within safe ranges:\n"
                    f"  🌡️ {temp}°C · 💧 {hum}% · 💨 {wind} km/h · 😷 AQI {aqi}\n\n"
                    f"  System is monitoring continuously."
                )
            lines = [f"🚨 **{len(self.disasters)} Active Risk(s) in {city}:**\n"]
            for d in self.disasters:
                lines.append(f"  {d['icon']} {d['name']} — {d['level'].upper()} ({d['probability']}%)")
            lines.append(f"\nℹ️ Ask about any specific risk for detailed advice.")
            return "\n".join(lines)

        # ── FORECAST ──────────────────────────
        elif intent == "forecast":
            if not self.forecast_data:
                return f"No forecast data loaded for {city} yet. Refresh the page to load."
            lines = [f"📅 **7-Day Forecast — {city}:**\n"]
            from preprocessing import engineer_features
            from model import rule_based_predict
            for i, day in enumerate(self.forecast_data[:7]):
                day_disasters = rule_based_predict({
                    "temp": day.get("temp", temp),
                    "humidity": day.get("humidity", hum),
                    "wind_speed": day.get("wind_speed", wind),
                    "rain_24h": day.get("rain_24h", 0),
                    "aqi": aqi,
                })
                risk = day_disasters[0]["label"] if day_disasters else "Normal"
                dow  = day.get("dow", f"Day {i+1}")
                date = day.get("date", "")
                lines.append(f"  {dow} {date}: {day.get('temp',temp)}°C — {risk}")
            return "\n".join(lines)

        # ── HUMIDITY ──────────────────────────
        elif intent == "humidity":
            status = "Very High — flood and discomfort risk" if hum > 85 else "High" if hum > 70 else "Normal"
            return (
                f"💧 **Humidity in {city}:**\n\n"
                f"  Current: {hum}%\n"
                f"  Status: {status}\n"
                f"  Dew Point: {w.get('dew', '?')}°C"
            )

        # ── HELP ──────────────────────────────
        elif intent == "help":
            return (
                f"🤖 **EnviroBot — What I Can Answer:**\n\n"
                f"  🌡️ Temperature, feels like, heat stress\n"
                f"  😷 AQI, PM2.5, air quality, pollution\n"
                f"  ⛈️ Storm and cyclone risk\n"
                f"  🌊 Flood risk and rainfall\n"
                f"  🔥 Heatwave warnings\n"
                f"  ❄️ Cold wave alerts\n"
                f"  ⛰️ Landslide risk\n"
                f"  🚨 All active disasters\n"
                f"  📅 7-day forecast\n"
                f"  ✅ Is it safe to go outside?\n\n"
                f"Just ask naturally — I'll understand!"
            )

        # ── UNKNOWN ───────────────────────────
        else:
            return (
                f"I'm not sure about that. Here's the current status for **{city}**:\n\n"
                f"  🌡️ {temp}°C (feels {feels}°C)\n"
                f"  😷 AQI: {aqi} — {_aqi_label(aqi)}\n"
                f"  💨 Wind: {wind} km/h\n"
                f"  🚨 Active alerts: {len(self.disasters)}\n\n"
                f"Try asking: 'Is it safe outside?' or 'What disasters are active?'"
            )


# ── AQI Helpers ──────────────────────────────
def _aqi_label(v: int) -> str:
    if v > 300: return "Hazardous"
    if v > 200: return "Very Unhealthy"
    if v > 150: return "Unhealthy"
    if v > 100: return "Sensitive Groups"
    if v > 50:  return "Moderate"
    return "Good"

def _aqi_advice(v: int) -> str:
    if v > 300: return "Stay indoors. Air is hazardous. Emergency level."
    if v > 200: return "Wear N95 mask. Avoid all outdoor activity."
    if v > 150: return "Sensitive groups stay indoors. Wear mask outdoors."
    if v > 100: return "Sensitive groups limit outdoor exposure."
    if v > 50:  return "Acceptable. Sensitive people take some precautions."
    return "Air quality is good. Safe for outdoor activities!"


# ── Run standalone demo ───────────────────────
if __name__ == "__main__":
    bot = EnviroBot()

    # Simulate Srinagar winter data
    bot.update_context(
        weather={
            "temp": 2, "feels_like": -3, "humidity": 88,
            "pressure": 1005, "pressure_drop": 7,
            "wind_speed": 38, "rain_24h": 22, "rain_48h": 45,
            "rain_72h": 60, "aqi": 82, "pm25": 28,
            "is_hilly": True, "is_coastal": False,
        },
        forecast=[],
        city="Srinagar"
    )

    print("🤖 EnviroBot Demo — Srinagar")
    print("=" * 45)

    test_questions = [
        "Hello!",
        "Is it safe to go outside today?",
        "What's the storm risk?",
        "Tell me about all disasters",
        "How's the temperature?",
        "What should I know about AQI?",
        "Landslide risk?",
        "Help",
    ]

    for q in test_questions:
        print(f"\n👤 You: {q}")
        print(f"🤖 Bot: {bot.chat(q)}")
        print("-" * 40)
