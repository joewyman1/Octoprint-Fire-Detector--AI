import cv2
import numpy as np
import requests
from octoprint.events import Events
from octoprint.settings import settings
from octoprint.plugin import OctoPrintPlugin

def detect_fire(image):
    if image is None:
        return False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    return bool(contours)

class FireDetectionPlugin(OctoPrintPlugin):
    def __init__(self):
        self.printing = False
        self.heaters_on = False

    def on_after_startup(self):
        self._logger.info("Fire Detection plugin initialized.")

    def on_settings_initialized(self):
        self._settings.set_defaults({
            "webcam_url": "",
            "pushbullet_api_key": "",
            "threshold_sensitivity": 0.5
        })

    def get_settings_defaults(self):
        return dict(
            webcam_url="",
            pushbullet_api_key="",
            threshold_sensitivity=0.5
        )

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=True)
        ]

    def send_notification(self, is_fire_detected, percentage_sure):
        pushbullet_api_key = self._settings.get(["pushbullet_api_key"])

        threshold_sensitivity = self._settings.get_float(["threshold_sensitivity"])

        if not pushbullet_api_key:
            self._logger.error("Pushbullet API key must be provided.")
            return

        if is_fire_detected and percentage_sure >= threshold_sensitivity:
            title = "Fire Detected!"
            body = f"Fire detected with {percentage_sure:.2f}% confidence."
            url = "https://api.pushbullet.com/v2/pushes"
            headers = {
                "Access-Token": pushbullet_api_key,
                "Content-Type": "application/json"
            }
            data = {
                "type": "note",
                "title": title,
                "body": body
            }
            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                self._logger.info("Notification sent successfully via Pushbullet.")
            except Exception as e:
                self._logger.error("Error sending notification via Pushbullet: %s" % str(e))
        else:
            self._logger.info("No fire detected or confidence below threshold.")

    def pause_print(self):
        self._printer.pause_print(reason="Fire detected!")

    def on_event(self, event, payload):
        if event == Events.PRINT_STARTED:
            self.printing = True
        elif event == Events.PRINT_DONE or event == Events.PRINT_FAILED or event == Events.PRINT_CANCELLED:
            self.printing = False
        elif event == Events.CONNECTED:
            self.heaters_on = payload.get("state", {}).get("temperature", {}).get("tool0", {}).get("target", 0) > 0
        elif event == Events.DISCONNECTED:
            self.heaters_on = False

        if self.printing or self.heaters_on:
            webcam_url = self._settings.get(["webcam_url"])
            if webcam_url:
                response = requests.get(webcam_url, stream=True)
                if response.status_code == 200:
                    image = np.asarray(bytearray(response.content), dtype="uint8")
                    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                    is_fire_detected = detect_fire(image)
                    self.send_notification(is_fire_detected, 0.7)
                    if is_fire_detected:
                        self.pause_print()
                
__plugin_name__ = "Fire Detector AI"
__plugin_pythoncompat__ = ">=3,<4"
__plugin_version__ = "0.1.0"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FireDetectionPlugin()

