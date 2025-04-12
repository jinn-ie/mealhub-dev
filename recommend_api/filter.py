import datetime

class Filter:
    def __init__(self):
        pass

class WeatherFilter(Filter):
    def __init__(self, current_weather: str):
        self.current_weather = current_weather
        ##
        self.weather_scores = {
        }

    def score(self, menu_name: str) -> float:
        return self.weather_scores.get(self.current_weather, {}).get(menu_name, 0.0)
    
class TimeFilter(Filter):
    def __init__(self, timestamp: int):
        self.timestamp = timestamp
        self.slot = self._convert_to_slot()

    def _convert_to_slot(self) -> str:
        hour = datetime.fromtimestamp(self.timestamp).hour
        if hour < 10:
            return "아침"
        elif hour < 14:
            return "점심"
        elif hour < 18:
            return "저녁"
        return "야식"

    def score(self, menu_name: str) -> float:
        ##
        return {
            "아침": {"죽": 1.0},
            "점심": {"비빔밥": 1.0},
            "저녁": {"삼겹살": 1.0},
            "야식": {"라면": 1.0}
        }.get(self.slot, {}).get(menu_name, 0.0)

class ContextFilter(WeatherFilter, TimeFilter):
    def __init__(self, current_weather, timestamp):
        self.weather = WeatherFilter(current_weather)
        self.time = TimeFilter(timestamp)

    def score(self, menu_name: str) -> float:
        return self.weather.score(menu_name) + self.time.score(menu_name)