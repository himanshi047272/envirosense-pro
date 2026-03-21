# ============================================
# model.py — ML Model Training & Prediction
# ============================================

import numpy as np
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, f1_score
)
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings("ignore")

from config import MODEL_PATH, SCALER_PATH, THRESHOLDS
from preprocessing import preprocess_pipeline, load_scaler, prepare_live_data


# ── Disaster Labels ──────────────────────────
DISASTER_LABELS = {
    0: "Normal",
    1: "Storm / High Wind",
    2: "Flood Risk",
    3: "Heatwave",
    4: "Cold Wave",
    5: "Air Pollution Spike",
    6: "Landslide Risk",
    7: "Cyclone Watch",
}


# ── 1. Split Data ────────────────────────────
def split_data(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
    """Split into train/test sets with stratification."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    print(f"[INFO] Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test


# ── 2. Train Multiple Models ─────────────────
def train_all_models(X_train, y_train) -> dict:
    """
    Train multiple classifiers and return all.
    """
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=10,
            min_samples_split=5,
            random_state=42
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=500,
            random_state=42,
            multi_class="ovr"
        ),
    }

    trained = {}
    print("\n🤖 Training models...")
    for name, model in models.items():
        print(f"  Training {name}...", end=" ")
        model.fit(X_train, y_train)
        trained[name] = model
        print("✅")

    return trained


# ── 3. Evaluate All Models ───────────────────
def evaluate_models(models: dict, X_test, y_test) -> pd.DataFrame:
    """
    Evaluate all models and return comparison table.
    """
    results = []
    print("\n📊 Model Evaluation:")
    print("-" * 55)

    for name, model in models.items():
        y_pred = model.predict(X_test)
        acc    = accuracy_score(y_test, y_pred)
        f1     = f1_score(y_test, y_pred, average="weighted")

        # 5-fold cross-validation
        cv_scores = cross_val_score(model, X_test, y_test, cv=5, scoring="accuracy")

        results.append({
            "Model":    name,
            "Accuracy": round(acc * 100, 2),
            "F1 Score": round(f1 * 100, 2),
            "CV Mean":  round(cv_scores.mean() * 100, 2),
            "CV Std":   round(cv_scores.std() * 100, 2),
        })

        print(f"  {name:<25} Acc: {acc*100:.1f}%  F1: {f1*100:.1f}%  CV: {cv_scores.mean()*100:.1f}%")

    df_results = pd.DataFrame(results).sort_values("Accuracy", ascending=False)
    print("-" * 55)
    print(f"\n🏆 Best model: {df_results.iloc[0]['Model']} ({df_results.iloc[0]['Accuracy']}%)")
    return df_results


# ── 4. Detailed Report for Best Model ────────
def detailed_report(model, X_test, y_test, model_name: str = "Best Model"):
    """Print classification report and confusion matrix."""
    y_pred = model.predict(X_test)

    print(f"\n📋 Classification Report — {model_name}:")
    print(classification_report(y_test, y_pred, target_names=[
        DISASTER_LABELS.get(i, str(i)) for i in sorted(y_test.unique())
    ]))

    print("🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    return cm


# ── 5. Tune Best Model (GridSearch) ──────────
def tune_model(X_train, y_train) -> RandomForestClassifier:
    """
    Hyperparameter tuning for Random Forest using GridSearch.
    """
    print("\n🔧 Tuning hyperparameters (this may take a few minutes)...")
    param_grid = {
        "n_estimators": [100, 200, 300],
        "max_depth":    [8, 12, 16],
        "min_samples_split": [2, 5, 10],
    }
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring="accuracy", n_jobs=-1)
    grid_search.fit(X_train, y_train)

    print(f"[INFO] Best params: {grid_search.best_params_}")
    print(f"[INFO] Best CV accuracy: {grid_search.best_score_*100:.2f}%")
    return grid_search.best_estimator_


# ── 6. Feature Importance ────────────────────
def feature_importance(model, feature_names: list) -> pd.DataFrame:
    """Return top features used by the model."""
    if not hasattr(model, "feature_importances_"):
        print("[WARN] Model does not support feature importance.")
        return pd.DataFrame()

    fi = pd.DataFrame({
        "Feature":    feature_names,
        "Importance": model.feature_importances_,
    }).sort_values("Importance", ascending=False)

    print("\n🔑 Top 10 Important Features:")
    print(fi.head(10).to_string(index=False))
    return fi


# ── 7. Save Model ────────────────────────────
def save_model(model, path: str = MODEL_PATH):
    """Save trained model to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"[INFO] Model saved to {path}")


# ── 8. Load Model ────────────────────────────
def load_model(path: str = MODEL_PATH):
    """Load saved model from disk."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}. Train first.")
    model = joblib.load(path)
    print(f"[INFO] Model loaded from {path}")
    return model


# ── 9. Predict Single City ───────────────────
def predict_disaster(weather_data: dict) -> dict:
    """
    Given live weather data dict, return disaster prediction.

    Args:
        weather_data: dict with keys:
            temp, feels_like, humidity, pressure,
            wind_speed, rainfall, aqi, pm25, visibility

    Returns:
        dict: { disaster_type, label, probability, risk_level, confidence }
    """
    model = load_model()

    # Preprocess live data
    X = prepare_live_data(weather_data)

    # Predict
    pred_class = model.predict(X)[0]
    pred_proba = model.predict_proba(X)[0]

    label       = DISASTER_LABELS.get(int(pred_class), "Unknown")
    probability = round(float(max(pred_proba)) * 100, 1)
    confidence  = round(float(sorted(pred_proba)[-2]) * 100, 1)  # 2nd highest

    # Risk level based on probability
    if probability >= 75:
        risk_level = "HIGH"
    elif probability >= 45:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    result = {
        "disaster_type": int(pred_class),
        "label":         label,
        "probability":   probability,
        "risk_level":    risk_level,
        "confidence":    confidence,
        "all_proba":     {DISASTER_LABELS[i]: round(float(p)*100,1) for i, p in enumerate(pred_proba)},
    }
    return result


# ── 10. Predict 7-Day Forecast ───────────────
def predict_7day_forecast(forecast_list: list) -> list:
    """
    Predict disaster risk for each of 7 forecast days.

    Args:
        forecast_list: list of daily weather dicts

    Returns:
        list of prediction dicts
    """
    results = []
    for i, day_data in enumerate(forecast_list[:7]):
        try:
            pred = predict_disaster(day_data)
            pred["day"] = i
            pred["date"] = day_data.get("date", f"Day {i+1}")
            results.append(pred)
        except Exception as e:
            results.append({"day": i, "label": "Unknown", "error": str(e)})
    return results


# ── 11. Rule-Based Fallback ───────────────────
def rule_based_predict(weather: dict) -> list:
    """
    Rule-based disaster detection (no ML model needed).
    Used as fallback / supplement to ML model.
    Returns list of active disasters.
    """
    disasters = []
    T = THRESHOLDS

    temp      = weather.get("temp", 25)
    feels     = weather.get("feels_like", 25)
    humidity  = weather.get("humidity", 60)
    wind      = weather.get("wind_speed", 10)
    rain_24h  = weather.get("rain_24h", 0)
    rain_48h  = weather.get("rain_48h", 0)
    rain_72h  = weather.get("rain_72h", 0)
    pres_drop = weather.get("pressure_drop", 0)
    aqi       = weather.get("aqi", 50)
    pm25      = weather.get("pm25", 10)
    is_hilly  = weather.get("is_hilly", False)
    is_coastal= weather.get("is_coastal", False)

    # Storm
    score = 0
    if wind > 60:       score += 40
    elif wind > 40:     score += 25
    if pres_drop > 8:   score += 15
    if humidity > 80:   score += 10
    if rain_24h > 15:   score += 10
    if score >= 30:
        disasters.append({
            "type": "storm", "label": "Storm / High Wind",
            "prob": min(97, score + 35),
            "level": "high" if score >= 60 else "medium" if score >= 40 else "low",
        })

    # Flood
    score = 0
    if rain_24h > 30:    score += 40
    elif rain_24h > 10:  score += 20
    if rain_48h > 50:    score += 20
    if humidity > 87:    score += 15
    elif humidity > 78:  score += 8
    if score >= 25:
        disasters.append({
            "type": "flood", "label": "Flood Risk",
            "prob": min(94, score + 30),
            "level": "high" if score >= 55 else "medium" if score >= 35 else "low",
        })

    # Heatwave
    score = 0
    if temp >= 44:              score += 50
    elif temp >= 40:            score += 35
    elif temp >= 38:            score += 22
    if feels >= temp + 4:       score += 12
    if humidity < 30 and temp > 35: score += 10
    if score >= 20:
        disasters.append({
            "type": "heatwave", "label": "Heatwave Alert",
            "prob": min(96, score + 32),
            "level": "high" if score >= 50 else "medium" if score >= 30 else "low",
        })

    # Cold Wave
    score = 0
    if temp <= 2:        score += 50
    elif temp <= 5:      score += 35
    elif temp <= 8:      score += 20
    if score >= 20:
        disasters.append({
            "type": "coldwave", "label": "Cold Wave Alert",
            "prob": min(93, score + 30),
            "level": "high" if score >= 50 else "medium" if score >= 30 else "low",
        })

    # Pollution
    if aqi > 100:
        score = 0
        if aqi > 300:    score += 60
        elif aqi > 200:  score += 45
        elif aqi > 150:  score += 28
        else:            score += 14
        if pm25 > 60:    score += 12
        disasters.append({
            "type": "pollution", "label": "Air Pollution Spike",
            "prob": min(99, score + 28),
            "level": "high" if score >= 55 else "medium" if score >= 35 else "low",
        })

    # Landslide (hilly only)
    if is_hilly:
        score = 0
        if rain_24h > 20:  score += 35
        elif rain_24h > 8: score += 20
        if rain_72h > 40:  score += 20
        if humidity > 80:  score += 12
        if score >= 25:
            disasters.append({
                "type": "landslide", "label": "Landslide Risk",
                "prob": min(88, score + 25),
                "level": "high" if score >= 50 else "medium" if score >= 35 else "low",
            })

    # Sort by severity
    level_order = {"high": 3, "medium": 2, "low": 1}
    disasters.sort(key=lambda x: level_order.get(x["level"], 0), reverse=True)
    return disasters


# ── Main: Full Training Pipeline ─────────────
if __name__ == "__main__":
    import sys

    data_path = sys.argv[1] if len(sys.argv) > 1 else "data/environment_data.csv"

    print("=" * 55)
    print("  EnviroSense Pro — ML Training Pipeline")
    print("=" * 55)

    # Step 1: Preprocess
    X, y, scaler = preprocess_pipeline(data_path, target_col="disaster_type")

    # Step 2: Split
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Step 3: Train all models
    all_models = train_all_models(X_train, y_train)

    # Step 4: Evaluate
    results_df = evaluate_models(all_models, X_test, y_test)
    print("\n", results_df.to_string(index=False))

    # Step 5: Best model details
    best_name = results_df.iloc[0]["Model"]
    best_model = all_models[best_name]
    detailed_report(best_model, X_test, y_test, best_name)

    # Step 6: Feature importance
    feature_importance(best_model, list(X.columns))

    # Step 7: Save
    save_model(best_model)
    print("\n✅ Training complete! Model saved.")
