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
        try:
            self.username = os.environ["SMTP_USERNAME"]
            print(f"SMTP Username: {self.username}")
        except KeyError:
            print("ERROR: SMTP_USERNAME not found in environment variables")
            raise

        try:
            self.password = os.environ["SMTP_PASSWORD"]
            # Only show first 4 and last 4 characters of password
            masked_password = self.password[:4] + '*' * (len(self.password)-8) + self.password[-4:]
            print(f"SMTP Password: {masked_password}")
            print(f"Password length: {len(self.password)}")
        except KeyError:
            print("ERROR: SMTP_PASSWORD not found in environment variables")
            raise

        self.recipient = "brett@marketingtech.pro"

    def send_report(self, filepaths, timestamp=None):
        """Send CSV reports as email attachments"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        if isinstance(filepaths, str):
            filepaths = [filepaths]  # Convert single filepath to list

        print(f"Attempting to send email with files: {filepaths}")
        for filepath in filepaths:
            print(f"File exists ({filepath}): {os.path.exists(filepath)}")

        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = self.recipient
            msg["Subject"] = f"QNTM API Latest CSV {timestamp}"

            # Create email body with information about both files
            body = "Please find attached the latest report data.\n\n"
            for filepath in filepaths:
                filename = os.path.basename(filepath)
                if 'invalid' in filename.lower():
                    body += f"\nThe file '{filename}' contains contacts that are missing both email and phone number."
                else:
                    body += f"\nThe file '{filename}' contains valid contacts that will be processed in GHL."

            msg.attach(MIMEText(body, "plain"))

            # Attach all files
            print("Adding attachments...")
            for filepath in filepaths:
                if os.path.exists(filepath):
                    with open(filepath, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(filepath)}",
                    )
                    msg.attach(part)
                else:
                    print(f"Warning: File not found: {filepath}")

            print("Establishing SMTP connection...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                print("Starting TLS...")
                server.starttls()
                print("Attempting login...")
                server.login(self.username, self.password)
                print("Sending message...")
                server.send_message(msg)

                print(f"Email sent successfully to {self.recipient}")
                return True

        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            print(f"Error type: {type(e)}")
            if isinstance(e, smtplib.SMTPAuthenticationError):
                print("Authentication failed - check username and password")
            return False
