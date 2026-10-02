"""
Generate a symptom -> nutrient-deficiency dataset (600 rows, 15 nutrients).

Each row = one "person". Columns = 40 binary symptom flags (1 = has symptom)
plus a `deficiency` label. Symptom-to-nutrient links follow commonly cited
nutrition references; each real symptom shows up with probability P_TRUE and
random unrelated symptoms leak in with probability P_NOISE, so classes overlap
like real data (fatigue, hair loss etc. are shared across many nutrients).

Educational project data only - NOT medical advice.

Run from the project root:  python scripts/generate_dataset.py
"""
import random
from pathlib import Path

import pandas as pd

SEED = 42
ROWS_PER_NUTRIENT = 40   # 15 nutrients x 40 = 600 rows
P_TRUE = 0.75            # chance each true symptom appears
P_NOISE = 0.04           # chance each unrelated symptom appears
MIN_TRUE_SYMPTOMS = 2    # every row shows at least this many real symptoms

NUTRIENT_SYMPTOMS = {
    "Iron": ["fatigue", "weakness", "pale_skin", "dizziness", "shortness_of_breath",
             "cold_hands_feet", "brittle_nails", "hair_loss"],
    "Vitamin B12": ["fatigue", "tingling_numbness", "memory_problems", "mood_changes",
                    "tongue_soreness", "pale_skin", "difficulty_concentrating", "weakness"],
    "Vitamin D": ["bone_pain", "muscle_weakness", "fatigue", "depression",
                  "frequent_infections", "slow_wound_healing", "joint_pain", "hair_loss"],
    "Vitamin C": ["bleeding_gums", "easy_bruising", "slow_wound_healing", "frequent_infections",
                  "dry_skin", "joint_pain", "fatigue", "tooth_problems"],
    "Vitamin A": ["night_blindness", "dry_eyes", "dry_skin", "frequent_infections",
                  "vision_problems", "skin_rash", "slow_wound_healing"],
    "Vitamin E": ["muscle_weakness", "tingling_numbness", "vision_problems", "frequent_infections",
                  "difficulty_concentrating", "dry_skin", "weakness"],
    "Vitamin K": ["easy_bruising", "bleeding_gums", "slow_wound_healing", "brittle_bones",
                  "joint_pain", "weakness"],
    "Folate": ["fatigue", "mouth_ulcers", "tongue_soreness", "mood_changes",
               "difficulty_concentrating", "pale_skin", "poor_appetite", "headache"],
    "Calcium": ["muscle_cramps", "brittle_nails", "brittle_bones", "tingling_numbness",
                "tooth_problems", "irregular_heartbeat", "fatigue", "bone_pain"],
    "Magnesium": ["muscle_cramps", "irregular_heartbeat", "anxiety", "poor_sleep",
                  "headache", "fatigue", "constipation", "tingling_numbness"],
    "Potassium": ["muscle_cramps", "muscle_weakness", "irregular_heartbeat", "constipation",
                  "fatigue", "tingling_numbness", "weakness"],
    "Zinc": ["hair_loss", "loss_of_taste_smell", "slow_wound_healing", "frequent_infections",
             "skin_rash", "poor_appetite", "mouth_ulcers", "difficulty_concentrating"],
    "Iodine": ["goiter_neck_swelling", "weight_gain", "fatigue", "dry_skin",
               "cold_hands_feet", "hair_loss", "constipation", "depression"],
    "Vitamin B6": ["mood_changes", "depression", "cracked_lips", "tongue_soreness",
                   "skin_rash", "anxiety", "tingling_numbness", "poor_sleep"],
    "Omega-3": ["dry_eyes", "dry_skin", "joint_pain", "memory_problems",
                "depression", "difficulty_concentrating", "brittle_nails", "poor_sleep"],
}

ALL_SYMPTOMS = sorted({s for symptoms in NUTRIENT_SYMPTOMS.values() for s in symptoms})


def make_row(nutrient: str, rng: random.Random) -> dict:
    true_symptoms = NUTRIENT_SYMPTOMS[nutrient]
    present = {s for s in true_symptoms if rng.random() < P_TRUE}
    while len(present) < MIN_TRUE_SYMPTOMS:
        present.add(rng.choice(true_symptoms))
    for s in ALL_SYMPTOMS:
        if s not in true_symptoms and rng.random() < P_NOISE:
            present.add(s)
    row = {s: int(s in present) for s in ALL_SYMPTOMS}
    row["deficiency"] = nutrient
    return row


def main() -> None:
    rng = random.Random(SEED)
    rows = [make_row(n, rng) for n in NUTRIENT_SYMPTOMS for _ in range(ROWS_PER_NUTRIENT)]
    rng.shuffle(rows)
    df = pd.DataFrame(rows)

    out_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "symptoms_dataset.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print(f"Saved {len(df)} rows -> {out_path}")
    print(f"Symptom columns: {len(ALL_SYMPTOMS)} | Nutrients: {df['deficiency'].nunique()}")
    print("\nRows per nutrient:")
    print(df["deficiency"].value_counts().to_string())
    print(f"\nAvg symptoms per row: {df[ALL_SYMPTOMS].sum(axis=1).mean():.1f}")


if __name__ == "__main__":
    main()
