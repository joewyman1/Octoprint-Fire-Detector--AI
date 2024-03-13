import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from octoprint.settings import settings
from octoprint.plugin import OctoPrintPlugin

class FireDetectionPlugin(OctoPrintPlugin):
    def on_settings_initialized(self):
        self._settings.set_defaults({
            "webcam_url": "",
            "smtp_server": "",
            "smtp_port": 0,
            "smtp_username": "",
            "smtp_password": "",
            "recipient_email": ""
        })

    def get_settings_defaults(self):
        return dict(
            webcam_url="",
            smtp_server="",
            smtp_port=0,
            smtp_username="",
            smtp_password="",
            recipient_email=""
        )

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def send_email_notification(self, message):
        smtp_server = self._settings.get(["smtp_server"])
        smtp_port = self._settings.get_int(["smtp_port"])
        smtp_username = self._settings.get(["smtp_username"])
        smtp_password = self._settings.get(["smtp_password"])
        recipient_email = self._settings.get(["recipient_email"])

        if not all([smtp_server, smtp_port, smtp_username, smtp_password, recipient_email]):
            self._logger.error("SMTP settings are incomplete, cannot send email notification.")
            return

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = "Fire Detected!"

        msg.attach(MIMEText(message, 'plain'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, recipient_email, msg.as_string())
            server.quit()
            self._logger.info("Email notification sent successfully.")
        except Exception as e:
            self._logger.error("Error sending email notification: %s" % str(e))

__plugin_name__ = "Fire Detection"
__plugin_pythoncompat__ = ">=3,<4"
__plugin_version__ = "0.1.0"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FireDetectionPlugin()

