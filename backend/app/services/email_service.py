import smtplib
import socket
from email.mime.text import MIMEText
from pydantic import EmailStr
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def is_online(host="8.8.8.8", port=53, timeout=3) -> bool:
    """
    Check internet connectivity by trying to connect to a known host.
    Default is Google's public DNS server.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        logger.warning(f"Internet connectivity check failed: {ex}")
        return False

def send_verification_email(user_email: EmailStr, username: str, verification_token: str):
    if not settings.SMTP_HOST or not settings.SMTP_SENDER_EMAIL:
        logger.warning("SMTP settings not configured. Skipping email verification.")
        return False

    if not is_online():
        logger.warning("No internet connection. Skipping email verification.")
        return False

    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

    subject = "Verify your email address"
    body = f"""
    Hi {username},

    Please click the following link to verify your email address:
    {verification_link}

    If you did not request this, please ignore this email.

    Thanks,
    The Team
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = settings.SMTP_SENDER_EMAIL
    msg['To'] = user_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.starttls() # Upgrade the connection to encrypted TLS
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_SENDER_EMAIL, [user_email], msg.as_string())
            logger.info(f"Verification email sent to {user_email}")
            return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: Failed to send email to {user_email}. Error: {e}")
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"SMTP Server Disconnected: Failed to send email to {user_email}. Error: {e}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP Error: Failed to send email to {user_email}. Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending email to {user_email}. Error: {e}")

    return False
