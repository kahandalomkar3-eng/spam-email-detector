from __future__ import annotations

import csv
import io
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import joblib
from flask import Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"
MODEL_PATH = BASE_DIR / "spam_model.pkl"
VECTORIZER_PATH = BASE_DIR / "vectorizer.pkl"
HISTORY_DB_PATH = Path(os.getenv("SPAM_HISTORY_DB", BASE_DIR / "prediction_history.db"))


def load_artifacts() -> tuple[object, object]:
    missing_files = [
        path.name for path in (MODEL_PATH, VECTORIZER_PATH) if not path.exists()
    ]
    if missing_files:
        missing = ", ".join(missing_files)
        raise FileNotFoundError(
            f"Missing trained artifacts: {missing}. Run model/train_model.py first."
        )

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    return model, vectorizer


def get_db_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(HISTORY_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_history_store() -> None:
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS email_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                label TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_history_entry(message: str, label: str, confidence: float) -> int:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_db_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO email_history (message, label, confidence, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (message, label, confidence, created_at),
        )
        return int(cursor.lastrowid)


def fetch_history_entries() -> list[dict[str, object]]:
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, message, label, confidence, created_at
            FROM email_history
            ORDER BY id DESC
            """
        ).fetchall()

    entries: list[dict[str, object]] = []
    for row in rows:
        entries.append(
            {
                "id": int(row["id"]),
                "message": str(row["message"]),
                "label": str(row["label"]),
                "confidence": float(row["confidence"]),
                "created_at": str(row["created_at"]),
            }
        )

    return entries


def build_history_export(history_entries: list[dict[str, object]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "message", "label", "confidence", "created_at"])

    for entry in reversed(history_entries):
        writer.writerow(
            [
                entry["id"],
                entry["message"],
                entry["label"],
                f"{float(entry['confidence']):.6f}",
                entry["created_at"],
            ]
        )

    return buffer.getvalue()


app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

init_history_store()
model, vectorizer = load_artifacts()


@app.get("/")
def index() -> object:
    return send_from_directory(app.static_folder, "index.html")


@app.get("/history")
def history_page() -> object:
    return send_from_directory(app.static_folder, "history.html")


@app.get("/health")
def health() -> object:
    return jsonify({"status": "ok", "model_loaded": True})


@app.post("/predict")
def predict() -> object:
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please provide an email message to analyze."}), 400

    features = vectorizer.transform([message])
    raw_prediction = str(model.predict(features)[0]).strip().lower()
    probabilities = model.predict_proba(features)[0]
    confidence = float(probabilities.max())

    if raw_prediction not in {"ham", "spam"}:
        raw_prediction = "spam" if raw_prediction in {"1", "true"} else "ham"

    history_id = save_history_entry(message, raw_prediction, confidence)

    return jsonify(
        {
            "label": raw_prediction,
            "confidence": confidence,
            "message": message,
            "history_id": history_id,
        }
    )


@app.get("/api/history")
def get_history() -> object:
    history_entries = fetch_history_entries()
    spam_count = sum(1 for entry in history_entries if entry["label"] == "spam")
    ham_count = sum(1 for entry in history_entries if entry["label"] == "ham")

    return jsonify(
        {
            "items": history_entries,
            "total": len(history_entries),
            "spam_count": spam_count,
            "ham_count": ham_count,
        }
    )


@app.get("/api/history/export")
def export_history() -> object:
    history_entries = fetch_history_entries()
    csv_content = build_history_export(history_entries)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f'attachment; filename="email-history-{timestamp}.csv"'
    )
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
