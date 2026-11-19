from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "spam.csv"
MODEL_PATH = BASE_DIR / "spam_model.pkl"
VECTORIZER_PATH = BASE_DIR / "vectorizer.pkl"


def load_dataset(file_path: Path) -> pd.DataFrame:
    dataset = pd.read_csv(file_path, encoding="latin-1")
    normalized_columns = {column.strip().lower(): column for column in dataset.columns}

    if {"label", "text"}.issubset(normalized_columns):
        dataset = dataset[
            [normalized_columns["label"], normalized_columns["text"]]
        ].rename(
            columns={
                normalized_columns["label"]: "label",
                normalized_columns["text"]: "text",
            }
        )
    elif {"v1", "v2"}.issubset(normalized_columns):
        dataset = dataset[[normalized_columns["v1"], normalized_columns["v2"]]].rename(
            columns={normalized_columns["v1"]: "label", normalized_columns["v2"]: "text"}
        )
    else:
        raise ValueError(
            "spam.csv must contain either 'label' and 'text' columns or the common 'v1' and 'v2' columns."
        )

    dataset["label"] = dataset["label"].astype(str).str.strip().str.lower()
    dataset["text"] = dataset["text"].astype(str).str.strip()

    dataset = dataset[dataset["label"].isin(["ham", "spam"])]
    dataset = dataset[dataset["text"] != ""]
    dataset = dataset.drop_duplicates().reset_index(drop=True)

    if dataset.empty:
        raise ValueError("The dataset is empty after cleaning.")

    return dataset


def train() -> None:
    dataset = load_dataset(DATA_PATH)
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        sublinear_tf=True,
    )
    model = LogisticRegression(max_iter=2000)

    cross_validation = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    evaluation_pipeline = make_pipeline(vectorizer, model)
    scores = cross_val_score(
        evaluation_pipeline,
        dataset["text"],
        dataset["label"],
        cv=cross_validation,
        scoring="accuracy",
    )

    all_vectors = vectorizer.fit_transform(dataset["text"])
    model.fit(all_vectors, dataset["label"])

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print(f"Samples: {len(dataset)}")
    print("Label distribution:")
    print(dataset["label"].value_counts().to_string())
    print(f"Cross-validated accuracy: {scores.mean():.2%} (+/- {scores.std():.2%})")
    print(f"Saved model to: {MODEL_PATH}")
    print(f"Saved vectorizer to: {VECTORIZER_PATH}")


if __name__ == "__main__":
    train()
