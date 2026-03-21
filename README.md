# 🛰️ EnviroSense Pro — AI-Based Smart Environmental Monitoring & Disaster Prediction System

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=flat-square&logo=flask)
![ML](https://img.shields.io/badge/ML-XGBoost%20%7C%20Random%20Forest-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

> A complete end-to-end system that monitors real-time environmental parameters, predicts disaster risks using Machine Learning, and provides actionable alerts for any location in India and worldwide.

---

## 📸 Dashboard Preview

The system includes a fully interactive web dashboard with:
- Real-time weather cards (Temperature, Humidity, AQI, Wind)
- Interactive Leaflet risk map with color-coded city markers
- 7-day disaster forecast matrix
- ML-powered prediction charts
- Rule-based + ML hybrid alert engine
- AI chatbot (EnviroBot)

---

## 🏗️ Project Structure

```
envirosense-pro/
│
├── main.py              ← Entry point (run this!)
├── app.py               ← Flask backend + all API routes
├── model.py             ← ML model training & prediction
├── preprocessing.py     ← Data cleaning & feature engineering
├── alerts.py            ← Disaster alert logic & suggestions
├── visualization.py     ← Charts (Matplotlib/Plotly)
├── chatbot.py           ← EnviroBot AI assistant
├── config.py            ← API keys & configuration
├── requirements.txt     ← Python dependencies
│
├── data/
│   ├── environment_data.csv   ← Raw training dataset
│   └── cleaned_data.csv       ← Auto-generated after preprocessing
│
├── models/
│   ├── trained_model.pkl      ← Saved ML model (after training)
│   └── scaler.pkl             ← Saved data scaler
│
├── templates/
│   ├── index.html             ← Main dashboard (single-page app)
│   └── dashboard.html         ← Alternative dashboard view
│
├── static/
│   ├── style.css              ← Custom styles
│   ├── script.js              ← Frontend JS (API calls, charts)
│   └── plots/                 ← Auto-generated chart images
│
└── docs/
    └── README.md              ← This file
```

---

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/envirosense-pro.git
cd envirosense-pro
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up API Key
Get a **free** OpenWeatherMap API key at https://openweathermap.org/api

Create a `.env` file in the project root:
```env
OWM_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

OR edit `config.py` directly (not recommended for production).

### 4. Run the App
```bash
# Start full web dashboard
python main.py

# Open in browser
http://localhost:5000
```

---

## 🤖 ML Model Training

### Step 1: Preprocess Data
```bash
python main.py --preprocess
```

### Step 2: Train Model
```bash
python main.py --train
```

This will:
- Train 5 models (Random Forest, XGBoost, Gradient Boosting, Decision Tree, Logistic Regression)
- Print accuracy comparison table
- Save the best model to `models/trained_model.pkl`

Expected output:
```
Model                    Accuracy   F1 Score   CV Mean
Random Forest            94.2%      93.8%      93.1%
XGBoost                  92.7%      92.1%      91.8%
Gradient Boosting        91.5%      90.9%      90.4%
...
✅ Best model: Random Forest (94.2%)
```

### Step 3: Test Alerts for a City
```bash
python main.py --alert Srinagar
python main.py --alert "New Delhi"
python main.py --alert Mumbai
```

### Demo Mode (No API Key Needed)
```bash
python main.py --demo
```

---

## 🧠 Disaster Detection Logic

The system uses a **multi-factor weighted scoring engine** (no random simulation):

| Disaster | Key Conditions | Threshold |
|---|---|---|
| ⛈️ Storm | Wind speed + pressure drop + humidity | Wind > 40 km/h |
| 🌊 Flood | Rainfall accumulation + humidity | Rain > 20mm/24h |
| 🔥 Heatwave | Temperature + heat index | Temp ≥ 38°C |
| ❄️ Cold Wave | Temperature + sudden drop + western disturbance | Temp ≤ 8°C |
| 🌫️ Pollution | AQI + PM2.5 + wind speed (trapping) | AQI > 150 |
| ⛰️ Landslide | Hilly terrain + rainfall accumulation | Rain > 20mm + hilly |
| 🌀 Cyclone | Coastal city + wind + pressure drop | Coastal + Wind > 35 |

Each factor has a **weighted score**. Score threshold determines risk level:
- Score ≥ 60 → **HIGH**
- Score ≥ 40 → **MEDIUM**  
- Score ≥ 30 → **LOW**

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Dashboard homepage |
| GET | `/api/weather?lat=28.6&lon=77.2&city=Delhi` | Live weather + AQI + forecast |
| GET | `/api/cities` | All supported cities |
| POST | `/api/alerts` | Get disaster alerts for weather data |
| POST | `/api/predict` | ML disaster prediction |
| POST | `/api/chat` | Chat with EnviroBot |
| GET | `/api/chat/history` | Chat history |
| GET | `/health` | Server health check |

### Example: Fetch Weather
```bash
curl "http://localhost:5000/api/weather?lat=34.08&lon=74.79&city=Srinagar"
```

### Example: Chat with Bot
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is it safe to go outside in Srinagar?"}'
```

---

## 📊 ML Models Used

| Model | Task | Algorithm |
|---|---|---|
| Disaster Classifier | Multi-class classification | Random Forest / XGBoost |
| Baseline | Comparison | Logistic Regression |
| Ensemble | Best accuracy | Gradient Boosting |

**Features Used:**
- Temperature, Feels Like, Humidity, Pressure
- Wind Speed, Rainfall (24h/48h/72h)
- AQI, PM2.5, PM10, NO2
- Derived: Heat Stress Index, Flood Risk Index, Pressure Drop
- Terrain flags: is_hilly, is_coastal

---

## 🗺️ Supported Cities

India: New Delhi, Mumbai, Srinagar, Shimla, Bhubaneswar, Chennai, Bengaluru, Kolkata, Hyderabad, Jaipur, Patna, Guwahati, Visakhapatnam, Kochi, Lucknow, Dehradun, Darjeeling

International: London, New York, Tokyo, Dubai, Beijing, Singapore

---

## 🔧 Configuration

Edit `config.py` to change:
- API key
- Disaster thresholds
- City database
- Model paths
- Alert sensitivity

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+, Flask 3.0 |
| ML | Scikit-learn, XGBoost, Pandas, NumPy |
| Data | OpenWeatherMap API, AQI API |
| Frontend | HTML5, CSS3, Vanilla JS, Chart.js |
| Maps | Leaflet.js + OpenStreetMap |
| Charts | Matplotlib, Plotly |
| Auth | localStorage (browser-based) |

---

## 🚀 Deploying Online

### Option 1: Render (Free, Recommended)
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set Environment Variable: `OWM_API_KEY = your_key`
5. Start command: `python main.py`

### Option 2: Railway
```bash
railway login
railway init
railway up
```

### Option 3: Local Network (Share with phone on same WiFi)
```bash
python main.py
# Access from phone: http://YOUR_PC_IP:5000
```

---

## 📝 Dataset Format

Your CSV (`data/environment_data.csv`) should have these columns:

| Column | Type | Description |
|---|---|---|
| temperature | float | °C |
| humidity | float | % |
| wind_speed | float | km/h |
| pressure | float | hPa |
| rainfall | float | mm |
| aqi | int | Air Quality Index |
| disaster_type | int | 0=Normal, 1=Storm, 2=Flood, 3=Heatwave, 4=Cold, 5=Pollution, 6=Landslide |

---

## 👩‍💻 Author

**Arjun Sharma**  
B.Tech CSE — Environmental Monitoring Project  
Powered by OpenWeatherMap API + Python ML

---

## 📄 License

MIT License — Free to use for academic and personal projects.
