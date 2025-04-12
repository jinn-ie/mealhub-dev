import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATEHR_API_KEY")

def get_weather_category(lat: float, lon: float) -> str:
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&lang=kr&units=metric"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_main = data["weather"][0]["main"]

        mapping = {
            "Clear": "맑음",
            "Clouds": "흐림",
            "Rain": "비",
            "Drizzle": "비",
            "Thunderstorm": "비",
            "Snow": "눈",
            "Mist": "안개",
            "Fog": "안개",
        }

        return mapping.get(weather_main, "맑음")

    except Exception as e:
        print(f"[날씨 API 오류] {e}")
        return "맑음"
