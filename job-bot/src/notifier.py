"""Optional email digest, sent via SMTP using credentials from the
environment (see .env.example). Never hardcode credentials in config
files that get committed to git.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailNotConfigured(Exception):
    pass


def _get_smtp_config() -> dict:
    required = ["SMTP_HOST", "SMTP_USER", "SMTP_PASS", "EMAIL_TO"]
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        raise EmailNotConfigured(f"Missing env vars: {', '.join(missing)}")
    return {
        "host": os.environ["SMTP_HOST"],
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ["SMTP_USER"],
        "password": os.environ["SMTP_PASS"],
        "to": os.environ["EMAIL_TO"],
        "from": os.environ.get("EMAIL_FROM", os.environ["SMTP_USER"]),
    }


def send_email_digest(subject: str, html_body: str) -> None:
    """Raises EmailNotConfigured if SMTP env vars aren't set -- callers
    should catch this and skip sending rather than treat it as fatal."""
    config = _get_smtp_config()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config["from"]
    msg["To"] = config["to"]
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(config["host"], config["port"]) as server:
        server.starttls()
        server.login(config["user"], config["password"])
        server.sendmail(config["from"], [config["to"]], msg.as_string())
