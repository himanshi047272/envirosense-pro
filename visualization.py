# ============================================
# visualization.py — Charts & Graphs
# ============================================

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os
from datetime import datetime


PLOT_DIR = "static/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# Color palette
COLORS = {
    "green":  "#1baa5e",
    "blue":   "#0ea5e9",
    "orange": "#f97316",
    "red":    "#e53935",
    "purple": "#7c3aed",
    "gray":   "#9e9e9e",
    "bg":     "#f8fafd",
    "dark":   "#0d1b2a",
}


def _save(fig, filename: str) -> str:
    """Save figure and return path."""
    path = os.path.join(PLOT_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close(fig)
    print(f"[INFO] Saved: {path}")
    return path


def _style_ax(ax, title: str = "", xlabel: str = "", ylabel: str = ""):
    """Apply consistent styling to an axis."""
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#e2e8f0")
    ax.spines["bottom"].set_color("#e2e8f0")
    ax.tick_params(colors="#64748b", labelsize=9)
    ax.yaxis.grid(True, color="#e2e8f0", linewidth=0.7, linestyle="--")
    ax.set_axisbelow(True)
    if title:   ax.set_title(title, fontsize=12, fontweight="bold", color=COLORS["dark"], pad=10)
    if xlabel:  ax.set_xlabel(xlabel, fontsize=9, color="#64748b")
    if ylabel:  ax.set_ylabel(ylabel, fontsize=9, color="#64748b")


# ── 1. Temperature Trend ─────────────────────
def plot_temperature_trend(forecast_data: list, city: str = "") -> str:
    """Line chart of temperature forecast (48h)."""
    times = [f["time"] for f in forecast_data]
    temps = [f["temp"] for f in forecast_data]

    fig, ax = plt.subplots(figsize=(10, 4), facecolor=COLORS["bg"])
    ax.fill_between(range(len(temps)), temps, alpha=0.15, color=COLORS["green"])
    ax.plot(range(len(temps)), temps, color=COLORS["green"], linewidth=2.5, marker="o", markersize=4)
    ax.set_xticks(range(len(times)))
    ax.set_xticklabels(times, rotation=45, ha="right", fontsize=8)
    _style_ax(ax, f"48h Temperature Forecast — {city}", "Time", "Temperature (°C)")
    plt.tight_layout()
    return _save(fig, f"temp_trend_{city.replace(' ','_')}.png")


# ── 2. AQI Gauge Chart ───────────────────────
def plot_aqi_gauge(aqi_value: int, city: str = "") -> str:
    """Semi-circular AQI gauge chart."""
    fig, ax = plt.subplots(figsize=(6, 4), subplot_kw={"aspect": "equal"}, facecolor=COLORS["bg"])

    # AQI color bands
    bands = [
        (0,   50,  "#1baa5e", "Good"),
        (50,  100, "#84cc16", "Moderate"),
        (100, 150, "#eab308", "Sensitive"),
        (150, 200, "#f97316", "Unhealthy"),
        (200, 300, "#e53935", "Very Unhealthy"),
        (300, 500, "#7c3aed", "Hazardous"),
    ]

    for lo, hi, color, label in bands:
        theta1 = 180 - (lo / 500) * 180
        theta2 = 180 - (hi / 500) * 180
        wedge = mpatches.Wedge((0.5, 0.2), 0.38, theta2, theta1, width=0.12, color=color, alpha=0.9)
        ax.add_patch(wedge)

    # Needle
    angle = 180 - (min(aqi_value, 500) / 500) * 180
    rad   = np.radians(angle)
    ax.annotate("", xy=(0.5 + 0.3 * np.cos(rad), 0.2 + 0.3 * np.sin(rad)),
                xytext=(0.5, 0.2),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["dark"], lw=2))

    # Center circle
    center = plt.Circle((0.5, 0.2), 0.04, color=COLORS["dark"])
    ax.add_patch(center)

    ax.text(0.5, 0.52, str(aqi_value), ha="center", va="center",
            fontsize=28, fontweight="bold", color=COLORS["dark"])
    ax.text(0.5, 0.42, _aqi_label(aqi_value), ha="center", fontsize=10,
            color=_aqi_color(aqi_value), fontweight="bold")
    ax.text(0.5, 0.35, f"AQI — {city}", ha="center", fontsize=9, color="#64748b")

    ax.set_xlim(0, 1); ax.set_ylim(0, 0.7)
    ax.axis("off")
    plt.tight_layout()
    return _save(fig, f"aqi_gauge_{city.replace(' ','_')}.png")


# ── 3. 7-Day Risk Bar Chart ───────────────────
def plot_7day_risk(forecast_days: list, city: str = "") -> str:
    """Horizontal bar chart of 7-day disaster risk."""
    days    = [d.get("dow", f"Day {i+1}") for i, d in enumerate(forecast_days)]
    probs   = [d.get("risk_prob", 0) for d in forecast_days]
    levels  = [d.get("level", "none") for d in forecast_days]
    colors  = [{"high": COLORS["red"], "medium": COLORS["orange"], "low": "#eab308"}.get(l, COLORS["green"]) for l in levels]

    fig, ax = plt.subplots(figsize=(8, 5), facecolor=COLORS["bg"])
    bars = ax.barh(days, probs, color=colors, height=0.55, edgecolor="white", linewidth=0.5)

    for bar, prob, level in zip(bars, probs, levels):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"{prob:.0f}%  {level.upper()}", va="center", fontsize=9,
                color=COLORS["dark"], fontweight="bold")

    ax.set_xlim(0, 110)
    _style_ax(ax, f"7-Day Disaster Risk Forecast — {city}", "Risk Probability (%)", "")
    plt.tight_layout()
    return _save(fig, f"7day_risk_{city.replace(' ','_')}.png")


# ── 4. Humidity + Temperature Combo ──────────
def plot_humidity_temp(forecast: list, city: str = "") -> str:
    """Dual-axis line chart: temperature vs humidity."""
    times   = [f.get("time", "") for f in forecast]
    temps   = [f.get("temp", 0) for f in forecast]
    humids  = [f.get("humidity", 0) for f in forecast]

    fig, ax1 = plt.subplots(figsize=(10, 4), facecolor=COLORS["bg"])
    ax2 = ax1.twinx()

    ax1.plot(range(len(temps)), temps, color=COLORS["red"], linewidth=2, label="Temperature °C", marker="o", markersize=3)
    ax2.plot(range(len(humids)), humids, color=COLORS["blue"], linewidth=2, label="Humidity %", marker="s", markersize=3, linestyle="--")

    ax1.set_ylabel("Temperature (°C)", color=COLORS["red"], fontsize=9)
    ax2.set_ylabel("Humidity (%)", color=COLORS["blue"], fontsize=9)
    ax1.tick_params(axis="y", labelcolor=COLORS["red"])
    ax2.tick_params(axis="y", labelcolor=COLORS["blue"])
    ax1.set_xticks(range(len(times)))
    ax1.set_xticklabels(times, rotation=45, ha="right", fontsize=8)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=9)

    _style_ax(ax1, f"Temperature vs Humidity — {city}", "Time", "")
    plt.tight_layout()
    return _save(fig, f"hum_temp_{city.replace(' ','_')}.png")


# ── 5. AQI Pie Chart ─────────────────────────
def plot_aqi_composition(components: dict, city: str = "") -> str:
    """Pie/donut chart of AQI pollutant composition."""
    labels = list(components.keys())
    values = list(components.values())
    colors = [COLORS["red"], COLORS["orange"], "#eab308", COLORS["green"], COLORS["blue"]]

    fig, ax = plt.subplots(figsize=(6, 5), facecolor=COLORS["bg"])
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        colors=colors[:len(labels)],
        wedgeprops={"width": 0.55, "edgecolor": "white"},
        startangle=90,
    )
    for t in texts:       t.set_fontsize(9)
    for at in autotexts:  at.set_fontsize(8); at.set_color("white"); at.set_fontweight("bold")

    ax.set_title(f"AQI Composition — {city}", fontsize=12, fontweight="bold", color=COLORS["dark"])
    plt.tight_layout()
    return _save(fig, f"aqi_pie_{city.replace(' ','_')}.png")


# ── 6. Wind Speed Chart ───────────────────────
def plot_wind_speed(forecast: list, city: str = "") -> str:
    """Bar chart of wind speed forecast."""
    times  = [f.get("time", "") for f in forecast]
    winds  = [f.get("wind_speed", 0) for f in forecast]
    colors = [COLORS["red"] if w > 40 else COLORS["orange"] if w > 25 else COLORS["green"] for w in winds]

    fig, ax = plt.subplots(figsize=(10, 4), facecolor=COLORS["bg"])
    bars = ax.bar(range(len(winds)), winds, color=colors, edgecolor="white", linewidth=0.5, width=0.65)
    ax.axhline(y=40, color=COLORS["red"], linestyle="--", linewidth=1, alpha=0.7, label="Storm Threshold (40 km/h)")
    ax.axhline(y=25, color=COLORS["orange"], linestyle="--", linewidth=1, alpha=0.7, label="Brisk Wind (25 km/h)")
    ax.set_xticks(range(len(times)))
    ax.set_xticklabels(times, rotation=45, ha="right", fontsize=8)
    ax.legend(fontsize=8)
    _style_ax(ax, f"Wind Speed Forecast — {city}", "Time", "Wind Speed (km/h)")
    plt.tight_layout()
    return _save(fig, f"wind_{city.replace(' ','_')}.png")


# ── 7. ML Model Comparison ───────────────────
def plot_model_comparison(results_df: pd.DataFrame) -> str:
    """Grouped bar chart comparing ML model accuracies."""
    models   = results_df["Model"].tolist()
    accuracy = results_df["Accuracy"].tolist()
    f1_score = results_df["F1 Score"].tolist()

    x     = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=COLORS["bg"])
    bars1 = ax.bar(x - width/2, accuracy, width, label="Accuracy %",  color=COLORS["green"], alpha=0.85, edgecolor="white")
    bars2 = ax.bar(x + width/2, f1_score, width, label="F1 Score %",  color=COLORS["blue"],  alpha=0.85, edgecolor="white")

    for bar in bars1 + bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{bar.get_height():.1f}", ha="center", fontsize=8, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=9)
    ax.set_ylim(0, 105)
    ax.legend(fontsize=9)
    _style_ax(ax, "ML Model Comparison — Accuracy vs F1 Score", "Model", "Score (%)")
    plt.tight_layout()
    return _save(fig, "model_comparison.png")


# ── 8. Feature Importance Chart ──────────────
def plot_feature_importance(fi_df: pd.DataFrame, top_n: int = 12) -> str:
    """Horizontal bar chart of top feature importances."""
    fi_top = fi_df.head(top_n).sort_values("Importance")

    fig, ax = plt.subplots(figsize=(8, 6), facecolor=COLORS["bg"])
    bars = ax.barh(fi_top["Feature"], fi_top["Importance"],
                   color=COLORS["blue"], alpha=0.8, edgecolor="white")

    for bar in bars:
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                f"{bar.get_width():.3f}", va="center", fontsize=8)

    _style_ax(ax, "Top Feature Importances — Random Forest", "Importance", "")
    plt.tight_layout()
    return _save(fig, "feature_importance.png")


# ── 9. Historical AQI Trend ──────────────────
def plot_historical_aqi(dates: list, aqi_values: list, city: str = "") -> str:
    """Line chart of historical AQI trend with color bands."""
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=COLORS["bg"])

    # Color bands
    ax.axhspan(0,   50,  alpha=0.1, color="#1baa5e")
    ax.axhspan(50,  100, alpha=0.1, color="#84cc16")
    ax.axhspan(100, 150, alpha=0.1, color="#eab308")
    ax.axhspan(150, 200, alpha=0.1, color="#f97316")
    ax.axhspan(200, 300, alpha=0.1, color="#e53935")

    ax.plot(range(len(aqi_values)), aqi_values, color=COLORS["orange"], linewidth=2,
            marker="o", markersize=3)
    ax.fill_between(range(len(aqi_values)), aqi_values, alpha=0.15, color=COLORS["orange"])

    # Add threshold lines
    for y, label, color in [(50, "Good/Mod", "#84cc16"), (150, "Unhealthy", "#f97316"), (200, "Very Unhealthy", "#e53935")]:
        ax.axhline(y=y, color=color, linestyle="--", linewidth=0.8, alpha=0.8)
        ax.text(len(aqi_values)-1, y+3, label, fontsize=7, color=color)

    step = max(1, len(dates)//10)
    ax.set_xticks(range(0, len(dates), step))
    ax.set_xticklabels(dates[::step], rotation=45, ha="right", fontsize=8)
    _style_ax(ax, f"Historical AQI Trend — {city}", "Date", "AQI")
    plt.tight_layout()
    return _save(fig, f"aqi_history_{city.replace(' ','_')}.png")


# ── 10. Confusion Matrix ─────────────────────
def plot_confusion_matrix(cm: np.ndarray, class_names: list) -> str:
    """Heatmap of confusion matrix."""
    fig, ax = plt.subplots(figsize=(8, 6), facecolor=COLORS["bg"])
    im = ax.imshow(cm, cmap="YlOrRd")
    plt.colorbar(im, ax=ax)

    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(class_names, fontsize=8)

    for i in range(len(class_names)):
        for j in range(len(class_names)):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max()/2 else COLORS["dark"],
                    fontsize=9, fontweight="bold")

    _style_ax(ax, "Confusion Matrix — ML Model", "Predicted", "Actual")
    plt.tight_layout()
    return _save(fig, "confusion_matrix.png")


# ── Helpers ───────────────────────────────────
def _aqi_color(v: int) -> str:
    if v > 300: return "#7c3aed"
    if v > 200: return "#e53935"
    if v > 150: return "#f97316"
    if v > 100: return "#eab308"
    if v > 50:  return "#84cc16"
    return "#1baa5e"

def _aqi_label(v: int) -> str:
    if v > 300: return "Hazardous"
    if v > 200: return "Very Unhealthy"
    if v > 150: return "Unhealthy"
    if v > 100: return "Sensitive Groups"
    if v > 50:  return "Moderate"
    return "Good"


# ── Run standalone demo ───────────────────────
if __name__ == "__main__":
    print("📊 Generating sample visualizations...")

    # Sample forecast data
    sample_fc = [{"time": f"{h:02d}:00", "temp": 18 + i*1.5, "humidity": 70 - i,
                  "wind_speed": 12 + i*2} for i, h in enumerate(range(6, 54, 3))]

    plot_temperature_trend(sample_fc[:16], "Srinagar")
    plot_aqi_gauge(145, "New Delhi")
    plot_humidity_temp(sample_fc[:16], "Mumbai")
    plot_aqi_composition({"PM2.5": 45, "PM10": 72, "NO₂": 28, "O₃": 35, "CO": 12}, "Delhi")
    plot_wind_speed(sample_fc[:16], "Bhubaneswar")
    print(f"\n✅ All charts saved to: {PLOT_DIR}/")
