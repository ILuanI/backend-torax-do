import httpx
from fastapi import HTTPException

from app.config import settings
from app.models.dato_clinico import DatoClinico
from app.models.prediccion import Prediccion

DEFAULT_SYSTEM_PROMPT = """
Eres un asistente experto en análisis de negocio, datos y software.
Responde de forma clara, útil y accionable.
"""

class DigitalOceanAIService:
    async def chat(self, prompt: str, system_prompt: str | None = None) -> dict:
        url = f"{settings.do_ai_base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.do_ai_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.do_ai_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt or DEFAULT_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": settings.do_ai_temperature,
            "max_completion_tokens": settings.do_ai_max_completion_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.do_ai_timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)

            if response.status_code >= 400:
                raise HTTPException(
                    status_code=502,
                    detail={
                        "message": "Error al consumir DigitalOcean Inference",
                        "status_code": response.status_code,
                        "response": response.text,
                    },
                )

            data = response.json()
            answer = data["choices"][0]["message"]["content"]

            return {
                "answer": answer,
                "model": data.get("model", settings.do_ai_model),
                "usage": data.get("usage"),
            }
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Timeout al consumir DigitalOcean Inference")
        except KeyError:
            raise HTTPException(status_code=502, detail="La respuesta de DigitalOcean no tuvo el formato esperado")
        except httpx.RequestError as error:
            raise HTTPException(status_code=502, detail=f"Error de conexión con DigitalOcean Inference: {str(error)}")

    async def generate_recommendation(self, prediccion: Prediccion, dato_clinico: DatoClinico | None) -> str:
        prompt = self._build_prompt(prediccion, dato_clinico)
        try:
            result = await self.chat(prompt=prompt)
            return result["answer"]
        except Exception:
            return "No fue posible generar recomendaciones."

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

digital_ocean_ai_service = DigitalOceanAIService()
