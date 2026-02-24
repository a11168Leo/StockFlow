import smtplib
from email.message import EmailMessage

from backend.core.config import get_settings


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    settings = get_settings()

    subject = "StockFlow - Redefinicao de senha"
    body = (
        "Recebemos uma solicitacao para redefinir sua senha.\n\n"
        f"Clique no link para continuar: {reset_link}\n\n"
        "Se voce nao solicitou essa redefinicao, ignore este email."
    )

    if not settings.smtp_host:
        # Fallback para ambiente local sem SMTP configurado.
        print(f"[email-dev] reset password para {to_email}: {reset_link}")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)
