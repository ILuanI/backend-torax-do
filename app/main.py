from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, citas, datos_clinicos, disponibilidad, escaner, medicos, pacientes, predicciones, recomendaciones, roles_permisos, users
from app.config import settings


app = FastAPI(
    title="Thorax Cancer Detection API",
    description="API medica para gestion de citas, pacientes y prediccion de cancer de torax.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(roles_permisos.router, prefix="/api/v1")
app.include_router(medicos.router, prefix="/api/v1")
app.include_router(pacientes.router, prefix="/api/v1")
app.include_router(disponibilidad.router, prefix="/api/v1")
app.include_router(citas.router, prefix="/api/v1")
app.include_router(datos_clinicos.router, prefix="/api/v1")
app.include_router(predicciones.router, prefix="/api/v1")
app.include_router(recomendaciones.router, prefix="/api/v1")
app.include_router(escaner.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
