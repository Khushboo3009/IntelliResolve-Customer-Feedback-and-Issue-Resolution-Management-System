import os
import smtplib

from email.message import EmailMessage


# ============================================================
# SMTP CONFIGURATION
# ============================================================

SMTP_HOST = os.getenv("SMTP_HOST", "").strip()

SMTP_PORT = int(
    os.getenv("SMTP_PORT", "587")
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    "",
).strip()

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    "",
)

SMTP_FROM_EMAIL = os.getenv(
    "SMTP_FROM_EMAIL",
    "",
).strip()


SMTP_USE_TLS = (
    os.getenv(
        "SMTP_USE_TLS",
        "true",
    ).strip().lower()
    in {"1", "true", "yes", "on"}
)


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(
    to_email,
    subject,
    body,
):

    to_email = str(to_email or "").strip()
    subject = str(subject or "").strip()
    body = str(body or "")

    if not to_email:
        raise ValueError(
            "Recipient email is required."
        )

    if not subject:
        raise ValueError(
            "Email subject is required."
        )

    if not SMTP_HOST:
        raise RuntimeError(
            "SMTP_HOST is not configured."
        )

    if not SMTP_USERNAME:
        raise RuntimeError(
            "SMTP_USERNAME is not configured."
        )

    if not SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP_PASSWORD is not configured."
        )

    sender = SMTP_FROM_EMAIL or SMTP_USERNAME

    message = EmailMessage()

    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=30,
    ) as server:

        server.ehlo()

        if SMTP_USE_TLS:
            server.starttls()
            server.ehlo()

        server.login(
            SMTP_USERNAME,
            SMTP_PASSWORD,
        )

        server.send_message(message)

    return True