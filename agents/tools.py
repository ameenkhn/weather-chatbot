# agents/tools.py
import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_data(city: str) -> Dict[str, Any]:
    """
    Fetch real-time weather data for a city using OpenWeather API.
    Returns dict with fields or {'error': '...'} on failure.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY missing in environment"}

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}

    data = resp.json()
    if "main" not in data or "weather" not in data:
        return {"error": "Unexpected response from OpenWeather"}

    return {
        "city": data.get("name", city),
        "temp": data["main"].get("temp"),
        "feels_like": data["main"].get("feels_like"),
        "humidity": data["main"].get("humidity"),
        "description": data["weather"][0].get("description", "").capitalize(),
        "raw": data
    }