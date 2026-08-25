"""Email service for sending welcome, verification, and reset emails."""
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from app.core.config import settings


class EmailService:
    def __init__(self):
        self.smtp_host = getattr(settings, "SMTP_HOST", None)
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_user = getattr(settings, "SMTP_USER", None)
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", None)
        self.from_email = getattr(settings, "EMAILS_FROM_EMAIL", self.smtp_user or "noreply@researchai.com")
        self.from_name = getattr(settings, "EMAILS_FROM_NAME", "ResearchAI")

    def is_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

    async def send_welcome_email(self, to_email: str, name: Optional[str] = None):
        """Send a rich welcome email to a newly registered user."""
        if not self.is_configured():
            return False

        display_name = name or to_email.split("@")[0]
        subject = "Welcome to ResearchAI — Your Research Workspace is Ready"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 40px 20px; }}
                .container {{ max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; padding: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
                .logo {{ width: 44px; height: 44px; background: #059669; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; color: #ffffff; font-size: 24px; font-weight: bold; margin-bottom: 24px; }}
                h1 {{ font-size: 22px; color: #0f172a; margin-top: 0; margin-bottom: 12px; letter-spacing: -0.02em; }}
                p {{ font-size: 14px; line-height: 1.6; color: #475569; margin-bottom: 20px; }}
                .button {{ display: inline-block; background-color: #059669; color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 10px; font-size: 14px; font-weight: 600; margin-top: 8px; margin-bottom: 24px; }}
                .footer {{ border-top: 1px solid #e2e8f0; padding-top: 20px; font-size: 12px; color: #94a3b8; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">⚡</div>
                <h1>Welcome to ResearchAI, {display_name}!</h1>
                <p>Your verified research workspace is ready. You now have direct access to our multi-agent intelligence platform searching across 8+ academic and scientific databases simultaneously.</p>
                <p>Start asking complex research inquiries, comparing literature, and generating full synthesized reports in PDF, DOCX, and Markdown formats.</p>
                <a href="{settings.FRONTEND_URL}/login" class="button">Launch ResearchAI Studio →</a>
                <div class="footer">
                    © 2026 ResearchAI Intelligence Inc. • All rights reserved.
                </div>
            </div>
        </body>
        </html>
        """

        return await asyncio.to_thread(self._send_smtp, to_email, subject, html_content)

    def _send_smtp(self, to_email: str, subject: str, html_content: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email

            part = MIMEText(html_content, "html")
            msg.attach(part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, [to_email], msg.as_string())
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False
