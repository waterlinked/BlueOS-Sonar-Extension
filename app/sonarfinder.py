import json
import time
from typing import List, Optional

import nmap3
from loguru import logger

from blueoshelper import request


def check_for_proper_sonar(ip: str) -> bool:
    # Check the API for the product_name field
    url = f"http://{ip}/api/v1/about"
    try:
        return "Sonar" in json.loads(request(url))["product_name"]
    except Exception as e:
        logger.debug(f"{ip} is not a sonar: {e}")
        return False
    json.loads(request(url))


def get_ips_wildcards(ips: List[str]):
    # Takes a list of ip strings and replaces the last field with * for it to be used by nmap
    return [".".join([*(ip.split(".")[0:-1]), "*"]) for ip in ips]


def find_the_sonar() -> Optional[str]:
    # The sonar always reports 192.168.194.95 on mdns, so we need to take drastic measures.
    # Nmap to the rescue!

    nmap = nmap3.Nmap()
    # generate the scan mask from our current ips
    # networks = json.loads(request("http://host.docker.internal/cable-guy/v1.0/ethernet"))
    # Instead of querying Cable Guy, define your network configuration manually.
    networks = [{
        "addresses": [{"ip": "192.168.194.0", "mode": "server"}] # TODO: Remove this line and uncomment the line above for Docker
    }]
    current_networks = [network["addresses"] for network in networks]
    # this looks like [{'ip': '192.168.2.2', 'mode': 'server'}]
    current_ips = []
    for network in current_networks:
        for entry in network:
            current_ips.append(entry["ip"])

    scans = get_ips_wildcards(current_ips)
    logger.info(f"Scanning: {scans} for Sonars")
    candidates = []
    for ip in scans:
        results = []
        while not results:
            try:
                results = nmap.scan_top_ports(ip, args="-p 80 --open")
            except nmap3.exceptions.NmapExecutionError as e:
                logger.debug(f"error running nmap: {e}, trying again in 1 second")
                time.sleep(1)
        for result in results:
            if result in current_ips:
                continue
            if result in ("runtime", "stats"):
                continue
            candidates.append(result)

    logger.info(f"candidates for being a sonar: {candidates}")

    for candidate in candidates:
        if check_for_proper_sonar(candidate):
            logger.info(f"Sonar found at {candidate}")
            return candidate
    return None
