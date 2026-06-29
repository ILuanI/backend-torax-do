ADMIN_ROLE = "admin"
SECRETARY_ROLE = "secretaria"
DOCTOR_ROLE = "especialista"

# Aliases from legacy seed/migrations (e.g. initial schema used "medico", "administrador")
ROLE_ALIASES: dict[str, str] = {
    "medico": DOCTOR_ROLE,
    "administrador": ADMIN_ROLE,
}


def normalize_role(role: str | None) -> str | None:
    if role is None:
        return None
    return ROLE_ALIASES.get(role, role)

MANAGE_USERS = "usuarios.manage"
MANAGE_ROLES = "roles.manage"
MANAGE_PATIENTS = "pacientes.create"
MANAGE_APPOINTMENTS = "citas.create"
READ_AVAILABILITY = "disponibilidad.read"
ATTEND_APPOINTMENTS = "citas.atender"
MANAGE_CLINICAL_DATA = "datos_clinicos.create"
CREATE_PREDICTIONS = "predicciones.create"
CREATE_RECOMMENDATIONS = "recomendaciones.create"
