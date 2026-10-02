"""
Core prediction pipeline, shared by scripts/recommend.py (CLI) and the
FastAPI app (main.py) so there's exactly one place this logic lives.
"""
from pathlib import Path

import joblib
import pandas as pd

from app.food_mapping import get_foods
from app.recipes import get_recipes

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "rf_model.joblib"

_bundle = None  # lazy-loaded once, reused across requests


def _load_model():
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError("Model not found. Run scripts/train_model.py first.")
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def valid_symptoms() -> list[str]:
    return _load_model()["symptoms"]


def recommend(symptoms_present: list[str], top_k: int = 3, recipes_per_deficiency: int = 3) -> dict:
    bundle = _load_model()
    model, all_symptoms = bundle["model"], bundle["symptoms"]

    unknown = [s for s in symptoms_present if s not in all_symptoms]
    if unknown:
        raise ValueError(f"Unknown symptoms: {unknown}")

    row = pd.DataFrame([[int(s in symptoms_present) for s in all_symptoms]],
                       columns=all_symptoms)
    proba = model.predict_proba(row)[0]
    ranked = sorted(zip(model.classes_, proba), key=lambda p: p[1], reverse=True)[:top_k]

    results = []
    for nutrient, confidence in ranked:
        foods = get_foods(nutrient)
        recipes = get_recipes(foods[0], number=recipes_per_deficiency)
        results.append({
            "nutrient": nutrient,
            "confidence": round(float(confidence), 3),
            "recommended_foods": foods,
            "recipes": recipes,
        })
    return {"input_symptoms": symptoms_present, "predictions": results}
