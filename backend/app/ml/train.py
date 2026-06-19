import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")
MODEL_PATH = os.path.join(MODEL_DIR, "match_model.joblib")
TRAIN_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "data", "train.csv")


def prepare_text(cv_text: str, jd_text: str) -> str:
    return f"{str(cv_text).strip()} [SEP] {str(jd_text).strip()}"


def train():
    # NOTE: This is the primary training script for the runtime model.
    # Also see ml_pipeline/train_pipeline.py (classification variant) — it saves
    # to a separate classifier path to avoid overwriting this regression model.
    os.makedirs(MODEL_DIR, exist_ok=True)

    df = pd.read_csv(TRAIN_CSV)
    df = df.dropna(subset=["cv_text", "job_desc", "match_score"])

    df["combined_text"] = df.apply(
        lambda row: prepare_text(row["cv_text"], row["job_desc"]), axis=1
    )

    X = df["combined_text"].tolist()
    y = df["match_score"].astype(float).tolist()

    vectorizer = TfidfVectorizer(max_features=20000, ngram_range=(1, 2))
    X_vec = vectorizer.fit_transform(X)

    X_train, X_val, y_train, y_val = train_test_split(
        X_vec, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_val)
    mse = mean_squared_error(y_val, preds)
    print(f"Validation MSE: {mse:.4f}")

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(model, MODEL_PATH)
    print("Saved vectorizer and model to:", MODEL_DIR)


if __name__ == "__main__":
    train()
