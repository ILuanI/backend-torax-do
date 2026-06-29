import google.generativeai as genai

from app.config import settings
from app.models.dato_clinico import DatoClinico
from app.models.prediccion import Prediccion


class GeminiService:
    def __init__(self) -> None:
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)

    async def generate_recommendation(self, prediccion: Prediccion, dato_clinico: DatoClinico | None) -> str:
        if not settings.gemini_api_key:
            return "Configure GEMINI_API_KEY para generar recomendaciones personalizadas."

        prompt = self._build_prompt(prediccion, dato_clinico)
        model = genai.GenerativeModel("gemini-flash-latest")
        response = await model.generate_content_async(prompt)
        return response.text or "No fue posible generar recomendaciones."

    def _build_prompt(self, prediccion: Prediccion, dato_clinico: DatoClinico | None) -> str:
        clinical_data = "No se registraron datos clinicos asociados."
        if dato_clinico:
            clinical_data = (
                f"Edad: {dato_clinico.edad}\n"
                f"Fumador: {dato_clinico.fumador}\n"
                f"Paquetes anio: {dato_clinico.paquetes_anio}\n"
                f"Exposicion humo: {dato_clinico.exposicion_humo}\n"
                f"Exposicion asbesto: {dato_clinico.exposicion_asbesto}\n"
                f"Exposicion radon: {dato_clinico.exposicion_radon}\n"
                f"Antecedente familiar cancer: {dato_clinico.antecedente_familiar_cancer}\n"
                f"Tos cronica: {dato_clinico.tos_cronica}\n"
                f"Hemoptisis: {dato_clinico.hemoptisis}\n"
                f"Disnea: {dato_clinico.disnea}\n"
                f"Dolor toracico: {dato_clinico.dolor_toracico}\n"
                f"Perdida peso: {dato_clinico.perdida_peso}\n"
                f"Fatiga: {dato_clinico.fatiga}\n"
                f"Ronquera: {dato_clinico.ronquera}\n"
                f"Infecciones recurrentes: {dato_clinico.infecciones_recurrentes}\n"
                f"Observaciones: {dato_clinico.observaciones}"
            )

        return (
            "Actua como asistente medico. Genera recomendaciones claras y prudentes para un paciente "
            "evaluado por posible cancer de torax. No des diagnosticos definitivos; indica seguimiento "
            "con medico especialista.\n\n"
            f"Clase predicha: {prediccion.clase_predicha}\n"
            f"Nivel de riesgo: {prediccion.nivel_riesgo}\n"
            f"Probabilidad del modelo: {prediccion.probabilidad}\n"
            f"Modelo usado: {prediccion.modelo_utilizado}\n\n"
            f"Datos clinicos:\n{clinical_data}"
        )


gemini_service = GeminiService()
