from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.core.file_storage import file_storage
from app.models.paciente import Paciente
from app.models.prediccion import Prediccion


def generate_recommendation_pdf(
    paciente: Paciente,
    prediccion: Prediccion,
    recommendation_text: str,
    output_path: str | Path | None = None,
) -> Path:
    path = Path(output_path) if output_path else file_storage.report_path()
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(str(path), pagesize=letter)
    story = [
        Paragraph("Reporte medico de prediccion", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Paciente: {paciente.nombres} {paciente.apellidos}", styles["Normal"]),
        Paragraph(f"DNI: {paciente.dni}", styles["Normal"]),
        Paragraph(f"Clase predicha: {prediccion.clase_predicha}", styles["Normal"]),
        Paragraph(f"Nivel de riesgo: {prediccion.nivel_riesgo}", styles["Normal"]),
        Paragraph(f"Modelo: {prediccion.modelo_utilizado.upper()}", styles["Normal"]),
        Paragraph(f"Probabilidad: {prediccion.probabilidad}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Recomendaciones", styles["Heading2"]),
        Paragraph(recommendation_text.replace("\n", "<br/>"), styles["BodyText"]),
    ]
    document.build(story)
    return path
