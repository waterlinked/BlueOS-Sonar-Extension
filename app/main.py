#!/usr/bin/env python3
"""
Driver for the Water Linked Sonar 3D-15 
"""

import json

from flask import Flask

from sonar import SonarDriver

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path="/static", static_folder="static")
thread = None


class API:
    sonar = None

    def __init__(self, sonar: SonarDriver):
        self.sonar = sonar

    def get_status(self) -> str:
        """
        Returns the driver status as a JSON containing the keys
        status, orientation, hostname, and enabled
        """
        return json.dumps(self.sonar.get_status())

    def set_enabled(self, enabled: str) -> bool:
        """
        Enables/Disables the Sonar driver
        """
        if enabled in ["true", "false"]:
            return self.sonar.set_enabled(enabled == "true")
        return False

    # def set_orientation(self, orientation: int) -> bool:
    #     """
    #     Sets the Sonar mounting orientation:
    #     1 = Down
    #     2 = Forward
    #     """
    #     return self.sonar.set_orientation(orientation)

    # def set_hostname(self, hostname: str) -> bool:
    #     """
    #     Sets the Hostname or IP where the driver tries to connect to the Sonar
    #     """
    #     return self.sonar.set_hostname(hostname)

    # def set_current_position(self, lat: str, lon: str) -> bool:
    #     """
    #     Sets the EKF origin to lat, lon
    #     """
    #     return self.sonar.set_current_position(float(lat), float(lon))

    # def set_use_as_rangefinder(self, enabled: str) -> bool:
    #     """
    #     Enables/disables usage of Sonar as rangefinder
    #     """
    #     if enabled in ["true", "false"]:
    #         return self.sonar.set_use_as_rangefinder(enabled == "true")
    #     return False

    # def load_params(self, selector: str) -> bool:
    #     """
    #     Load parameters
    #     """
    #     if selector in ["sonar", "sonar_gps"]:
    #         return self.sonar.load_params(selector)
    #     return False

    # def set_message_type(self, messagetype: str):
    #     self.sonar.set_should_send(messagetype)


if __name__ == "__main__":
    driver = SonarDriver()
    api = API(driver)

    @app.route("/get_status")
    def get_status():
        return api.get_status()

    @app.route("/enable/<enable>")
    def set_enabled(enable: str):
        return str(api.set_enabled(enable))

    @app.route("/use_as_rangefinder/<enable>")
    def set_use_rangefinder(enable: str):
        return str(api.set_use_as_rangefinder(enable))

    @app.route("/load_params/<selector>")
    def load_params(selector: str):
        return str(api.load_params(selector))

    @app.route("/orientation/<int:orientation>")
    def set_orientation(orientation: int):
        return str(api.set_orientation(orientation))

    @app.route("/message_type/<messagetype>")
    def set_message_type(messagetype: str):
        return str(api.set_message_type(messagetype))

    @app.route("/setcurrentposition/<lat>/<lon>")
    def set_current_position(lat, lon):
        return str(api.set_current_position(lat, lon))

    @app.route("/register_service")
    def register_service():
        return app.send_static_file("service.json")

    @app.route("/")
    def root():
        return app.send_static_file("index.html")

    driver.start()
    app.run(host="0.0.0.0", port=9001)
