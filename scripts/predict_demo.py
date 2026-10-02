"""
Test the saved model on its own, no training needed.

Run from the project root:
  python scripts/predict_demo.py fatigue pale_skin dizziness cold_hands_feet
  python scripts/predict_demo.py --list          (show all valid symptom names)
"""
import sys
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "rf_model.joblib"


def predict(symptoms_present: list[str], top_k: int = 3) -> list[tuple[str, float]]:
    bundle = joblib.load(MODEL_PATH)
    model, all_symptoms = bundle["model"], bundle["symptoms"]

    unknown = [s for s in symptoms_present if s not in all_symptoms]
    if unknown:
        raise ValueError(f"Unknown symptoms: {unknown}. Use --list to see valid names.")

    row = pd.DataFrame([[int(s in symptoms_present) for s in all_symptoms]],
                       columns=all_symptoms)
    proba = model.predict_proba(row)[0]
    ranked = sorted(zip(model.classes_, proba), key=lambda p: p[1], reverse=True)
    return [(name, float(p)) for name, p in ranked[:top_k]]


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    if not MODEL_PATH.exists():
        raise SystemExit("Model not found. Run scripts/train_model.py first.")
    if args == ["--list"]:
        print("\n".join(joblib.load(MODEL_PATH)["symptoms"]))
        raise SystemExit

    print(f"Symptoms: {', '.join(args)}\n")
    for name, p in predict(args):
        print(f"  {name:<12} {p:6.1%}")
