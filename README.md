# AI Traffic Congestion Predictor 

A full-stack ML traffic intelligence prototype using a **HistGradientBoostingRegressor** with time-series-aware features, chronological holdout evaluation, historical location profiles, a Flask API, SQLite prediction history, and a responsive dashboard.



## Model
**HistGradientBoostingRegressor** (scikit-learn), a gradient-boosted decision-tree model for tabular regression.

Target:
`traffic_volume` (vehicles/hour)

Congestion is derived from predicted volume:
- < 1000 → LOW
- 1000–1999 → MEDIUM
- 2000–2999 → HIGH
- ≥ 3000 → SEVERE

## Validation
The model is evaluated on a chronological holdout beginning **2025-08-01**, rather than randomly mixing future and past observations.

Current benchmark on the included synthetic dataset:
- MAE ≈ 104.6 vehicles/hour
- RMSE ≈ 131.6 vehicles/hour
- R² ≈ 0.9891

**Important:** the included dataset is synthetic but designed to behave like a traffic time series. These metrics must NOT be presented as real-world accuracy. For a production-grade project, replace the CSV with real sensor/GPS/traffic-count data and retrain.

## Run

### 1. Create an environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install
```bash
pip install -r requirements.txt
```

### 3. (Optional) Retrain
```bash
cd ml
python train_model.py
cd ..
```

### 4. Start API
```bash
python backend/app.py
```

API: `http://127.0.0.1:5000`

### 5. Open frontend
Open `frontend/index.html` in a browser.

## API example
POST `/predict`
```json
{
  "city": "Hyderabad",
  "area": "HITEC City",
  "date": "2026-09-14",
  "time": "18:30",
  "weather": "Rainy",
  "temperature": 27
}
```

## Recommended next step for a true 9.5+ academic/portfolio version
Use real historical traffic data (traffic counts or GPS speeds) and add:
1. live map integration,
2. multi-step forecasting (15/30/60 minutes),
3. real holiday/event/roadwork features,
4. model comparison (Random Forest, XGBoost/LightGBM/CatBoost where available),
5. SHAP feature explanations,
6. drift monitoring and periodic retraining,
7. route-level congestion rather than area-level prediction.

