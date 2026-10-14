"""Email service for sending welcome, login notification, and other emails."""
import asyncio
import smtplib
from datetime import datetime
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

    # ─── Welcome Email (on Registration) ──────────────────────────────────────
    async def send_welcome_email(self, to_email: str, name: Optional[str] = None):
        """Send a rich welcome email to a newly registered user."""
        if not self.is_configured():
            return False

        display_name = name or to_email.split("@")[0]
        subject = "Welcome to ResearchAI — Your Research Workspace is Ready ⚡"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Welcome to ResearchAI</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

          <!-- Logo -->
          <tr>
            <td align="center" style="padding-bottom:32px;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:linear-gradient(135deg,#059669,#047857);border-radius:16px;padding:14px 18px;">
                    <span style="color:#ffffff;font-size:22px;font-weight:800;letter-spacing:-0.5px;">⚡ ResearchAI</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background:#1e293b;border-radius:20px;border:1px solid #334155;overflow:hidden;">

              <!-- Hero -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:linear-gradient(135deg,#064e3b 0%,#065f46 50%,#0f172a 100%);padding:40px 40px 32px;">
                    <p style="margin:0 0 8px;color:#6ee7b7;font-size:12px;font-weight:600;letter-spacing:2px;text-transform:uppercase;">Account Activated</p>
                    <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:800;letter-spacing:-0.5px;line-height:1.2;">
                      Welcome, {display_name}! 🎉
                    </h1>
                    <p style="margin:16px 0 0;color:#94a3b8;font-size:15px;line-height:1.6;">
                      Your ResearchAI workspace is live. You now have access to the world's most powerful AI-driven research platform.
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Features -->
              <table width="100%" cellpadding="0" cellspacing="0" style="padding:32px 40px;">
                <tr>
                  <td>
                    <p style="margin:0 0 20px;color:#cbd5e1;font-size:13px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;">What you can do</p>

                    <!-- Feature 1 -->
                    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px;">
                      <tr>
                        <td width="44" valign="top">
                          <div style="background:#064e3b;border-radius:10px;width:36px;height:36px;text-align:center;line-height:36px;font-size:18px;">🔬</div>
                        </td>
                        <td style="padding-left:14px;">
                          <p style="margin:0 0 2px;color:#f1f5f9;font-size:14px;font-weight:600;">Multi-Agent Research</p>
                          <p style="margin:0;color:#64748b;font-size:13px;line-height:1.5;">Search 8+ academic databases simultaneously with AI agents</p>
                        </td>
                      </tr>
                    </table>

                    <!-- Feature 2 -->
                    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px;">
                      <tr>
                        <td width="44" valign="top">
                          <div style="background:#064e3b;border-radius:10px;width:36px;height:36px;text-align:center;line-height:36px;font-size:18px;">📄</div>
                        </td>
                        <td style="padding-left:14px;">
                          <p style="margin:0 0 2px;color:#f1f5f9;font-size:14px;font-weight:600;">Full Report Generation</p>
                          <p style="margin:0;color:#64748b;font-size:13px;line-height:1.5;">Export synthesized reports as PDF, DOCX, or Markdown</p>
                        </td>
                      </tr>
                    </table>

                    <!-- Feature 3 -->
                    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
                      <tr>
                        <td width="44" valign="top">
                          <div style="background:#064e3b;border-radius:10px;width:36px;height:36px;text-align:center;line-height:36px;font-size:18px;">💬</div>
                        </td>
                        <td style="padding-left:14px;">
                          <p style="margin:0 0 2px;color:#f1f5f9;font-size:14px;font-weight:600;">AI Research Chat</p>
                          <p style="margin:0;color:#64748b;font-size:13px;line-height:1.5;">Ask complex scientific questions and get cited, verified answers</p>
                        </td>
                      </tr>
                    </table>

                    <!-- CTA Button -->
                    <table cellpadding="0" cellspacing="0" style="margin-bottom:8px;">
                      <tr>
                        <td style="background:linear-gradient(135deg,#059669,#047857);border-radius:12px;">
                          <a href="{settings.FRONTEND_URL}/chat/new" style="display:inline-block;padding:14px 32px;color:#ffffff;text-decoration:none;font-size:15px;font-weight:700;letter-spacing:-0.2px;">
                            Launch ResearchAI →
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Divider -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="border-top:1px solid #334155;padding:24px 40px;">
                    <p style="margin:0;color:#475569;font-size:12px;line-height:1.6;">
                      This email was sent to <span style="color:#94a3b8;">{to_email}</span> because you created a ResearchAI account.
                      If this wasn't you, you can safely ignore this email.
                    </p>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding:28px 0 8px;">
              <p style="margin:0 0 8px;color:#334155;font-size:12px;">© 2026 ResearchAI Intelligence Inc.</p>
              <p style="margin:0;color:#1e3a5f;font-size:11px;">Made with ❤️ for researchers worldwide</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        return await asyncio.to_thread(self._send_smtp, to_email, subject, html_content)

    # ─── Login Notification Email ──────────────────────────────────────────────
    async def send_login_email(self, to_email: str, name: Optional[str] = None, login_method: str = "email"):
        """Send a beautiful login notification email."""
        if not self.is_configured():
            return False

        display_name = name or to_email.split("@")[0]
        now = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
        method_icon = "🔐" if login_method == "email" else "🔵"
        method_label = "Email & Password" if login_method == "email" else "Google Account"
        subject = f"New sign-in to ResearchAI, {display_name}"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>ResearchAI Sign-In</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="max-width:520px;width:100%;">

          <!-- Logo -->
          <tr>
            <td align="center" style="padding-bottom:28px;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:linear-gradient(135deg,#059669,#047857);border-radius:14px;padding:12px 16px;">
                    <span style="color:#ffffff;font-size:20px;font-weight:800;letter-spacing:-0.5px;">⚡ ResearchAI</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background:#1e293b;border-radius:20px;border:1px solid #334155;overflow:hidden;">

              <!-- Top accent bar -->
              <tr>
                <td style="background:linear-gradient(90deg,#059669,#0d9488,#0891b2);height:4px;display:block;line-height:4px;font-size:4px;">&nbsp;</td>
              </tr>

              <!-- Content -->
              <table width="100%" cellpadding="0" cellspacing="0" style="padding:36px 40px 28px;">
                <tr>
                  <td>
                    <!-- Icon + Title -->
                    <table cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                      <tr>
                        <td style="background:#064e3b;border-radius:14px;width:52px;height:52px;text-align:center;line-height:52px;font-size:24px;">🔓</td>
                        <td style="padding-left:16px;">
                          <p style="margin:0 0 2px;color:#6ee7b7;font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;">Sign-In Detected</p>
                          <h1 style="margin:0;color:#f1f5f9;font-size:22px;font-weight:800;letter-spacing:-0.3px;">New login to your account</h1>
                        </td>
                      </tr>
                    </table>

                    <p style="margin:0 0 24px;color:#94a3b8;font-size:14px;line-height:1.7;">
                      Hi <strong style="color:#e2e8f0;">{display_name}</strong>, we detected a new sign-in to your ResearchAI account. Here are the details:
                    </p>

                    <!-- Details box -->
                    <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;border-radius:12px;border:1px solid #1e3a5f;margin-bottom:24px;">
                      <tr>
                        <td style="padding:20px 24px;">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td style="padding-bottom:14px;border-bottom:1px solid #1e293b;">
                                <p style="margin:0 0 2px;color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Account</p>
                                <p style="margin:0;color:#e2e8f0;font-size:14px;font-weight:500;">{to_email}</p>
                              </td>
                            </tr>
                            <tr>
                              <td style="padding:14px 0;border-bottom:1px solid #1e293b;">
                                <p style="margin:0 0 2px;color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Sign-In Method</p>
                                <p style="margin:0;color:#e2e8f0;font-size:14px;font-weight:500;">{method_icon} {method_label}</p>
                              </td>
                            </tr>
                            <tr>
                              <td style="padding-top:14px;">
                                <p style="margin:0 0 2px;color:#475569;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Time</p>
                                <p style="margin:0;color:#e2e8f0;font-size:14px;font-weight:500;">🕐 {now}</p>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>

                    <!-- Security note -->
                    <table width="100%" cellpadding="0" cellspacing="0" style="background:#431407;border-radius:10px;border:1px solid #7c2d12;margin-bottom:28px;">
                      <tr>
                        <td style="padding:14px 18px;">
                          <p style="margin:0;color:#fed7aa;font-size:13px;line-height:1.6;">
                            ⚠️ <strong>Not you?</strong> If you didn't sign in, your account may be compromised. Change your password immediately.
                          </p>
                        </td>
                      </tr>
                    </table>

                    <!-- CTA -->
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="background:linear-gradient(135deg,#059669,#047857);border-radius:10px;">
                          <a href="{settings.FRONTEND_URL}/chat/new" style="display:inline-block;padding:12px 28px;color:#ffffff;text-decoration:none;font-size:14px;font-weight:700;">
                            Go to ResearchAI →
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Footer -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="border-top:1px solid #334155;padding:20px 40px;">
                    <p style="margin:0;color:#475569;font-size:12px;line-height:1.6;">
                      This security alert was sent to <span style="color:#64748b;">{to_email}</span>.
                      © 2026 ResearchAI Intelligence Inc.
                    </p>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <!-- Bottom spacing -->
          <tr><td style="padding-top:28px;"></td></tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

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
