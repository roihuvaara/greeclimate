"""
Gree Versati - Python library for controlling Gree Versati series heatpumps

Fork of greeclimate by Clifford Roche.
Maintained by Jukka Roihuvaara.
"""

import logging

from gree_versati.device import Device
from gree_versati.discovery import Discovery, Listener
from gree_versati.exceptions import DeviceNotBoundError, DeviceTimeoutError

__version__ = "1.0.12"

# Define what should be importable directly from the package
__all__ = [
    "Device",
    "Discovery",
    "Listener",
    "DeviceNotBoundError",
    "DeviceTimeoutError",
]

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)
