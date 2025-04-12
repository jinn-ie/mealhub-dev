from sqlalchemy import Column, Integer, String, Float
from database import Base

class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    menu_name = Column(String, index=True)
    calorie = Column(Integer)

class CosineSimilarity(Base):
    __tablename__ = "cosine_similarity"

    menu_id_1 = Column(Integer, primary_key=True, index=True)
    menu_id_2 = Column(Integer, primary_key=True, index=True)
    score = Column(Float)

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    menu_id = Column(Integer, index=True) 
    score = Column(Float)