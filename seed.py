import asyncio
from datetime import date, datetime, timedelta, time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.disponibilidad import DisponibilidadMedica
from app.models.cita import Cita
from app.models.dato_clinico import DatoClinico

async def seed():
    async with AsyncSessionLocal() as session:
        print("Limpiando tablas existentes...")
        await session.execute(text("TRUNCATE TABLE citas, datos_clinicos, disponibilidad_medica, medicos, usuarios, rol_permisos, permisos, roles, pacientes, recomendaciones, predicciones RESTART IDENTITY CASCADE;"))
        await session.commit()
        
        print("Creando Roles y Permisos...")
        p_all = Permiso(codigo="all", descripcion="Acceso total")
        p_read = Permiso(codigo="read", descripcion="Solo lectura")
        session.add_all([p_all, p_read])
        await session.flush()
        
        r_admin = Rol(nombre="admin", descripcion="Administrador del sistema", permisos=[p_all])
        r_medico = Rol(nombre="especialista", descripcion="Médico Especialista")
        r_secre = Rol(nombre="secretaria", descripcion="Personal administrativo")
        session.add_all([r_admin, r_medico, r_secre])
        await session.flush()
        
        print("Creando Usuarios y Médicos...")
        admin = Usuario(
            rol_id=r_admin.id,
            nombre_completo="Admin Principal",
            email="admin@example.com",
            username="admin",
            password_hash=get_password_hash("admin123"),
            activo=True
        )
        medico_user = Usuario(
            rol_id=r_medico.id,
            nombre_completo="Dr. Carlos Mendez",
            email="medico@example.com",
            username="medico",
            password_hash=get_password_hash("medico123"),
            activo=True
        )
        secre_user = Usuario(
            rol_id=r_secre.id,
            nombre_completo="Ana Torres (Secretaría)",
            email="secretaria@example.com",
            username="secretaria",
            password_hash=get_password_hash("secre123"),
            activo=True
        )
        session.add_all([admin, medico_user, secre_user])
        await session.flush()
        
        medico_profile = Medico(
            usuario_id=medico_user.id,
            cmp="123456",
            especialidad="Neumologia"
        )
        session.add(medico_profile)
        await session.flush()
        
        print("Creando Disponibilidad Médica...")
        hoy = datetime.now()
        for i in range(5): # Monday to Friday
            disp = DisponibilidadMedica(
                medico_id=medico_profile.id,
                fecha=hoy.date() + timedelta(days=i),
                hora_inicio=time(8, 0),
                hora_fin=time(17, 0),
                disponible=True
            )
            session.add(disp)
        
        print("Creando Pacientes y Citas...")
        p1 = Paciente(
            nombres="Juan",
            apellidos="Pérez",
            dni="11112222",
            fecha_nacimiento=date(1980, 5, 20),
            sexo="M",
            email="juan.perez@mail.com"
        )
        p2 = Paciente(
            nombres="María",
            apellidos="García",
            dni="33334444",
            fecha_nacimiento=date(1995, 10, 12),
            sexo="F",
            email="maria.garcia@mail.com"
        )
        session.add_all([p1, p2])
        await session.flush()
        
        # Historial (Datos clínicos)
        dc1 = DatoClinico(
            paciente_id=p1.id,
            edad=46,
            fumador=True,
            tos_cronica=True,
            disnea=False,
            observaciones="Paciente presenta tos frecuente desde hace 2 meses."
        )
        session.add(dc1)
        
        # Cita pendiente para hoy
        hoy = datetime.now()
        c1 = Cita(
            paciente_id=p1.id,
            medico_id=medico_profile.id,
            fecha_cita=hoy + timedelta(hours=2),
            motivo_consulta="Revisión general de tórax",
            estado="pendiente"
        )
        session.add(c1)
        
        await session.commit()
        print("[OK] Base de datos rellenada exitosamente!")
        print("Credenciales:")
        print("  Admin: admin@example.com / admin123")
        print("  Médico: medico@example.com / medico123")
        print("  Secretaria: secretaria@example.com / secre123")

if __name__ == "__main__":
    asyncio.run(seed())
