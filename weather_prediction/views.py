from django.shortcuts import render
from django.http import JsonResponse
import pickle, os, numpy as np, requests
from django.conf import settings

BASE = os.path.join(os.path.dirname(__file__), "ML_Model")

# ---------- LOAD MODELS ----------
weather_model = pickle.load(open(f"{BASE}/weather_model.pkl", "rb"))
storm_model   = pickle.load(open(f"{BASE}/storm_model.pkl", "rb"))
aqi_us_model  = pickle.load(open(f"{BASE}/aqi_us_model.pkl", "rb"))
aqi_uk_model  = pickle.load(open(f"{BASE}/aqi_uk_model.pkl", "rb"))

# ---------- LOAD METADATA ----------
encoders      = pickle.load(open(f"{BASE}/encoders.pkl", "rb"))
state_map     = pickle.load(open(f"{BASE}/state_district_map.pkl", "rb"))
location_meta = pickle.load(open(f"{BASE}/location_meta.pkl", "rb"))

# ---------- SAFE CAST ----------
def safe_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default


def dashboard(request):

    states = sorted(state_map.keys())
    from datetime import datetime

    today = datetime.now()
    formatted_date = str(today.strftime("%A, %B %d"))
    if "history" not in request.session:
        request.session["history"] = []

    history = request.session["history"]

    if request.method == "POST":
        mode = request.POST.get("mode", "live")
    else:
        mode = "live"

    result = {
        "emote":"🌍",
        "emoji":"🎏",
        "weather": "Weather",
        "storm": " ",
        "us_aqi": 0,
        "uk_aqi": 0,
        "travel": "visibility",
        "uv_msg": "UV",
        "state": "State",
        "district": "District",
    }

    location_info = {
        "latitude": 0,
        "longitude": 0,
        "timezone": "-/-"
    }

    if request.method == "POST":

        state = request.POST.get("region", "").strip()
        district = request.POST.get("location_name", "").strip()

        if not state or not district:
            return render(request, "dashboard.html", {
                "states": states,
                "mode": mode,
                "state_map": state_map,
                "format_date": formatted_date,
                "result": result,
                "location_info": location_info,
                "error": "Please select a state and district."
            })

        location_info = location_meta.get((state, district), location_info)

        state_enc = encoders["region"].transform([state])[0]
        dist_enc  = encoders["location_name"].transform([district])[0]

        # ---------- WEATHER ----------
        X_weather = np.array([[

            safe_float(request.POST.get("temperature")),
            safe_float(request.POST.get("feels_like_celsius")),
            safe_float(request.POST.get("humidity")),
            safe_float(request.POST.get("cloud")),
            safe_float(request.POST.get("visibility")),
            safe_float(request.POST.get("uv")),
            safe_float(request.POST.get("precip")),
            state_enc,
            dist_enc
        ]])

        weather = encoders["weather_condition"].inverse_transform(
            weather_model.predict(X_weather)
        )[0]

        # ---------- STORM ----------
        X_storm = np.array([[

            safe_float(request.POST.get("wind")),
            safe_float(request.POST.get("gust")),
            safe_float(request.POST.get("pressure")),
            safe_float(request.POST.get("humidity")),
            safe_float(request.POST.get("cloud")),
            safe_float(request.POST.get("precip")),

            state_enc,
            dist_enc
        ]])

        storm = encoders["storm"].inverse_transform(
            storm_model.predict(X_storm)
        )[0]

        # ---------- AQI ----------
        X_aqi = np.array([[

            safe_float(request.POST.get("pm25")),
            safe_float(request.POST.get("pm10")),
            safe_float(request.POST.get("no2")),
            safe_float(request.POST.get("so2")),
            safe_float(request.POST.get("o3")),
            safe_float(request.POST.get("co")),

            state_enc,
            dist_enc
        ]])

        us_aqi = encoders["air_quality_us-epa-index"].inverse_transform(
            aqi_us_model.predict(X_aqi)
        )[0]

        uk_aqi = encoders["air_quality_gb-defra-index"].inverse_transform(
            aqi_uk_model.predict(X_aqi)
        )[0]

        visibility = safe_float(request.POST.get("visibility"))
        travel = (
            "Poor visibility – drive carefully" if visibility < 2 else
            "Moderate visibility" if visibility < 5 else
            "Good visibility"
        )

        uv = safe_float(request.POST.get("uv"))
        uv_msg = (
            "Very high UV – avoid direct sunlight" if uv >= 8 else
            "Moderate UV – use sun protection" if uv >= 5 else
            "Low UV – safe"
        )

        Wemote={"Sunny":"🌞","Rainy":"🌧️","Foggy":"🌨️","Cloudy":"☁️","Partly Cloudy":"🌤️"}
        Semote={"Windstorm":"🌪️","Thunderstorm":"⛈️","Clear": "🪁","Cyclone Warning":"🌀"}


        result = {
            "emote":Wemote[weather],
            "emoji":Semote[storm],
            "weather": weather,
            "storm": storm,
            "us_aqi": us_aqi,
            "uk_aqi": uk_aqi,
            "travel": travel,
            "uv_msg": uv_msg,
            "state": state,
            "district": district
        }


    return render(request, "dashboard.html", {
        "states": states,
        "mode": mode,
        "state_map": state_map,
        "format_date": formatted_date,
        "result": result,
        "location_info": location_info,
        "selected_state": request.POST.get("region", ""),
        "selected_district": request.POST.get("location_name", ""),
        "form_data": request.POST if request.method == "POST" else {}
    })


# ---------- REALTIME API ----------
def realtime_weather(request):

    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if not lat or not lon:
        return JsonResponse({"error": "Missing coordinates"}, status=400)

    url = (
        f"http://api.weatherapi.com/v1/current.json"
        f"?key={settings.WEATHER_API_KEY}&q={lat},{lon}&aqi=yes"
    )

    res = requests.get(url)
    data = res.json()

    if "error" in data:
        return JsonResponse({"error": "API error"}, status=500)

    c = data["current"]
    a = c["air_quality"]

    return JsonResponse({
        "temperature": c["temp_c"],
        "feels_like_celsius": c["feelslike_c"],
        "humidity": c["humidity"],
        "cloud": c["cloud"],
        "visibility": c["vis_km"],
        "uv": c["uv"],
        "wind": c["wind_kph"],
        "gust": c["gust_kph"],
        "pressure": c["pressure_mb"],
        "precip": c["precip_mm"],
        "pm25": a["pm2_5"],
        "pm10": a["pm10"],
        "no2": a["no2"],
        "so2": a["so2"],
        "o3": a["o3"],
        "co": a["co"],
    })
