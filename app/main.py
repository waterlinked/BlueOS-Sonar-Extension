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

        Returns:
            str: JSON string containing the driver status
        """
        return json.dumps(self.sonar.get_status())


if __name__ == "__main__":
    driver = SonarDriver()
    api = API(driver)

    @app.route("/get_status")
    def get_status():
        return api.get_status()

    @app.route("/register_service")
    def register_service():
        return app.send_static_file("service.json")

    @app.route("/")
    def root():
        return app.send_static_file("index.html")

    driver.start()
    app.run(host="0.0.0.0", port=9001)
