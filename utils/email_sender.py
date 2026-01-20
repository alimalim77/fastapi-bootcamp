import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Send OTP verification email using Gmail SMTP.
    
    Requires EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.
    EMAIL_PASSWORD should be a Gmail App Password (not your regular password).
    """
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD environment variables must be set")
    
    # Create email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Verification Code"
    message["From"] = sender_email
    message["To"] = to_email
    
    # Plain text version
    text = f"""
    Your verification code is: {otp_code}
    
    This code will expire in 10 minutes.
    
    If you didn't request this code, please ignore this email.
    """
    
    # HTML version
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 500px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .otp-code {{ font-size: 32px; font-weight: bold; color: #2563eb; letter-spacing: 5px; text-align: center; padding: 20px; background: #eff6ff; border-radius: 8px; margin: 20px 0; }}
            .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 style="text-align: center; color: #333;">Email Verification</h2>
            <p>Use the following code to verify your email address:</p>
            <div class="otp-code">{otp_code}</div>
            <p style="text-align: center; color: #666;">This code will expire in <strong>10 minutes</strong>.</p>
            <div class="footer">
                If you didn't request this code, please ignore this email.
            </div>
        </div>
    </body>
    </html>
    """
    
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    
    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise
