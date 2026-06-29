from fastapi import APIRouter, File, Form, UploadFile, status
from pydantic import BaseModel

from app.core.modelos_ia.load import predict
from app.core.modelos_ia.preprocess import preprocess_radiografia
from app.core.file_storage import file_storage

router = APIRouter(prefix="/escaner", tags=["escaner"])

class ModeloInfo(BaseModel):
    value: str
    label: str
    description: str

class ModelosDisponibles(BaseModel):
    available_models: list[str]
    model_options: list[ModeloInfo]

class AnalisisResultado(BaseModel):
    prediction: str
    probability_cancer: float
    probability_normal: float
    risk_level: str
    model_used: str
    model_display_name: str
    model_version: str
    confidence_percent: float
    recommendation: str
    disclaimer: str

@router.get("/modelos", response_model=ModelosDisponibles)
async def get_modelos():
    return ModelosDisponibles(
        available_models=["logistic_regression", "random_forest"],
        model_options=[
            ModeloInfo(value="logistic_regression", label="Reg. Logística", description="Rápido e interpretable"),
            ModeloInfo(value="random_forest", label="Random Forest", description="Alta precisión (50 árboles)"),
        ]
    )

@router.post("/analizar", response_model=AnalisisResultado)
async def analizar_imagen(
    file: UploadFile = File(...),
    model_type: str = Form("logistic_regression")
):
    original_path = await file_storage.save_upload(file)
    processed_path = file_storage.processed_image_path()
    
    # Preprocesar
    features = preprocess_radiografia(original_path, processed_path)
    
    # Mapeo de nombre de modelo
    modelo_interno = "rf" if model_type == "random_forest" else "lr"
    
    # Predecir
    result, probability = predict(modelo_interno, features)
    
    # Si probability es None, simulamos una probabilidad basada en el resultado
    if probability is None:
        probability = 0.85 if result == "positivo" else 0.15

    prob_cancer = probability
    prob_normal = 1.0 - probability

    if result == "positivo":
        risk_level = "alto" if prob_cancer >= 0.7 else "moderado"
        pred_label = "cancer_detected" if prob_cancer >= 0.7 else "review_recommended"
        rec = "Se recomienda evaluación oncológica urgente y confirmación histopatológica."
    else:
        risk_level = "bajo"
        pred_label = "no_cancer" if prob_normal >= 0.8 else "low_suspicion"
        rec = "Hallazgos dentro de parámetros normales. Mantener control preventivo."

    return AnalisisResultado(
        prediction=pred_label,
        probability_cancer=prob_cancer,
        probability_normal=prob_normal,
        risk_level=risk_level,
        model_used=model_type,
        model_display_name="Random Forest" if model_type == "random_forest" else "Regresión Logística",
        model_version="1.0",
        confidence_percent=max(prob_cancer, prob_normal) * 100.0,
        recommendation=rec,
        disclaimer="Este análisis es una herramienta de apoyo y NO sustituye el diagnóstico médico profesional."
    )
