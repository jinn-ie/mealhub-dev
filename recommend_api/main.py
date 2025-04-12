from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd

from weather_api import get_weather_category

from recommender import Hybrid
from filter import ContextFilter


app = FastAPI()

class RecommendRequest(BaseModel):
    user_id: str
    pref_categories: List[str]
    pref_foods: List[str]
    timestamp: int
    lat: float
    lon: float

class RecommendResponse(BaseModel):
    recommendations: List[str]

@app.post("/recommend", response_model=RecommendResponse)
def get_recommendation(req: RecommendRequest):
    weather = get_weather_category(req.lat, req.lon)

    context_filter = ContextFilter(weather, req.timestamp)

    hybrid = Hybrid(user_id=req.user_id, pref_categories=req.pref_categories, pref_foods=req.pref_foods)
    raw_recommendations = hybrid.recommend()

    sorted_recommendations = sorted(
        raw_recommendations,
        key=lambda menu: context_filter.score(menu),
        reverse=True
    )

    return RecommendResponse(recommendations=sorted_recommendations)

