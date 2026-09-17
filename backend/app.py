
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from datetime import datetime
import sqlite3, json, joblib, pandas as pd, numpy as np

BASE = Path(__file__).resolve().parent
DB = BASE.parent / "database" / "traffic.db"
app = Flask(__name__)
CORS(app)

model = joblib.load(BASE / "model_pipeline.pkl")
features = joblib.load(BASE / "model_features.pkl")
profile = joblib.load(BASE / "historical_profile.pkl")
thresholds = joblib.load(BASE / "congestion_thresholds.pkl")
metrics = json.loads((BASE / "metrics.json").read_text())
config = json.loads((BASE / "config.json").read_text())

def init_db():
    DB.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT, area TEXT, date TEXT, time TEXT,
            weather TEXT, temperature REAL, predicted_volume REAL, congestion_level TEXT,
            congestion_score REAL, created_at TEXT)""")

def congestion(volume):
    if volume < thresholds["low"]: return "LOW"
    if volume < thresholds["medium"]: return "MEDIUM"
    if volume < thresholds["high"]: return "HIGH"
    return "SEVERE"

def row_for_prediction(payload):
    city, area = payload["city"], payload["area"]
    dt = pd.Timestamp(f'{payload["date"]} {payload["time"]}')
    hour = dt.hour + dt.minute/60
    # Profile is based on historical observations at the same location/time.
    p = profile[(profile.city == city) & (profile.area == area)]
    if p.empty:
        raise ValueError("Unknown city/area combination.")
    p = p.assign(hdiff=(p.hour-hour).abs()).sort_values("hdiff").iloc[0]
    dow = dt.dayofweek
    # Prefer exact weekday if available by recomputing nearest profile match.
    exact = p
    candidates = profile[(profile.city==city)&(profile.area==area)&(profile.dow==dow)]
    if not candidates.empty:
        exact = candidates.assign(hdiff=(candidates.hour-hour).abs()).sort_values("hdiff").iloc[0]
    return {
        "city":city,"area":area,"weather":payload["weather"],
        "temperature":float(payload["temperature"]),
        "speed":float(exact.speed),"road_capacity":float(exact.road_capacity),
        "hour":hour,"dow":dow,"month":dt.month,"is_weekend":int(dow>=5),
        "is_peak":int((7<=hour<=10) or (17<=hour<=20)),
        "hour_sin":np.sin(2*np.pi*hour/24),"hour_cos":np.cos(2*np.pi*hour/24),
        "dow_sin":np.sin(2*np.pi*dow/7),"dow_cos":np.cos(2*np.pi*dow/7),
        "lag_30m":float(exact.lag_30m),"lag_60m":float(exact.lag_60m),
        "lag_24h":float(exact.lag_24h),"rolling_6h":float(exact.rolling_6h),
        "rolling_24h":float(exact.rolling_24h)
    }

@app.get("/health")
def health():
    return jsonify({"status":"ok","model":"HistGradientBoostingRegressor","version":"2.0"})

@app.get("/config")
def get_config():
    return jsonify(config)

@app.get("/metrics")
def get_metrics():
    return jsonify(metrics)

@app.get("/history")
def history():
    limit=min(int(request.args.get("limit",20)),100)
    with sqlite3.connect(DB) as con:
        rows=con.execute("SELECT city,area,date,time,weather,temperature,predicted_volume,congestion_level,congestion_score,created_at FROM predictions ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    cols=["city","area","date","time","weather","temperature","predicted_volume","congestion_level","congestion_score","created_at"]
    return jsonify([dict(zip(cols,r)) for r in rows])

@app.post("/predict")
def predict():
    try:
        payload=request.get_json(force=True)
        required=["city","area","date","time","weather","temperature"]
        missing=[x for x in required if x not in payload or payload[x] in ("",None)]
        if missing: return jsonify({"error":f"Missing fields: {', '.join(missing)}"}),400
        row=row_for_prediction(payload)
        X=pd.DataFrame([row])[features]
        pred=float(max(0,model.predict(X)[0]))
        level=congestion(pred)
        score=float(min(100,max(0,round(pred/thresholds["high"]*100,1))))
        mae=metrics["MAE"]
        low=max(0,pred-mae); high=pred+mae
        recommendation={
            "LOW":"Traffic is light. Normal travel conditions expected.",
            "MEDIUM":"Moderate traffic expected. Allow a little extra travel time.",
            "HIGH":"High congestion expected. Consider leaving earlier or using an alternate route.",
            "SEVERE":"Severe congestion expected. Avoid the peak window if possible and consider an alternate route."
        }[level]
        with sqlite3.connect(DB) as con:
            con.execute("""INSERT INTO predictions
            (city,area,date,time,weather,temperature,predicted_volume,congestion_level,congestion_score,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",(payload["city"],payload["area"],payload["date"],payload["time"],
            payload["weather"],float(payload["temperature"]),round(pred,1),level,score,datetime.now().isoformat()))
        return jsonify({"traffic_volume":round(pred),"congestion_level":level,"congestion_score":score,
                        "prediction_range":[round(low),round(high)],"model_mae":round(mae,2),
                        "recommendation":recommendation})
    except Exception as e:
        return jsonify({"error":str(e)}),400

if __name__=="__main__":
    init_db()
    app.run(host="127.0.0.1",port=5000,debug=True)
