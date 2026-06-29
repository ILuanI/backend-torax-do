from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.config import settings


MODEL_PATHS = {
    "lr": settings.model_lr_path,
    "rf": settings.model_rf_path,
}


@lru_cache
def load_model(model_key: str) -> Any:
    normalized_key = model_key.lower()
    if normalized_key not in MODEL_PATHS:
        raise ValueError("Modelo no soportado. Usa 'lr' o 'rf'.")

    model_path = Path(MODEL_PATHS[normalized_key])
    if not model_path.exists():
        raise FileNotFoundError(f"No se encontro el modelo IA en: {model_path}")

    return joblib.load(model_path)


def predict(model_key: str, features: np.ndarray) -> tuple[str, float | None]:
    model = load_model(model_key)
    raw_prediction = model.predict(features)[0]
    probability: float | None = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        probability = float(max(probabilities))

    positive_values = {1, "1", True, "cancer", "positivo", "positive", "maligno"}
    result = "positivo" if raw_prediction in positive_values else "negativo"
    return result, probability
