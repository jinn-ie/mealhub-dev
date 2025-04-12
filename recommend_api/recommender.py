import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Menu, CosineSimilarity, Rating

class Recommender:
    def __init__(self):
        self._db: Session = SessionLocal()
        self._menu_df = pd.DataFrame([{
            "menu_name": menu.menu_name,
            "category": menu.category
        } for menu in self._db.query(Menu).all()])

    def recommend(self) -> list:
        return []

class CBF(Recommender):
    def __init__(self, pref_categories, pref_foods, alergic_foods=[]):
        super().__init__()
        self._cos_sim_dict = self._load_cosine_similarity()
        self._pref_categories = self._menu_df[self._menu_df["category"].isin(pref_categories)]["menu_name"].tolist()
        self._pref_foods = list(set(pref_foods) - set(pref_categories))
    
    def _load_cosine_similarity(self):
        sim_rows = self._db.query(CosineSimilarity).all()
        cos_sim_dict = {}
        for row in sim_rows:
            if row.menu_id_1 not in cos_sim_dict:
                cos_sim_dict[row.menu_id_1] = []
            cos_sim_dict[row.menu_id_1].append((row.menu_id_2, row.score))
        return pd.DataFrame(cos_sim_dict)

    def _get_similar_menus(self, index):
        sim_scores = list(enumerate(self._cos_sim.iloc[index].values))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:3]
        return [s[0] for s in sim_scores]

    def recommend(self) -> list:
        recommendations = []
        preferences = self._pref_categories + self._pref_foods
        for p in preferences:
            idx = self._menu_df.index[self._menu_df["menu_name"] == p][0]
            sim_i = self._get_similar_menus(idx)
            recommendations.extend([self._menu_df.iloc[i]["menu_name"] for i in sim_i]) 
        return list(set(recommendations))

class CF(Recommender):
    def __init__(self, user_id):
        super().__init__()
        self._user_id = user_id
        self._user_ratings = self._load_user_ratings()

    def _load_user_ratings(self):
        ratings = self._db.query(Rating).all()
        data = {}
        for rating in ratings:
            if rating.user_id not in data:
                data[rating.user_id] = {}
            data[rating.user_id][rating.menu_name] = rating.score
        return pd.DataFrame.from_dict(data, orient='index')

    def _get_similar_users(self, user_id):
        if user_id not in self._user_ratings.index:
            return []
        user_data = self._user_ratings.loc[user_id]
        similarities = self._user_ratings.corrwith(user_data, axis=1).dropna()
        return similarities.sort_values(ascending=False).index[1:3]

    def recommend(self) -> list:
        similar_users = self._get_similar_users(self._user_id)
        recommendations = []
        for user in similar_users:
            user_rated_menus = self._user_ratings.loc[user]
            top_menus = user_rated_menus[user_rated_menus > 7500].index.tolist()
            recommendations.extend(top_menus)
        return list(set(recommendations))

class Hybrid(Recommender):
    def __init__(self, user_id, pref_categories, pref_foods):
        super().__init__()
        self._user_id = user_id
        self._cbf = CBF(pref_categories, pref_foods)
        self._cf = CF(user_id)

    def get_weight(self):
        if self._user_id not in self._cf._user_ratings.index:
            return 0.9, 0.1
        user_data = self._cf._user_ratings.loc[self._user_id]
        filled_ratio = user_data.count() / len(user_data)
        cf_weight = min(0.8, max(0.1, filled_ratio))
        cbf_weight = 1.0 - cf_weight
        return cbf_weight, cf_weight

    def recommend(self) -> list:
        cbf_recommendations = self._cbf.recommend()
        cf_recommendations = self._cf.recommend()
        cbf_weight, cf_weight = self.get_weight()
        score_map = {}
        for menu in cbf_recommendations:
            score_map[menu] = score_map.get(menu, 0) + cbf_weight
        for menu in cf_recommendations:
            score_map[menu] = score_map.get(menu, 0) + cf_weight
        sorted_menus = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        return [menu for menu, _ in sorted_menus]
