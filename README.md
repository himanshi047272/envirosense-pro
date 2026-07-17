# 🛰️ EnviroSense Pro
### AI-Powered Smart Environmental Monitoring & Disaster Prediction System

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![Machine Learning](https://img.shields.io/badge/Machine-Learning-green)
![Scikit Learn](https://img.shields.io/badge/scikit--learn-orange?logo=scikitlearn)
![License](https://img.shields.io/badge/License-MIT-blue)

</p>

---

## 📌 Overview

Natural disasters such as floods, storms, landslides, heatwaves, and air pollution continue to affect millions of people every year. Traditional monitoring systems often provide delayed warnings and limited decision support.

**EnviroSense Pro** is an AI-powered environmental monitoring platform that combines **Machine Learning**, **live weather APIs**, **rule-based disaster intelligence**, and **interactive visualization** to monitor environmental conditions and predict disaster risks in real time.

The system provides actionable insights through an intelligent dashboard, helping users understand environmental conditions and receive early warnings before disasters occur.

---

## ✨ Features

- 🌍 Real-time environmental monitoring
- 🌡 Live weather & AQI integration
- 🤖 Machine Learning based disaster prediction
- 🚨 Hybrid Rule-Based + AI Alert Engine
- 🗺 Interactive Risk Map
- 📅 7-Day Disaster Forecast
- 📈 Interactive visual analytics
- 🤖 EnviroBot AI Assistant
- 🌐 REST API support
- 💾 Model persistence using Joblib

---

## 🏗 System Architecture

```

OpenWeatherMap API
│
▼
Data Collection
│
▼
Data Preprocessing
│
▼
Feature Engineering
│
▼
Machine Learning Models
(Random Forest, XGBoost,
Gradient Boosting,
Decision Tree,
Logistic Regression)
│
▼
Hybrid Disaster Engine
(ML + Rule Based)
│
▼
REST API (Flask)
│
▼
Dashboard + EnviroBot

```

---

## 🤖 Machine Learning Pipeline

### Data Collection

- Live Weather Data
- Air Quality Data
- Historical Environmental Dataset

### Data Preprocessing

- Missing Value Handling
- Duplicate Removal
- Feature Scaling
- Label Encoding
- Feature Engineering

### Engineered Features

- Heat Stress Index
- Flood Risk Index
- Pressure Drop
- Temperature Indicators
- Wind Severity
- AQI Categories
- Rainfall Indicators

### Models Evaluated

| Model | Purpose |
|--------|----------|
| Random Forest | Primary Classifier |
| XGBoost | Ensemble Learning |
| Gradient Boosting | Performance Comparison |
| Decision Tree | Baseline Tree Model |
| Logistic Regression | Baseline Model |

---

## 📊 Dashboard

### Dashboard includes

- Live Weather Cards
- Air Quality Monitoring
- Disaster Risk Gauge
- Interactive Risk Map
- Environmental Trends
- Prediction Charts
- Alert System
- AI Chatbot

---

## 🚨 Disaster Detection

The system predicts multiple disaster categories including:

- 🌊 Flood
- ⛈ Storm
- 🔥 Heatwave
- ❄ Cold Wave
- 🌫 Air Pollution
- ⛰ Landslide
- 🌀 Cyclone

A hybrid scoring mechanism combines **Machine Learning predictions** with **rule-based risk analysis** to improve reliability.

---

## 📈 Model Evaluation

Models are evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- Cross Validation
- Feature Importance

The best performing model is automatically selected and saved for deployment.

---

## 🛠 Tech Stack

### Backend

- Python
- Flask

### Machine Learning

- Scikit-learn
- XGBoost
- Pandas
- NumPy

### Visualization

- Plotly
- Matplotlib
- Leaflet
- OpenStreetMap

### APIs

- OpenWeatherMap API

### Deployment

- Flask
- Render / Railway

---

## 📂 Project Structure

```

EnviroSense-Pro/
│
├── app.py
├── main.py
├── preprocessing.py
├── model.py
├── alerts.py
├── chatbot.py
├── visualization.py
│
├── data/
├── models/
├── templates/
├── static/
├── assets/
├── requirements.txt
└── README.md

```

---

## 🚀 Getting Started

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/EnviroSense-Pro.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python main.py
```

Open

```
http://localhost:5000
```

---

## 📸 Screenshots

> Add these images after uploading them.

- Dashboard
- Risk Map
- Prediction Charts
- Alert System
- AI Chatbot
- Architecture Diagram

---

## 📄 Project Report

A detailed project report containing the complete methodology, literature review, implementation details, and evaluation is available in this repository.

📘 **Project_Report.pdf**

---

## 🔮 Future Improvements

- Deep Learning based forecasting
- Satellite imagery integration
- IoT sensor support
- Mobile application
- Docker deployment
- Kubernetes deployment
- Multi-language support
- LLM-powered environmental assistant

---

## 👩‍💻 Author

**Himanshi Tanwar**

Bachelor of Computer Applications (AI & ML)

Interested in

- Artificial Intelligence
- Machine Learning
- Deep Learning
- Computer Vision
- Environmental Analytics

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
