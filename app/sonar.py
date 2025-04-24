"""
Code for integration of Water Linked Sonar 3D-15 with BlueOS
"""

import time
import threading

from loguru import logger

from blueoshelper import request
from sonarfinder import find_the_sonar

HOSTNAME = "192.168.194.96"  # Default Sonar IP


# pylint: disable=too-many-instance-attributes
# pylint: disable=unspecified-encoding
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
class SonarDriver(threading.Thread):
    """
    Simplified driver for detecting the sonar and reporting its status.
    """

    status = "Starting"
    hostname = HOSTNAME  # Default Sonar IP
    enabled = True

    def __init__(self) -> None:
        threading.Thread.__init__(self)

    def report_status(self, msg: str) -> None:
        """
        Updates the status and logs it.

        Args:
            msg (str): The status message to report.
        """
        self.status = msg
        logger.debug(msg)

    def get_status(self) -> dict:
        """
        Returns the current status as a dictionary.

        Returns:
            dict: A dictionary containing the current status, enabled state, and hostname.
        """
        return {
            "status": self.status,
            "enabled": self.enabled,
            "hostname": self.hostname,
        }

    def wait_for_cable_guy(self) -> None:
        """
        Waits for the Docker cable-guy to come online.
        """
        while not request("http://host.docker.internal/cable-guy/v1.0/ethernet"):
            self.report_status("waiting for cable-guy to come online...")
            time.sleep(1)

    def look_for_sonar(self) -> None:
        """
        Waits for the sonar to show up at the designated hostname or finds it on the network.
        """
        self.wait_for_cable_guy()
        self.report_status(f"Trying to talk to sonar at http://{self.hostname}/api/v1/about")
        while True:
            if request(f"http://{self.hostname}/api/v1/about"):
                self.report_status(f"Sonar found at {self.hostname}")
                return
            self.report_status(f"Could not talk to sonar at {self.hostname}, looking for it in the local network...")
            found_sonar = find_the_sonar()
            if found_sonar:
                self.report_status(f"Sonar found at address {found_sonar}, using it instead.")
                self.hostname = found_sonar
                return
            time.sleep(1)

    def run(self) -> None:
        """
        Main loop for detecting the sonar and reporting its status.
        """
        self.look_for_sonar()
        self.report_status("Sonar detection complete. Ready.")
        while self.enabled:
            time.sleep(1)  # Keep the thread alive to allow status updates

        logger.error("Driver Quit! This should not happen.")
