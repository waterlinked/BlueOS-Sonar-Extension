"""
Code for integration of Water Linked Sonar 3D-15 with BlueOS
"""

import json
import math
import os
import socket
import threading
import time
from enum import Enum
from select import select
from typing import Any, Dict, List

from loguru import logger

from blueoshelper import request
from sonarfinder import find_the_sonar
# from mavlink2resthelper import GPS_GLOBAL_ORIGIN_ID, Mavlink2RestHelper

HOSTNAME = "waterlinked-sonar.local"


class MessageType(str, Enum):

    @staticmethod
    def contains(value):
        return value in set(item.value for item in MessageType)


# pylint: disable=too-many-instance-attributes
# pylint: disable=unspecified-encoding
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
class SonarDriver(threading.Thread):
    """
    Responsible for the Sonar interactions themselves.
    This handles fetching the Sonar data and forwarding it to Ardusub
    """

    status = "Starting"
    version = ""
    # mav = Mavlink2RestHelper()
    socket = None
    port = 16171  # Water Linked mentioned they won't allow changing or disabling this
    enabled = True
    # rangefinder = True
    hostname = HOSTNAME
    timeout = 3  # tcp timeout in seconds

    def __init__(self) -> None:
        threading.Thread.__init__(self)

    def report_status(self, msg: str) -> None:
        self.status = msg
        logger.debug(msg)

    def get_status(self) -> dict:
        """
        Returns a dict with the current status
        """
        return {
            "status": self.status,
            "enabled": self.enabled,
            "hostname": self.hostname
        }

    @property
    def host(self) -> str:
        """Make sure there is no port in the hostname allows local testing by where http can be running on other ports than 80"""
        try:
            host = self.hostname.split(":")[0]
        except IndexError:
            host = self.hostname
        return host

    def look_for_sonar(self):
        """
        Waits for the sonar to show up at the designated hostname
        """
        self.wait_for_cable_guy()
        ip = self.hostname
        self.status = f"Trying to talk to sonar at http://{ip}/api/v1/about"
        while not self.version:
            if not request(f"http://{ip}/api/v1/about"):
                self.report_status(f"could not talk to sonar at {ip}, looking for it in the local network...")
            found_sonar = find_the_sonar()
            if found_sonar:
                self.report_status(f"Sonar found at address {found_sonar}, using it instead.")
                self.hostname = found_sonar
                return
            time.sleep(1)

    def wait_for_cable_guy(self):
        while not request("http://host.docker.internal/cable-guy/v1.0/ethernet"):
            self.report_status("waiting for cable-guy to come online...")
            time.sleep(1)

    def set_enabled(self, enable: bool) -> bool:
        """
        Enables/disables the driver
        """
        self.enabled = enable
        return True

    def setup_connections(self, timeout=300) -> None:
        """
        Sets up the socket to talk to the Sonar
        """
        while timeout > 0:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.socket.setblocking(0)
                return True
            except socket.error:
                time.sleep(0.1)
            timeout -= 1
        self.report_status(f"Setup connection to {self.host}:{self.port} timed out")
        return False

    def reconnect(self):
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except Exception as e:
                self.report_status(f"Unable to reconnect: {e}, looking for the sonar again...")
                self.look_for_sonar()
        success = self.setup_connections()
        if success:
            self.last_recv_time = time.time()  # Don't disconnect directly after connect
            return True

        return False

    def run(self):
        """
        Runs the main routing
        """
        self.look_for_sonar()
        self.setup_connections()
        time.sleep(1)
        self.report_status("Running")
        self.last_recv_time = time.time()
        buf = ""
        connected = True
        while True:
            if not self.enabled:
                time.sleep(1)
                buf = ""  # Reset buf when disabled
                continue

            r, _, _ = select([self.socket], [], [], 0)
            data = None
            if r:
                try:
                    recv = self.socket.recv(1024).decode()
                    connected = True
                    if recv:
                        self.last_recv_time = time.time()
                        buf += recv
                except socket.error as e:
                    logger.warning(f"Disconnected: {e}")
                    connected = False
                except Exception as e:
                    logger.warning(f"Error receiving: {e}")

            # Extract 1 complete line from the buffer if available
            if len(buf) > 0:
                lines = buf.split("\n", 1)
                if len(lines) > 1:
                    buf = lines[1]
                    data = json.loads(lines[0])

            if not connected:
                buf = ""
                self.report_status("restarting")
                self.reconnect()
                time.sleep(0.003)
                continue

            if not data:
                if time.time() - self.last_recv_time > self.timeout:
                    buf = ""
                    self.report_status("timeout, restarting")
                    connected = self.reconnect()
                time.sleep(0.003)
                continue

            self.status = "Running"

            if "type" not in data:
                continue

            if data["type"] == "velocity":
                self.handle_velocity(data)
            elif data["type"] == "position_local":
                self.handle_position_local(data)

            self.check_temperature()
            time.sleep(0.003)
        logger.error("Driver Quit! This should not happen.")
