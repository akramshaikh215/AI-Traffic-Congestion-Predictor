
"""Print time-series test metrics and congestion classification report."""
from pathlib import Path
import pandas as pd, numpy as np, joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, classification_report
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/"data/traffic_data.csv",parse_dates=["timestamp"])
model=joblib.load(ROOT/"backend/model_pipeline.pkl"); features=joblib.load(ROOT/"backend/model_features.pkl")
test=df[df.timestamp>=pd.Timestamp("2025-08-01")]
p=model.predict(test[features])
print("Holdout period: 2025-08-01 to 2025-12-31")
print(f"MAE : {mean_absolute_error(test.traffic_volume,p):.2f}")
print(f"RMSE: {mean_squared_error(test.traffic_volume,p)**.5:.2f}")
print(f"R2  : {r2_score(test.traffic_volume,p):.4f}")
def level(x): return "LOW" if x<1000 else "MEDIUM" if x<2000 else "HIGH" if x<3000 else "SEVERE"
print(classification_report(test.traffic_volume.map(level),pd.Series(p).map(level),zero_division=0))
