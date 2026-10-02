"""Pydantic models: define the shape of API requests/responses."""
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    symptoms: list[str] = Field(..., min_length=1, examples=[
        ["fatigue", "pale_skin", "dizziness", "cold_hands_feet"]
    ])


class Recipe(BaseModel):
    title: str
    image: str
    url: str


class Prediction(BaseModel):
    nutrient: str
    confidence: float
    recommended_foods: list[str]
    recipes: list[Recipe]


class PredictResponse(BaseModel):
    input_symptoms: list[str]
    predictions: list[Prediction]


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: str
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    username: str
    email: str
