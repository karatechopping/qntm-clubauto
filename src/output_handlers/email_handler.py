# src/output_handlers/email_handler.py
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

class EmailHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        try:
            self.username = os.environ["SMTP_USERNAME"]
            self.logger.info(f"SMTP Username: {self.username}")
        except KeyError:
            self.logger.error("SMTP_USERNAME not found in environment variables")
            raise

        try:
            self.password = os.environ["SMTP_PASSWORD"]
            # Only show first 4 and last 4 characters of password
            masked_password = self.password[:4] + '*' * (len(self.password)-8) + self.password[-4:]
            self.logger.info(f"SMTP Password: {masked_password}")
            self.logger.info(f"Password length: {len(self.password)}")
        except KeyError:
            self.logger.error("SMTP_PASSWORD not found in environment variables")
            raise

        self.recipient = "brett@marketingtech.pro"

    def send_report(self, results, timestamp):
        """
        Send report email with comprehensive results
        :param results: Dictionary containing all process results
        :param timestamp: Timestamp string
        """
        self.logger.info(f"Attempting to send email with results: {results}")

        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = self.recipient
            msg["Subject"] = f"QNTM API Process Report {timestamp}"

            # Create detailed body
            body = f"Process Report for {timestamp}\n"
            body += "=" * 50 + "\n\n"

            # CSV Status
            body += "CSV PROCESSING\n"
            body += "-" * 20 + "\n"
            if results['status'].get('csv') == 'Completed':
                body += f"Status: Completed\n"
                body += f"Valid contacts: {results['csv_stats']['valid']}\n"
                body += f"Invalid contacts: {results['csv_stats']['invalid']}\n"
                if results['csv_files']:
                    body += f"Files generated:\n"
                    for file in results['csv_files']:
                        body += f"- {os.path.basename(file)}\n"
            else:
                body += "Status: Skipped\n"
            body += "\n"

            # GHL Status
            body += "GHL PROCESSING\n"
            body += "-" * 20 + "\n"
            if results['status'].get('ghl') == 'Completed':
                body += f"Status: Completed\n"
                if 'success' in results['ghl_stats']:
                    body += f"Total Successfully processed: {results['ghl_stats']['success']}\n"
                if 'failed' in results['ghl_stats']:
                    body += f"Failed: {results['ghl_stats']['failed']}\n"
                if 'added' in results['ghl_stats']:
                    body += f"New contacts added: {results['ghl_stats']['added']}\n"
                if 'updated' in results['ghl_stats']:
                    body += f"Existing contacts updated: {results['ghl_stats']['updated']}\n"
                if 'processing_time' in results['ghl_stats']:
                    body += f"Processing time: {results['ghl_stats']['processing_time']['minutes']} minutes "
                    body += f"and {results['ghl_stats']['processing_time']['seconds']} seconds\n"
            else:
                body += "Status: Skipped\n"
            body += "\n"

            # Process Summary
            body += "PROCESS SUMMARY\n"
            body += "-" * 20 + "\n"
            for component, status in results['status'].items():
                if component != 'email':  # Skip email status
                    body += f"{component.upper()}: {status}\n"

            msg.attach(MIMEText(body, "plain"))

            # Attach CSV files if they exist
            if results['csv_files']:
                self.logger.info("Adding CSV attachments...")
                for filepath in results['csv_files']:
                    if os.path.exists(filepath):
                        self.logger.info(f"Attaching file: {filepath}")
                        with open(filepath, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(filepath)}",
                        )
                        msg.attach(part)
                        self.logger.info(f"Successfully attached: {filepath}")
                    else:
                        self.logger.warning(f"Warning: File not found: {filepath}")

            self.logger.info("Establishing SMTP connection...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                self.logger.info("Starting TLS...")
                server.starttls()
                self.logger.info("Attempting login...")
                server.login(self.username, self.password)
                self.logger.info("Sending message...")
                server.send_message(msg)

                self.logger.info(f"Email sent successfully to {self.recipient}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            self.logger.error(f"Error type: {type(e)}")
            if isinstance(e, smtplib.SMTPAuthenticationError):
                self.logger.error("Authentication failed - check username and password")
            return False

    def _format_file_info(self, filepath):
        """
        Helper method to format file information including row count
        """
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                row_count = sum(1 for line in f) - 2  # Subtract 2 for headers
            return f"{os.path.basename(filepath)} ({row_count} records)"
        return f"{os.path.basename(filepath)} (file not found)"

if __name__ == "__main__":
    # Test code
    test_results = {
        'csv_files': ['test_valid.csv', 'test_invalid.csv'],
        'csv_stats': {'valid': 100, 'invalid': 10},
        'ghl_stats': {
            'success': 95,
            'failed': 5,
            'added': 60,
            'updated': 35,
            'processing_time': {'minutes': 1, 'seconds': 30}
        },
        'status': {
            'csv': 'Completed',
            'ghl': 'Completed',
            'email': 'Pending'
        }
    }

    handler = EmailHandler()
    handler.send_report(test_results, datetime.now().strftime("%Y-%m-%d_%H%M%S"))
