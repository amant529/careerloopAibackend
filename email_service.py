import smtplib
import os
from email.mime.text import MIMEText

EMAIL = os.getenv("EMAIL")
EMAIL_PASS = os.getenv("EMAIL_PASS")

async def send_otp_email(to_email: str, otp: int):
    msg = MIMEText(f"Your Careerloop AI OTP is: {otp}")
    msg["Subject"] = "Careerloop AI OTP Login"
    msg["From"] = EMAIL
    msg["To"] = to_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL, EMAIL_PASS)
    server.sendmail(EMAIL, to_email, msg.as_string())
    server.quit()
