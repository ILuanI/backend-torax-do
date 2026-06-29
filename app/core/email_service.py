from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import settings


def _email_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_STARTTLS=settings.mail_starttls,
        MAIL_SSL_TLS=settings.mail_ssl_tls,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )


async def send_email_with_attachment(
    recipient: str,
    subject: str,
    body: str,
    attachment_path: str | Path | None = None,
) -> None:
    if not all([settings.mail_username, settings.mail_password, settings.mail_from, settings.mail_server]):
        raise ValueError("SMTP settings are incomplete")

    attachments = [str(attachment_path)] if attachment_path else []
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype=MessageType.plain,
        attachments=attachments,
    )
    await FastMail(_email_config()).send_message(message)
