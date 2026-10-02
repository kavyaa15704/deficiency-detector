"""
Step 2: validate data, split, train a Random Forest, evaluate, and save it.

Run from the project root:  python scripts/train_model.py

Outputs
  data/processed/train.csv, test.csv      the exact split used
  models/rf_model.joblib                  model + symptom list + class names
  models/reports/metrics.json             headline numbers
  models/reports/classification_report.txt
  models/reports/confusion_matrix.csv
  models/reports/feature_importance.csv
"""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, precision_recall_fscore_support)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

SEED = 42
TEST_SIZE = 0.20
TARGET = "deficiency"

ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = ROOT / "data" / "raw" / "symptoms_dataset.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = MODELS_DIR / "reports"


def load_and_validate() -> pd.DataFrame:
    if not RAW_CSV.exists():
        raise SystemExit(f"Dataset not found: {RAW_CSV}\nRun scripts/generate_dataset.py first.")

    df = pd.read_csv(RAW_CSV)
    print(f"Loaded {len(df)} rows, {df.shape[1] - 1} symptom columns")

    # 1. missing values
    missing = int(df.isna().sum().sum())
    print(f"Missing values: {missing}")
    if missing:
        df = df.dropna()

    # 2. symptom columns must be strictly 0/1
    symptoms = [c for c in df.columns if c != TARGET]
    bad = [c for c in symptoms if not set(df[c].unique()) <= {0, 1}]
    if bad:
        raise SystemExit(f"Non-binary values found in columns: {bad}")

    # 3. exact duplicates would leak between train and test, so drop them
    dupes = int(df.duplicated().sum())
    print(f"Exact duplicate rows dropped: {dupes}")
    df = df.drop_duplicates().reset_index(drop=True)

    print("Class balance (min/max rows per nutrient):",
          df[TARGET].value_counts().min(), "/", df[TARGET].value_counts().max())
    return df


def main() -> None:
    df = load_and_validate()
    symptoms = [c for c in df.columns if c != TARGET]
    X, y = df[symptoms], df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=SEED)
    print(f"\nTrain: {len(X_train)} rows | Test: {len(X_test)} rows")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pd.concat([X_train, y_train], axis=1).to_csv(PROCESSED_DIR / "train.csv", index=False)
    pd.concat([X_test, y_test], axis=1).to_csv(PROCESSED_DIR / "test.csv", index=False)

    model = RandomForestClassifier(
        n_estimators=300, max_depth=None, min_samples_leaf=1,
        random_state=SEED, n_jobs=-1)

    # cross-validation on the training set only (test set stays untouched)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"5-fold CV accuracy (train): {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test, preds, average="macro", zero_division=0)
    print(f"\nTest accuracy : {acc:.3f}")
    print(f"Macro precision: {prec:.3f} | recall: {rec:.3f} | F1: {f1:.3f}")

    # top-3 accuracy: is the true nutrient among the 3 most likely? (matters for the app,
    # which shows several possible deficiencies rather than one)
    proba = model.predict_proba(X_test)
    top3 = model.classes_[proba.argsort(axis=1)[:, -3:]]
    top3_acc = sum(t in row for t, row in zip(y_test, top3)) / len(y_test)
    print(f"Top-3 accuracy : {top3_acc:.3f}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = classification_report(y_test, preds, zero_division=0)
    (REPORTS_DIR / "classification_report.txt").write_text(report)
    print("\n" + report)

    labels = list(model.classes_)
    cm = pd.DataFrame(confusion_matrix(y_test, preds, labels=labels),
                      index=labels, columns=labels)
    cm.to_csv(REPORTS_DIR / "confusion_matrix.csv")

    importance = (pd.Series(model.feature_importances_, index=symptoms)
                  .sort_values(ascending=False))
    importance.to_csv(REPORTS_DIR / "feature_importance.csv", header=["importance"])
    print("Top 8 most important symptoms:")
    print(importance.head(8).round(3).to_string())

    metrics = {
        "rows_total": len(df), "rows_train": len(X_train), "rows_test": len(X_test),
        "n_symptoms": len(symptoms), "n_nutrients": len(labels),
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "test_accuracy": round(float(acc), 4),
        "test_top3_accuracy": round(float(top3_acc), 4),
        "macro_precision": round(float(prec), 4),
        "macro_recall": round(float(rec), 4),
        "macro_f1": round(float(f1), 4),
    }
    (REPORTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump({"model": model, "symptoms": symptoms, "classes": labels},
                MODELS_DIR / "rf_model.joblib")
    print(f"\nSaved model -> {MODELS_DIR / 'rf_model.joblib'}")


if __name__ == "__main__":
    main()
