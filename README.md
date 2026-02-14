**🌦 Weather Intelligence Dashboard – Project Overview**
<img width="1879" height="883" alt="Screenshot 2025-12-25 160507" src="https://github.com/user-attachments/assets/1d90f571-b0a0-4fff-bf1c-0ab086441dcc" />
The Weather Intelligence Dashboard is an interactive, map-based web application that provides district-level weather and air-quality predictions across India.
Users can select a state and district directly from a visual map, fetch real-time weather data, and view AI-driven predictions for weather conditions, storms, air quality, and safety advisories — all in a single unified interface.

**Interactive Map-Based Location Selection**
<img width="1882" height="887" alt="Screenshot 2025-12-25 154730" src="https://github.com/user-attachments/assets/c0d81e26-1e63-4b05-9483-11864d861e43" />
- The dashboard initially displays a clickable India map with state boundaries.
- When a state is clicked, the map transitions to a district-level view of that state.
Clicking a district automatically:
- Selects the location
- Loads latitude, longitude, and timezone
- Prepares the system for prediction (manual or live mode)

**Prediction Output Dashboard**
  <img width="823" height="886" alt="Screenshot 2025-12-25 154751" src="https://github.com/user-attachments/assets/6f6baf2c-d784-4710-91cb-70513f7a893c" />
**Displayed Predictions**
- Weather Condition (Sunny, Cloudy, Rainy, etc.)
- Temperature & Humidity
- Storm Alert Status
- Travel Advisory (based on visibility)
- UV Safety Guidance
- Air Quality Index
- 🇺🇸 US AQI (1–6)
- 🇬🇧 UK AQI (1–10)
  
**Visual Enhancements**
- Dynamic weather icons
- Gradient AQI bars indicating severity (Good → Hazardous)
Location metadata:
- Latitude
- Longitude
- Timezone
All predictions update without resetting the map or inputs, ensuring a smooth user experience.

**Machine Learning & Intelligence Layer**
Models Used:
- Weather Classification Model
- Storm Prediction Model
- US AQI Prediction Model
- UK AQI Prediction Model
Features:
- Temperature, humidity, visibility, wind, pressure, UV
- Pollutants (PM2.5, PM10, NO₂, SO₂, O₃, CO)
- Encoded geographic context (state & district)
Each model is trained offline and deployed via Django, ensuring fast and reliable inference.
  
