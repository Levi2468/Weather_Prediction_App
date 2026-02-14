import pandas as pd
import numpy as np
import os, pickle
import kagglehub
from functools import reduce
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.base import clone
import xgboost as xgb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- LOAD DATA ----------------
path = kagglehub.dataset_download("pratikjadhav05/indian-weather-data")

def load_file(fp):
    if fp.endswith(".csv"):
        return pd.read_csv(fp)
    if fp.endswith((".xls", ".xlsx")):
        return pd.read_excel(fp)

dfs = [load_file(os.path.join(path,f)) for f in os.listdir(path)]
dfs = [d for d in dfs if d is not None]

common_cols = set(dfs[0].columns)
for d in dfs[1:]:
    common_cols &= set(d.columns)

df = reduce(lambda a,b: pd.merge(a,b,on=list(common_cols),how="outer"), dfs)

# ---------------- CLEAN ----------------
df.drop(columns=["country","sunrise","sunset","moonrise","moonset"],
        errors="ignore", inplace=True)
df.drop(columns=df.select_dtypes("datetime64").columns, inplace=True)

# ---------------- STATE → DISTRICT MAP ----------------
state_district_map = (
    df.groupby("region")["location_name"]
    .unique()
    .apply(sorted)
    .to_dict()
)

# ---------------- TARGET LOGIC ----------------
def get_weather(row):
    if row["precip_mm"] > 0.2 and row["cloud"] > 60:
        return "Rainy"
    if row["visibility_km"] < 2 and row["humidity"] > 85:
        return "Foggy"
    if row["cloud"] > 65:
        return "Cloudy"
    if row["cloud"] < 30 and row["uv_index"] >= 5:
        return "Sunny"
    return "Partly Cloudy"

def get_storm(row):
    if row["pressure_mb"] < 995 and row["gust_kph"] > 40:
        return "Cyclone Warning"
    if row["precip_mm"] > 10:
        return "Thunderstorm"
    if row["gust_kph"] > 30:
        return "Windstorm"
    return "Clear"

df["weather_condition"] = df.apply(get_weather, axis=1)
df["storm"] = df.apply(get_storm, axis=1)

location_meta = (
    df.groupby(["region", "location_name"])
      .agg({
          "latitude": "first",
          "longitude": "first",
          "timezone": "first"
      })
      .reset_index()
)

# ---------------- ENCODERS ----------------
encoders = {}
for col in ["region","location_name","weather_condition","storm",
            "air_quality_us-epa-index","air_quality_gb-defra-index"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# ---------------- FEATURES ----------------
feature_schema = {
    "weather": [
        "temperature_celsius","feels_like_celsius","humidity","cloud","visibility_km",
        "uv_index","precip_mm","region","location_name"
    ],
    "storm": [
        "wind_kph","gust_kph","pressure_mb",
        "humidity","cloud","precip_mm","region","location_name"
    ],
    "aqi": [
        "air_quality_PM2.5","air_quality_PM10",
        "air_quality_Nitrogen_dioxide",
        "air_quality_Sulphur_dioxide",
        "air_quality_Ozone",
        "air_quality_Carbon_Monoxide",
        "region","location_name"
    ]
}

# ---------------- BASE MODEL ----------------
base_model = xgb.XGBClassifier(
    n_estimators=400,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss",
    random_state=42
)

# ---------------- WEATHER MODEL ----------------
Xw = df[feature_schema["weather"]]
yw = df["weather_condition"]

cw = compute_class_weight("balanced", classes=np.unique(yw), y=yw)
sw = np.array([dict(zip(np.unique(yw),cw))[i] for i in yw])

weather_model = clone(base_model)
weather_model.fit(Xw, yw, sample_weight=sw)

# ---------------- STORM MODEL ----------------
Xs = df[feature_schema["storm"]]
ys = df["storm"]

storm_model = clone(base_model)
storm_model.fit(Xs, ys)

# ---------------- AQI MODELS ----------------
Xa = df[feature_schema["aqi"]]

aqi_us_model = clone(base_model)
aqi_us_model.fit(Xa, df["air_quality_us-epa-index"])

aqi_uk_model = clone(base_model)
aqi_uk_model.fit(Xa, df["air_quality_gb-defra-index"])

# ---------------- SAVE ----------------
os.makedirs(BASE_DIR, exist_ok=True)

pickle.dump(weather_model, open(f"{BASE_DIR}/weather_model.pkl","wb"))
pickle.dump(storm_model, open(f"{BASE_DIR}/storm_model.pkl","wb"))
pickle.dump(aqi_us_model, open(f"{BASE_DIR}/aqi_us_model.pkl","wb"))
pickle.dump(aqi_uk_model, open(f"{BASE_DIR}/aqi_uk_model.pkl","wb"))
pickle.dump(encoders, open(f"{BASE_DIR}/encoders.pkl","wb"))
pickle.dump(feature_schema, open(f"{BASE_DIR}/feature_schema.pkl","wb"))
pickle.dump(state_district_map, open(f"{BASE_DIR}/state_district_map.pkl","wb"))

print("✅ Training complete with State & District support")
# ---------------- LOCATION METADATA ----------------


# Convert to dictionary for fast lookup
location_meta_dict = {
    (row["region"], row["location_name"]): {
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "timezone": row["timezone"]
    }
    for _, row in location_meta.iterrows()
}

# Save it
pickle.dump(
    location_meta_dict,
    open(os.path.join(BASE_DIR, "location_meta.pkl"), "wb")
)

print("✅ Location metadata saved")
