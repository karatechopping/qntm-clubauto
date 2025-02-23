import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime


class EmailHandler:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = os.environ["SMTP_USERNAME"]
        self.password = os.environ["SMTP_PASSWORD"]
        self.recipient = "brett@marketingtech.pro"

    def send_report(self, filepath, timestamp=None):
        """Send CSV report as email attachment"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = self.recipient
            msg["Subject"] = f"QNTM API Latest CSV {timestamp}"

            body = "Please find attached the latest report data."
            msg.attach(MIMEText(body, "plain"))

            with open(filepath, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(filepath)}",
            )
            msg.attach(part)

            # Send email
        #            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        #                server.starttls()
        #                server.login(self.username, self.password)
        #                server.send_message(msg)
        #
        #            print(f"Email sent successfully to {self.recipient}")
        #            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
