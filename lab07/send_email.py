import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL = "hanzina53@gmail.com"
PASSWORD = "qcha ylst luyu pmez"   
TO_EMAIL = "hanzian67@gmail.com"

def send_email():
    subject = "Server Health Report"
    body = f"Server check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nEverything looks OK."

    msg = MIMEText(body)
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    send_email()

