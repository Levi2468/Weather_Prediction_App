from django.urls import path
from .views import dashboard, realtime_weather

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("realtime-weather/", realtime_weather, name="realtime_weather"),
]

