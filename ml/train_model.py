
"""Train the traffic forecasting model.
Dataset in this project is a realistic synthetic benchmark. Replace data/traffic_data.csv
with real sensor/GPS observations for production use.
"""
from pathlib import Path
import pandas as pd, numpy as np, joblib, json
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data/traffic_data.csv"; BACK=ROOT/"backend"
FEATURES=["city","area","weather","temperature","speed","road_capacity","hour","dow","month","is_weekend","is_peak","hour_sin","hour_cos","dow_sin","dow_cos","lag_30m","lag_60m","lag_24h","rolling_6h","rolling_24h"]
CAT=["city","area","weather"]; NUM=[x for x in FEATURES if x not in CAT]
def main():
    df=pd.read_csv(DATA,parse_dates=["timestamp"]).sort_values(["area","timestamp"])
    cut=pd.Timestamp("2025-08-01")
    train=df[df.timestamp<cut]; test=df[df.timestamp>=cut]
    prep=ColumnTransformer([("cat",OneHotEncoder(handle_unknown="ignore",sparse_output=False),CAT)],remainder="passthrough")
    model=HistGradientBoostingRegressor(max_iter=350,learning_rate=.08,max_leaf_nodes=31,l2_regularization=1.0,random_state=42)
    pipe=Pipeline([("preprocessor",prep),("model",model)])
    pipe.fit(train[FEATURES],train.traffic_volume)
    pred=pipe.predict(test[FEATURES])
    metrics={"MAE":float(mean_absolute_error(test.traffic_volume,pred)),"RMSE":float(mean_squared_error(test.traffic_volume,pred)**.5),"R2":float(r2_score(test.traffic_volume,pred))}
    BACK.mkdir(exist_ok=True)
    joblib.dump(pipe,BACK/"model_pipeline.pkl"); joblib.dump(FEATURES,BACK/"model_features.pkl")
    prof=train.groupby(["city","area","dow","hour"]).agg(lag_30m=("lag_30m","mean"),lag_60m=("lag_60m","mean"),lag_24h=("lag_24h","mean"),rolling_6h=("rolling_6h","mean"),rolling_24h=("rolling_24h","mean"),speed=("speed","mean"),road_capacity=("road_capacity","mean")).reset_index()
    joblib.dump(prof,BACK/"historical_profile.pkl")
    json.dump(metrics,open(BACK/"metrics.json","w"),indent=2)
    print(json.dumps(metrics,indent=2))
if __name__=="__main__": main()
