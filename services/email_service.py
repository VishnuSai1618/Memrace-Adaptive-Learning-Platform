"""
Email service for MEMRACE — sends transactional emails via SMTP.
Uses Python stdlib smtplib so no extra dependencies are required.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app


def send_reset_email(to_email: str, reset_link: str) -> bool:
    """
    Send a password-reset email.

    Args:
        to_email:   Recipient email address.
        reset_link: The full /reset-password/<token> URL.

    Returns:
        True on success, False on failure (error is logged, not raised).
    """
    server_host  = current_app.config.get('MAIL_SERVER',   'smtp.gmail.com')
    server_port  = current_app.config.get('MAIL_PORT',     587)
    use_tls      = current_app.config.get('MAIL_USE_TLS',  True)
    username     = current_app.config.get('MAIL_USERNAME', '')
    password     = current_app.config.get('MAIL_PASSWORD', '')
    from_name    = current_app.config.get('MAIL_FROM_NAME','MEMRACE')
    from_email   = username  # sender = same as login

    # Build e-mail
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Reset Your MEMRACE Password'
    msg['From']    = f'{from_name} <{from_email}>'
    msg['To']      = to_email

    # Plain-text fallback
    text_body = f"""\
Hi,

You requested a password reset for your MEMRACE account.

Click the link below to reset your password:
{reset_link}

This link is valid for 30 minutes. If you did not request this reset,
you can safely ignore this email — your password will not change.

— The MEMRACE Team
"""

    # HTML body
    html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Your Password</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Inter',Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="background:#0a0a0a;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#111111;border-radius:16px;overflow:hidden;
                      border:1px solid rgba(255,184,77,0.15);">

          <!-- Header -->
          <tr>
            <td style="padding:32px 40px 24px;border-bottom:1px solid rgba(255,184,77,0.1);">
              <h1 style="margin:0;font-size:24px;font-weight:800;letter-spacing:-0.5px;
                         background:linear-gradient(135deg,#ffb84d,#ff9800);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">
                🧠 MEMRACE
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 32px;color:#ffffff;">
              <h2 style="margin:0 0 12px;font-size:22px;font-weight:700;color:#ffffff;">
                Password Reset Request
              </h2>
              <p style="margin:0 0 24px;color:rgba(255,255,255,0.65);line-height:1.6;font-size:15px;">
                We received a request to reset the password for your MEMRACE account.
                Click the button below to create a new password.
              </p>

              <!-- Button -->
              <table cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
                <tr>
                  <td style="border-radius:10px;
                             background:linear-gradient(135deg,#ffb84d,#ff9800);">
                    <a href="{reset_link}"
                       style="display:inline-block;padding:14px 32px;
                              font-size:15px;font-weight:700;color:#000000;
                              text-decoration:none;border-radius:10px;
                              letter-spacing:0.2px;">
                      Reset My Password
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Link fallback -->
              <p style="margin:0 0 8px;color:rgba(255,255,255,0.45);font-size:13px;">
                Or copy and paste this link into your browser:
              </p>
              <p style="margin:0 0 28px;word-break:break-all;">
                <a href="{reset_link}"
                   style="color:#ffb84d;font-size:13px;text-decoration:underline;">
                  {reset_link}
                </a>
              </p>

              <!-- Warning -->
              <div style="background:rgba(255,184,77,0.08);border-left:3px solid #ffb84d;
                          border-radius:0 8px 8px 0;padding:14px 16px;">
                <p style="margin:0;color:rgba(255,255,255,0.65);font-size:13px;line-height:1.5;">
                  ⏱ <strong style="color:#ffb84d;">This link expires in 30 minutes.</strong><br>
                  If you did not request a password reset, you can safely ignore this email.
                </p>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px;border-top:1px solid rgba(255,255,255,0.06);">
              <p style="margin:0;color:rgba(255,255,255,0.3);font-size:12px;text-align:center;">
                © 2026 MEMRACE AI. Powered by Google Gemini.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body,  'html'))

    try:
        if not username or not password:
            current_app.logger.warning(
                'MAIL_USERNAME / MAIL_PASSWORD not configured — skipping email send.'
            )
            # In dev, print the link so you can still test manually
            current_app.logger.info(f'[DEV] Password reset link: {reset_link}')
            return False

        with smtplib.SMTP(server_host, server_port) as smtp:
            if use_tls:
                smtp.starttls()
            smtp.login(username, password)
            smtp.sendmail(from_email, to_email, msg.as_string())
        return True

    except Exception as e:
        current_app.logger.error(f'Failed to send reset email to {to_email}: {e}')
        # In dev, always print the link so the feature is still testable
        current_app.logger.info(f'[DEV] Password reset link: {reset_link}')
        return False
