"""initial medical schema

Revision ID: 20260614_0001
Revises:
Create Date: 2026-06-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260614_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(length=50), nullable=False, unique=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
    )

    op.create_table(
        "permisos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(length=100), nullable=False, unique=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
    )

    op.create_table(
        "rol_permisos",
        sa.Column("rol_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permiso_id", sa.Integer(), sa.ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False, unique=True),
        sa.Column("email", sa.String(length=120), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("nombre_completo", sa.String(length=150), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("TRUE"), nullable=True),
        sa.Column("rol_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
    )

    op.create_table(
        "pacientes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dni", sa.String(length=20), nullable=True, unique=True),
        sa.Column("nombres", sa.String(length=100), nullable=False),
        sa.Column("apellidos", sa.String(length=100), nullable=False),
        sa.Column("fecha_nacimiento", sa.Date(), nullable=True),
        sa.Column("sexo", sa.String(length=20), nullable=True),
        sa.Column("telefono", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("direccion", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
    )

    op.create_table(
        "medicos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True, unique=True),
        sa.Column("cmp", sa.String(length=30), nullable=True, unique=True),
        sa.Column("especialidad", sa.String(length=100), server_default="Neumologia", nullable=True),
    )

    op.create_table(
        "disponibilidad_medica",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("medico_id", sa.Integer(), sa.ForeignKey("medicos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fin", sa.Time(), nullable=False),
        sa.Column("disponible", sa.Boolean(), server_default=sa.text("TRUE"), nullable=True),
        sa.CheckConstraint("hora_fin > hora_inicio", name="disponibilidad_medica_hora_check"),
    )

    op.create_table(
        "citas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("paciente_id", sa.Integer(), sa.ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("medico_id", sa.Integer(), sa.ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("disponibilidad_id", sa.Integer(), sa.ForeignKey("disponibilidad_medica.id", ondelete="SET NULL"), nullable=True),
        sa.Column("fecha_cita", sa.DateTime(), nullable=False),
        sa.Column("estado", sa.String(length=30), server_default="pendiente", nullable=True),
        sa.Column("motivo_consulta", sa.Text(), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("estado IN ('pendiente', 'atendida', 'cancelada')", name="citas_estado_check"),
    )

    op.create_table(
        "datos_clinicos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("paciente_id", sa.Integer(), sa.ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("medico_id", sa.Integer(), sa.ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("edad", sa.Integer(), nullable=True),
        sa.Column("fumador", sa.Boolean(), nullable=True),
        sa.Column("paquetes_anio", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("exposicion_humo", sa.Boolean(), nullable=True),
        sa.Column("exposicion_asbesto", sa.Boolean(), nullable=True),
        sa.Column("exposicion_radon", sa.Boolean(), nullable=True),
        sa.Column("antecedente_familiar_cancer", sa.Boolean(), nullable=True),
        sa.Column("tos_cronica", sa.Boolean(), nullable=True),
        sa.Column("hemoptisis", sa.Boolean(), nullable=True),
        sa.Column("disnea", sa.Boolean(), nullable=True),
        sa.Column("dolor_toracico", sa.Boolean(), nullable=True),
        sa.Column("perdida_peso", sa.Boolean(), nullable=True),
        sa.Column("fatiga", sa.Boolean(), nullable=True),
        sa.Column("ronquera", sa.Boolean(), nullable=True),
        sa.Column("infecciones_recurrentes", sa.Boolean(), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
    )

    op.create_table(
        "predicciones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("paciente_id", sa.Integer(), sa.ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("medico_id", sa.Integer(), sa.ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("datos_clinicos_id", sa.Integer(), sa.ForeignKey("datos_clinicos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("modelo_utilizado", sa.String(length=20), nullable=False),
        sa.Column("probabilidad", sa.Numeric(precision=6, scale=4), nullable=False),
        sa.Column("clase_predicha", sa.String(length=50), nullable=False),
        sa.Column("nivel_riesgo", sa.String(length=20), nullable=False),
        sa.Column("imagen_original_path", sa.Text(), nullable=True),
        sa.Column("imagen_procesada_path", sa.Text(), nullable=True),
        sa.Column("fecha_prediccion", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
    )

    op.create_table(
        "recomendaciones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("prediccion_id", sa.Integer(), sa.ForeignKey("predicciones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("paciente_id", sa.Integer(), sa.ForeignKey("pacientes.id", ondelete="CASCADE"), nullable=True),
        sa.Column("medico_id", sa.Integer(), sa.ForeignKey("medicos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("contenido_recomendacion", sa.Text(), nullable=False),
        sa.Column("reporte_pdf_path", sa.Text(), nullable=True),
        sa.Column("email_enviado_a", sa.String(length=100), nullable=True),
        sa.Column("email_enviado", sa.Boolean(), server_default=sa.text("FALSE"), nullable=True),
        sa.Column("fecha_envio", sa.DateTime(), nullable=True),
        sa.Column("fecha_generacion", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
    )

    op.create_table(
        "email_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recomendacion_id", sa.Integer(), sa.ForeignKey("recomendaciones.id", ondelete="CASCADE"), nullable=True),
        sa.Column("destinatario", sa.String(length=120), nullable=True),
        sa.Column("estado", sa.String(length=50), nullable=True),
        sa.Column("mensaje", sa.Text(), nullable=True),
        sa.Column("fecha_evento", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
    )

    op.create_index("idx_citas_paciente", "citas", ["paciente_id"])
    op.create_index("idx_citas_medico", "citas", ["medico_id"])
    op.create_index("idx_citas_fecha", "citas", ["fecha_cita"])
    op.create_index("idx_dc_paciente", "datos_clinicos", ["paciente_id"])
    op.create_index("idx_pred_paciente", "predicciones", ["paciente_id"])
    op.create_index("idx_pred_medico", "predicciones", ["medico_id"])
    op.create_index("idx_pred_fecha", "predicciones", ["fecha_prediccion"])
    op.create_index("idx_rec_paciente", "recomendaciones", ["paciente_id"])
    op.create_index("idx_rec_medico", "recomendaciones", ["medico_id"])

    op.execute(
        """
        INSERT INTO roles(nombre, descripcion) VALUES
        ('administrador', 'Acceso total'),
        ('secretaria', 'Gestion de pacientes y citas'),
        ('medico', 'Atencion y predicciones')
        """
    )

    op.execute(
        """
        INSERT INTO permisos(codigo, descripcion) VALUES
        ('usuarios.manage', 'Gestion usuarios'),
        ('roles.manage', 'Gestion roles'),
        ('pacientes.create', 'Crear paciente'),
        ('pacientes.read', 'Ver paciente'),
        ('pacientes.update', 'Editar paciente'),
        ('pacientes.delete', 'Eliminar paciente'),
        ('citas.create', 'Crear cita'),
        ('citas.read', 'Ver cita'),
        ('citas.update', 'Editar cita'),
        ('citas.delete', 'Eliminar cita'),
        ('disponibilidad.manage', 'Gestion disponibilidad'),
        ('datos_clinicos.create', 'Registrar datos clinicos'),
        ('datos_clinicos.read', 'Ver datos clinicos'),
        ('predicciones.create', 'Generar prediccion'),
        ('predicciones.read', 'Ver predicciones'),
        ('recomendaciones.create', 'Generar recomendaciones'),
        ('recomendaciones.read', 'Ver recomendaciones'),
        ('citas.atender', 'Atender cita'),
        ('disponibilidad.read', 'Ver disponibilidad de medicos')
        """
    )

    op.execute(
        """
        INSERT INTO rol_permisos
        SELECT r.id, p.id
        FROM roles r CROSS JOIN permisos p
        WHERE r.nombre = 'administrador'
        """
    )

    op.execute(
        """
        INSERT INTO rol_permisos
        SELECT r.id, p.id
        FROM roles r, permisos p
        WHERE r.nombre = 'secretaria'
        AND p.codigo IN (
            'pacientes.create', 'pacientes.read', 'pacientes.update', 'pacientes.delete',
            'citas.create', 'citas.read', 'citas.update', 'citas.delete',
            'disponibilidad.read'
        )
        """
    )

    op.execute(
        """
        INSERT INTO rol_permisos
        SELECT r.id, p.id
        FROM roles r, permisos p
        WHERE r.nombre = 'medico'
        AND p.codigo IN (
            'pacientes.read',
            'citas.read', 'citas.atender',
            'datos_clinicos.create', 'datos_clinicos.read',
            'predicciones.create', 'predicciones.read',
            'recomendaciones.create', 'recomendaciones.read',
            'disponibilidad.read'
        )
        """
    )

    op.execute(
        """
        INSERT INTO usuarios(username, email, password_hash, nombre_completo, rol_id)
        VALUES
        (
            'admin',
            'admin@example.com',
            '$2b$12$EpMklzJ3IiXyJUAqdhkoe.ds7ZNR2rAAgz17RHaS2gTv5GQNOSTbi',
            'Administrador General',
            (SELECT id FROM roles WHERE nombre = 'administrador')
        ),
        (
            'secretaria1',
            'secretaria@example.com',
            '$2b$12$Xx7FCAx5G4lDFwW5Diz6euY3jN9KPJH4hMDzfdEvWmhiOgasx9oDy',
            'Secretaria Demo',
            (SELECT id FROM roles WHERE nombre = 'secretaria')
        ),
        (
            'medico1',
            'medico@example.com',
            '$2b$12$G3a.CROh4GHpzXwVWPcFweocGW6gNbhPuxpb06W/NmEBqIpqyNU36',
            'Dr. Carlos Ramirez',
            (SELECT id FROM roles WHERE nombre = 'medico')
        )
        """
    )

    op.execute(
        """
        INSERT INTO medicos(usuario_id, cmp, especialidad)
        VALUES (
            (SELECT id FROM usuarios WHERE username = 'medico1'),
            'CMP-123456',
            'Neumologia'
        )
        """
    )

    op.execute(
        """
        INSERT INTO pacientes(dni, nombres, apellidos, fecha_nacimiento, sexo, telefono, email)
        VALUES (
            '12345678',
            'Juan',
            'Perez',
            '1985-05-10',
            'Masculino',
            '999999999',
            'juan@example.com'
        )
        """
    )

    op.execute(
        """
        INSERT INTO disponibilidad_medica(medico_id, fecha, hora_inicio, hora_fin)
        VALUES
        ((SELECT id FROM medicos LIMIT 1), CURRENT_DATE + 1, '08:00', '09:00'),
        ((SELECT id FROM medicos LIMIT 1), CURRENT_DATE + 1, '09:00', '10:00'),
        ((SELECT id FROM medicos LIMIT 1), CURRENT_DATE + 2, '14:00', '15:00')
        """
    )

    op.execute(
        """
        INSERT INTO citas(paciente_id, medico_id, fecha_cita, estado, motivo_consulta)
        VALUES (
            (SELECT id FROM pacientes LIMIT 1),
            (SELECT id FROM medicos LIMIT 1),
            CURRENT_TIMESTAMP + INTERVAL '1 day',
            'pendiente',
            'Evaluacion preventiva de cancer de torax'
        )
        """
    )

    op.execute(
        """
        COMMENT ON TABLE predicciones IS
        'Resultados generados por modelos LR/RF luego del preprocesamiento de radiografias 64x64 en escala de grises.'
        """
    )
    op.execute(
        """
        COMMENT ON TABLE recomendaciones IS
        'Recomendaciones generadas mediante Gemini API. Incluye PDF y estado de envio por correo.'
        """
    )


def downgrade() -> None:
    op.drop_index("idx_rec_medico", table_name="recomendaciones")
    op.drop_index("idx_rec_paciente", table_name="recomendaciones")
    op.drop_index("idx_pred_fecha", table_name="predicciones")
    op.drop_index("idx_pred_medico", table_name="predicciones")
    op.drop_index("idx_pred_paciente", table_name="predicciones")
    op.drop_index("idx_dc_paciente", table_name="datos_clinicos")
    op.drop_index("idx_citas_fecha", table_name="citas")
    op.drop_index("idx_citas_medico", table_name="citas")
    op.drop_index("idx_citas_paciente", table_name="citas")

    op.drop_table("email_logs")
    op.drop_table("recomendaciones")
    op.drop_table("predicciones")
    op.drop_table("datos_clinicos")
    op.drop_table("citas")
    op.drop_table("disponibilidad_medica")
    op.drop_table("medicos")
    op.drop_table("pacientes")
    op.drop_table("usuarios")
    op.drop_table("rol_permisos")
    op.drop_table("permisos")
    op.drop_table("roles")
