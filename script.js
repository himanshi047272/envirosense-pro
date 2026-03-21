// ============================================
// script.js — EnviroSense Pro Frontend Logic
// Handles API calls from Flask backend
// ============================================

const API_BASE = window.location.origin; // http://localhost:5000

// ── Fetch weather for a city ──────────────
async function fetchWeather(lat, lon, cityName) {
  showLoader(`Loading data for ${cityName}…`);
  try {
    const res  = await fetch(`${API_BASE}/api/weather?lat=${lat}&lon=${lon}&city=${encodeURIComponent(cityName)}`);
    const data = await res.json();

    if (data.error) { showError(data.error); return null; }

    updateDashboard(data.weather, data.forecast, data.disasters, data.summary);
    hideLoader();
    return data;
  } catch (err) {
    showError("Could not connect to server. Is Flask running?");
    hideLoader();
    return null;
  }
}

// ── Send chat message ─────────────────────
async function sendChatMessage(message) {
  const res  = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  const data = await res.json();
  return data.response || "I couldn't process that.";
}

// ── Update dashboard UI ───────────────────
function updateDashboard(weather, forecast, disasters, summary) {
  // Stat cards
  setEl("sc-temp",  weather.temp + "°C");
  setEl("sc-humid", weather.humidity + "%");
  setEl("sc-aqi",   weather.aqi);
  setEl("sc-wind",  weather.wind_speed + " km/h");

  // Weather hero
  setEl("wh-city",   weather.city + ", " + weather.country);
  setEl("wh-temp",   weather.temp + "°");
  setEl("wh-cond",   capitalize(weather.description));
  setEl("wh-feels",  `Feels like ${weather.feels_like}°C · Visibility ${weather.visibility} km`);

  // Status bar
  const level = summary?.highest_risk || "none";
  setEl("env-status", summary?.status || "Normal");
  setEl("risk-level", level.toUpperCase());

  // Update page title
  document.title = `${weather.city} — EnviroSense Pro`;

  // Update charts if available
  if (typeof buildTempChart === "function") buildTempChart(forecast, weather.city);
  if (typeof buildAQIGauge   === "function") buildAQIGauge(weather.aqi);
  if (typeof buildHourlyStrip === "function") buildHourlyStrip(forecast.slice(0, 9));
  if (typeof render7DayForecast === "function") render7DayForecast(forecast, weather.city);
  if (typeof renderAlerts === "function") renderAlerts(disasters, weather.city);
}

// ── Utility: set element HTML ─────────────
function setEl(id, value) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = value;
}

// ── Utility: capitalize ───────────────────
function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
}

// ── Loader ────────────────────────────────
function showLoader(msg) {
  const el = document.getElementById("loader");
  if (el) { el.classList.add("show"); }
  const txt = document.getElementById("loader-msg");
  if (txt) txt.textContent = msg || "Loading…";
}
function hideLoader() {
  const el = document.getElementById("loader");
  if (el) el.classList.remove("show");
}

// ── Error display ─────────────────────────
function showError(msg) {
  hideLoader();
  console.error("[EnviroSense]", msg);
  // Show toast if available
  if (typeof toast === "function") toast("❌", "Error", msg, "r");
}

// ── AQI Helpers ───────────────────────────
function aqiLabel(v) {
  if (v > 300) return "Hazardous";
  if (v > 200) return "Very Unhealthy";
  if (v > 150) return "Unhealthy";
  if (v > 100) return "Sensitive Groups";
  if (v > 50)  return "Moderate";
  return "Good";
}

function aqiColor(v) {
  if (v > 300) return "#7c3aed";
  if (v > 200) return "#e53935";
  if (v > 150) return "#f97316";
  if (v > 100) return "#eab308";
  if (v > 50)  return "#84cc16";
  return "#1baa5e";
}

function weatherEmoji(wid) {
  if (!wid) return "⛅";
  if (wid >= 200 && wid < 300) return "⛈️";
  if (wid >= 300 && wid < 400) return "🌦️";
  if (wid >= 500 && wid < 600) return wid >= 502 ? "🌧️" : "🌦️";
  if (wid >= 600 && wid < 700) return "❄️";
  if (wid >= 700 && wid < 800) return "🌫️";
  if (wid === 800) return "☀️";
  if (wid === 801) return "🌤️";
  return "⛅";
}
