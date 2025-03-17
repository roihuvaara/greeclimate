import asyncio
import logging
from asyncio import AbstractEventLoop
from typing import Any, Dict, List, Optional, Union

from gree_versati.cipher import CipherV1, CipherV2
from gree_versati.deviceinfo import DeviceInfo
from gree_versati.exceptions import DeviceNotBoundError, DeviceTimeoutError
from gree_versati.network import DeviceProtocol2
from gree_versati.taskable import Taskable

TEMP_OFFSET = 40


class BaseDevice(DeviceProtocol2, Taskable):
    """Class representing a physical device, it's state and properties.

    Devices must be bound, either by discovering their presence, or supplying a
    persistent device key which is then used for communication (and encryption)
    with the unit. See the `bind` function for more details on how to do this.

    Once a device is bound occasionally call `update_state` to request and update
    state from the HVAC, as it is possible that it changes state from other sources.
    """

    def __init__(
        self,
        device_info: Optional[DeviceInfo],
        timeout: int = 120,
        bind_timeout: int = 10,
        loop: Optional[AbstractEventLoop] = None,
    ):
        """Initialize the device object

        Args:
            device_info (DeviceInfo): Information about the physical device
            timeout (int): Timeout for device communication
            bind_timeout (int): Timeout for binding to the device, keep this short to
                prevent delays determining the correct device cipher to use
            loop (AbstractEventLoop): The event loop to run the device operations on
        """
        DeviceProtocol2.__init__(self, timeout)
        Taskable.__init__(self, loop)
        self._logger = logging.getLogger(__name__)
        self.device_info: Optional[DeviceInfo] = device_info

        self._bind_timeout = bind_timeout

        """ Device properties """
        self.hid = None
        self.version: Optional[str] = None
        self.check_version = True
        self._properties: Dict[str, Any] = {}
        self._dirty: List[str] = []

    async def bind(
        self,
        key: Optional[str] = None,
        cipher: Optional[Union[CipherV1, CipherV2]] = None,
    ):
        """Run the binding procedure.

        Binding is a finicky procedure, and happens in 1 of 2 ways:
            1 - Without the key, binding must pass the device info structure
                immediately following the search devices procedure. There is only
                a small window to complete registration.
            2 - With a key, binding is implicit and no further action is required

            Both approaches result in a device_key which is used as like a
            persistent session id.

        Args:
            cipher (CipherV1 | CipherV2): The cipher type to use for encryption,
                if None will attempt to detect the correct one
            key (str): The device key, when provided binding is a NOOP, if None
                binding will attempt to negotiate the key with the device.
                cipher must be provided.

        Raises:
            DeviceNotBoundError: If binding was unsuccessful and no key returned
            DeviceTimeoutError: The device didn't respond
        """

        if key:
            if not cipher:
                raise ValueError("cipher must be provided when key is provided")
            else:
                cipher.key = key
                self.device_cipher = cipher
                return

        if not self.device_info:
            raise DeviceNotBoundError

        if self._transport is None:
            self._transport, _ = await self._loop.create_datagram_endpoint(
                lambda: self, remote_addr=(self.device_info.ip, self.device_info.port)
            )

        self._logger.info("Starting device binding to %s", str(self.device_info))

        try:
            if cipher is not None:
                await self.__bind_internal(cipher)
            else:
                """ Try binding with CipherV1 first, if that fails try CipherV2"""
                try:
                    self._logger.info("Attempting to bind to device using CipherV1")
                    await self.__bind_internal(CipherV1())
                except asyncio.TimeoutError:
                    self._logger.info("Attempting to bind to device using CipherV2")
                    await self.__bind_internal(CipherV2())

        except asyncio.TimeoutError as err:
            raise DeviceTimeoutError from err

        if not self.device_cipher:
            raise DeviceNotBoundError
        else:
            self._logger.info("Bound to device using key %s", self.device_cipher.key)

    async def __bind_internal(self, cipher: Union[CipherV1, CipherV2]):
        """Internal binding procedure, do not call directly"""
        if self.device_info is None:
            raise DeviceNotBoundError
        await self.send(self.create_bind_message(self.device_info), cipher=cipher)
        task = asyncio.create_task(self.ready.wait())
        await asyncio.wait_for(task, timeout=self._bind_timeout)

    def handle_device_bound(self, key: str) -> None:
        """Handle the device bound message from the device"""
        if self.device_cipher is not None:
            self.device_cipher.key = key

    async def request_version(self) -> None:
        """Request the firmware version from the device."""
        if not self.device_cipher:
            await self.bind()

        try:
            if self.device_info is None:
                raise DeviceNotBoundError
            await self.send(self.create_status_message(self.device_info, "hid"))

        except asyncio.TimeoutError as err:
            raise DeviceTimeoutError from err

    def __eq__(self, other):
        """Compare two devices for equality based on their properties state and
        device info."""
        try:
            if not isinstance(other, BaseDevice):
                return False
            # Different device info means not equal
            if self.device_info != other.device_info:
                return False
            # Different binding state means not equal
            has_cipher = (
                hasattr(self, "device_cipher") and self.device_cipher is not None
            )
            other_has_cipher = (
                hasattr(other, "device_cipher") and other.device_cipher is not None
            )
            # When any property differs the device info is not the same
            if has_cipher != other_has_cipher:
                return False
            # If both bound, different keys means not equal
            if (
                has_cipher
                and other_has_cipher
                and self.device_cipher is not None
                and other.device_cipher is not None
                and self.device_cipher.key != other.device_cipher.key
            ):
                return False
            # Check if either device has pending property changes
            if hasattr(self, "_dirty") and self._dirty:
                return False
            if hasattr(other, "_dirty") and other._dirty:
                return False
            # Finally compare properties
            return self._properties == other._properties
        except asyncio.TimeoutError as err:
            raise DeviceTimeoutError from err

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def raw_properties(self) -> dict:
        return self._properties

    def get_property(self, name):
        """Generic lookup of properties tracked from the physical device"""
        if self._properties:
            return self._properties.get(name.value)
        return None

    def set_property(self, name, value):
        """Generic setting of properties for the physical device"""
        if not self._properties:
            self._properties = {}

        if self._properties.get(name.value) == value:
            return
        else:
            self._properties[name.value] = value
            if name.value not in self._dirty:
                self._dirty.append(name.value)

    def create_status_message(self, device_info: DeviceInfo, *args) -> dict:
        """Create a status request message."""
        self._logger.debug(f"Creating status message with args: {args}")
        message = {
            "cid": "app",
            "i": 0,
            "t": "pack",
            "uid": 0,
            "tcid": device_info.mac,
            "pack": {"mac": device_info.mac, "t": "status", "cols": list(args)},
        }
        self._logger.debug(f"Created status message: {message}")
        return message
