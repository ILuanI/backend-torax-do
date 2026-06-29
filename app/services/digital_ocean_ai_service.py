import httpx
from fastapi import HTTPException

from app.config import settings

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

digital_ocean_ai_service = DigitalOceanAIService()
