import argparse
import asyncio
import json
import logging

from aioconsole import ainput

from gree_versati.device import Device, DeviceInfo
from gree_versati.discovery import Discovery, Listener

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)
_LOGGER = logging.getLogger(__name__)


class DiscoveryListener(Listener):
    device: Device

    def __init__(self, bind):
        """Initialize the event handler."""
        super().__init__()
        self.bind = bind

    """Class to handle incoming device discovery events."""

    async def device_found(self, device_info: DeviceInfo) -> None:
        """A new device was found on the network."""
        if self.bind:
            self.device = Device(device_info)
            await self.device.bind()
            await self.device.request_version()
            _LOGGER.info(f"Device firmware: {self.device.hid}")

    def get_device(self):
        return self.device


async def run_discovery(bind=False):
    """Run the device discovery process."""
    _LOGGER.debug("Scanning network for Gree devices")

    discovery = Discovery()
    listener = DiscoveryListener(bind)
    discovery.add_listener(listener)

    await discovery.scan(wait_for=10)
    _LOGGER.info("Done discovering devices")


async def wait_for_input():
    discovery = Discovery()
    listener = DiscoveryListener(True)
    discovery.add_listener(listener)

    await discovery.scan(wait_for=10)
    _LOGGER.info("Done discovering devices")

    device = listener.get_device()

    while True:
        """
            Get text input from the command line and pass it to device's decrypt method.
            Attempt to naively clean up the extras from wireshark's copy paste but not much
            effort was put into this. This is enough to capture the pack and decrypt it to
            find correct property names and values.
        """
        try:
            text = await ainput("Enter text to decrypt: ")
            clean_text = text[text.find("{"):] if "{" in text else ""
            obj = json.loads(clean_text)

            if obj.get("pack"):
                obj["pack"] = device._cipher.decrypt(obj["pack"])
                _LOGGER.info(f"Decrypted pack: {obj}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON input after cleaning: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gree command line utility.")
    parser.add_argument("--discovery", default=False, action="store_true")
    parser.add_argument("--bind", default=False, action="store_true")
    parser.add_argument("--decrypt", default=False, action="store_true")
    args = parser.parse_args()

    if args.discovery:
        asyncio.run(run_discovery(args.bind))

    if args.decrypt:
        asyncio.run(wait_for_input())
