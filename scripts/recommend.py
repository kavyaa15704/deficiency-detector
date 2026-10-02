"""
CLI pipeline test: symptoms -> predicted deficiencies -> foods -> recipes.
Thin wrapper around app/inference.py, which is also used by the FastAPI app.

Run from the project root:
  python scripts/recommend.py fatigue pale_skin dizziness cold_hands_feet
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # so `app` package imports

from app.inference import recommend


def print_report(result: dict) -> None:
    print(f"Symptoms: {', '.join(result['input_symptoms'])}\n")
    for pred in result["predictions"]:
        print(f"{pred['nutrient']}  ({pred['confidence']:.1%})")
        print(f"  Foods: {', '.join(pred['recommended_foods'][:5])}")
        if pred["recipes"]:
            print("  Recipes:")
            for r in pred["recipes"]:
                print(f"    - {r['title']}")
        else:
            print("  Recipes: none returned")
        print()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    print_report(recommend(args))
