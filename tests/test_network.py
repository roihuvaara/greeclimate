import asyncio
import json
import socket
from threading import Thread
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from gree_versati.deviceinfo import DeviceInfo
from gree_versati.network import (
    BroadcastListenerProtocol,
    Commands,
    DeviceProtocol2,
    DeviceProtocolBase2,
    IPAddr,
    Response,
)

from .common import (
    DEFAULT_REQUEST,
    DEFAULT_RESPONSE,
    DEFAULT_TIMEOUT,
    DISCOVERY_REQUEST,
    DISCOVERY_RESPONSE,
    FakeCipher,
    Responder,
    generate_response,
)
from .test_device import get_mock_info


class FakeDiscoveryProtocol(BroadcastListenerProtocol):
    """Fake discovery class."""

    def __init__(self):
        super().__init__(timeout=1, drained=asyncio.Event())
        self.packets: asyncio.Queue = asyncio.Queue()

    def packet_received(self, obj, addr: IPAddr) -> None:
        self.packets.put_nowait(obj)


class FakeDeviceProtocol(DeviceProtocol2):
    """Fake discovery class."""

    def __init__(self, drained: asyncio.Event | None = None):
        super().__init__(timeout=1, drained=drained or asyncio.Event())
        self.packets: asyncio.Queue = asyncio.Queue()
        self.device_cipher = FakeCipher(b"1234567890123456")

    def packet_received(self, obj, addr: IPAddr) -> None:
        self.packets.put_nowait(obj)


@pytest.mark.asyncio
@pytest.mark.parametrize("addr,family", [(("127.0.0.1", 7000), socket.AF_INET)])
async def test_close_connection(addr, family):
    """Test closing the connection."""
    # Run the listener portion now
    loop = asyncio.get_event_loop()

    bcast = (addr[0], 7000)
    local_addr = (addr[0], 0)

    with patch.object(DeviceProtocolBase2, "connection_lost") as mock:
        dp2 = FakeDiscoveryProtocol()
        await loop.create_datagram_endpoint(
            lambda: dp2,
            local_addr=local_addr,
        )

        # Send the scan command
        data = DISCOVERY_REQUEST
        await dp2.send(data, bcast)
        dp2.close()

        # Wait on the scan response
        with pytest.raises(asyncio.TimeoutError):
            task = asyncio.create_task(dp2.packets.get())
            await asyncio.wait_for(task, DEFAULT_TIMEOUT)
            (response, _) = task.result()

            assert not response
            assert len(response) == 0

        assert mock.call_count == 1


@pytest.mark.asyncio
async def test_set_get_key():
    """Test the encryption key property."""
    key = "faketestkey"
    dp2 = DeviceProtocolBase2()
    dp2.device_cipher = FakeCipher(key.encode())
    assert dp2.device_cipher is not None
    # Use cast to tell pyright that device_cipher is not None here
    cipher = cast(FakeCipher, dp2.device_cipher)
    assert cipher.key == key


@pytest.mark.asyncio
@pytest.mark.parametrize("addr", [(("127.0.0.1", 7001))])
async def test_connection_error(addr):
    """Test the encryption key property."""
    dp2 = DeviceProtocolBase2()

    loop = asyncio.get_event_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: dp2,
        local_addr=addr,
    )

    # Send the scan command
    data = DISCOVERY_REQUEST
    await dp2.send(data, (addr[0], 7000))

    with pytest.raises(RuntimeError):
        dp2.connection_lost(RuntimeError())
    assert transport.is_closing()


@pytest.mark.asyncio
@pytest.mark.parametrize("addr", [(("127.0.0.1", 7001))])
async def test_pause_resume(addr):
    """Test the encryption key property."""
    event = asyncio.Event()
    dp2 = DeviceProtocolBase2(drained=event)

    loop = asyncio.get_event_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: dp2,
        local_addr=addr,
    )

    dp2.pause_writing()
    assert not event.is_set()

    dp2.resume_writing()
    assert event.is_set()

    dp2.close()
    assert transport.is_closing()


@pytest.mark.asyncio
@pytest.mark.parametrize("addr,family", [(("127.0.0.1", 7000), socket.AF_INET)])
async def test_broadcast_recv(addr, family):
    """Create a socket broadcast responder and an async broadcast listener.

    Tests discovery responses from the network.
    """
    with Responder(family, addr[1]) as sock:

        def responder(s):
            (d, addr) = s.recvfrom(2048)
            p = json.loads(d)
            assert p == DISCOVERY_REQUEST

            p = json.dumps(DISCOVERY_RESPONSE)
            s.sendto(p.encode(), addr)

        serv = Thread(target=responder, args=(sock,))
        serv.start()

        # Run the listener portion now
        loop = asyncio.get_event_loop()

        bcast = (addr[0], 7000)
        local_addr = (addr[0], 0)

        dp2 = FakeDiscoveryProtocol()
        dp2.device_cipher = FakeCipher(b"1234567890123456")
        await loop.create_datagram_endpoint(
            lambda: dp2,
            local_addr=local_addr,
        )

        # Send the scan command
        data = DISCOVERY_REQUEST
        await dp2.send(data, bcast)

        # Wait on the scan response
        task = asyncio.create_task(dp2.packets.get())
        await asyncio.wait_for(task, DEFAULT_TIMEOUT)
        response = task.result()

        assert response == DISCOVERY_RESPONSE
        serv.join(timeout=DEFAULT_TIMEOUT)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "addr,family",
    [
        (("127.0.0.1", 7000), socket.AF_INET),
    ],
)
async def test_broadcast_timeout(addr, family):
    """Create an async broadcast listener, test discovery responses."""

    # Run the listener portion now
    loop = asyncio.get_event_loop()

    bcast = (addr[0], 7000)
    local_addr = (addr[0], 0)

    dp2 = FakeDiscoveryProtocol()
    await loop.create_datagram_endpoint(
        lambda: dp2,
        local_addr=local_addr,
    )

    # Send the scan command
    await dp2.send(DISCOVERY_REQUEST, bcast)

    # Wait on the scan response
    task = asyncio.create_task(dp2.packets.get())
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(task, DEFAULT_TIMEOUT)

    with pytest.raises(asyncio.CancelledError):
        response = task.result()
        assert len(response) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("addr,family", [(("127.0.0.1", 7000), socket.AF_INET)])
async def test_datagram_connect(addr, family):
    """Create a socket responder, an async connection, test send and recv."""
    with Responder(family, addr[1], bcast=False) as sock:

        def responder(s):
            (d, addr) = s.recvfrom(2048)
            p = json.dumps(DEFAULT_RESPONSE)
            s.sendto(p.encode(), addr)

        serv = Thread(target=responder, args=(sock,))
        serv.start()

        # Run the listener portion now
        loop = asyncio.get_event_loop()
        drained = asyncio.Event()

        remote_addr = (addr[0], 7000)
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: FakeDeviceProtocol(drained=drained), remote_addr=remote_addr
        )

        # Send the scan command
        cipher = FakeCipher(b"1234567890123456")
        await protocol.send(DEFAULT_REQUEST, remote_addr, cipher)

        # Wait on the scan response
        task = asyncio.create_task(protocol.packets.get())
        await asyncio.wait_for(task, DEFAULT_TIMEOUT)
        response = task.result()

        assert response == DEFAULT_RESPONSE

        sock.close()
        serv.join(timeout=DEFAULT_TIMEOUT)


def test_bindok_handling():
    """Test the bindok response."""
    response = generate_response({"t": "bindok", "key": "fake-key"})
    protocol = DeviceProtocol2(timeout=DEFAULT_TIMEOUT)
    protocol.device_cipher = FakeCipher(b"1234567890123456")

    with patch.object(DeviceProtocol2, "handle_device_bound") as mock:
        protocol.datagram_received(json.dumps(
            response).encode(), ("0.0.0.0", 0))
        assert mock.call_count == 1
        assert mock.call_args[0][0] == "fake-key"


def test_create_bind_message():
    # Arrange
    device_info = DeviceInfo(*get_mock_info())
    protocol = DeviceProtocol2()

    # Act
    result = protocol.create_bind_message(device_info)

    # Assert
    assert isinstance(result, dict)
    assert result == {
        "cid": "app",
        "i": 1,  # Default key encryption
        "t": "pack",
        "uid": 0,
        "tcid": device_info.mac,
        "pack": {"t": "bind", "mac": device_info.mac, "uid": 0},
    }


def test_create_status_message():
    # Arrange
    device_info = DeviceInfo(*get_mock_info())
    protocol = DeviceProtocol2()

    # Act
    result = protocol.create_status_message(device_info, "test")

    # Assert
    assert isinstance(result, dict)
    assert result == {
        "cid": "app",
        "i": 0,  # Device key encryption
        "t": "pack",
        "uid": 0,
        "tcid": device_info.mac,
        "pack": {
            "t": "status",
            "mac": device_info.mac,
            "cols": ["test"],
        },
    }


def test_create_command_message():
    # Arrange
    device_info = DeviceInfo(*get_mock_info())
    protocol = DeviceProtocol2()

    # Act
    result = protocol.create_command_message(device_info, **{"key": "value"})

    # Assert
    assert isinstance(result, dict)
    assert result == {
        "cid": "app",
        "i": 0,  # Device key encryption
        "t": "pack",
        "uid": 0,
        "tcid": device_info.mac,
        "pack": {
            "t": "cmd",
            "mac": device_info.mac,
            "opt": ["key"],
            "p": ["value"],
        },
    }


class DeviceProtocol2Test(DeviceProtocol2):
    def __init__(self):
        super().__init__(timeout=DEFAULT_TIMEOUT)
        self.state = {}
        self.key = None
        self.unknown = False

    def handle_state_update(self, **kwargs) -> None:
        self.state = dict(kwargs)

    def handle_device_bound(self, key: str) -> None:
        self._ready.set()
        self.key = key

    def handle_unknown_packet(self, obj, addr: IPAddr) -> None:
        self.unknown = True


def test_handle_state_update():
    # Arrange
    protocol = DeviceProtocol2Test()
    state = {"key": "value"}

    # Act
    protocol.packet_received(
        {"pack": {"t": "dat", "cols": list(
            state.keys()), "dat": list(state.values())}},
        ("0.0.0.0", 0),
    )

    # Assert
    assert protocol.state == state
    assert protocol.state == {"key": "value"}


def test_handle_result_update():
    # Arrange
    protocol = DeviceProtocol2Test()
    state = {"key": "value"}

    # Act
    protocol.packet_received(
        {"pack": {"t": "res", "opt": list(
            state.keys()), "val": list(state.values())}},
        ("0.0.0.0", 0),
    )

    # Assert
    assert protocol.state == state
    assert protocol.state == {"key": "value"}


def test_handle_device_bound():
    # Arrange
    protocol = DeviceProtocol2Test()

    # Act
    protocol.packet_received(
        {"pack": {"t": "bindok", "key": "fake-key"}}, ("0.0.0.0", 0)
    )

    # Assert
    assert protocol._ready.is_set()
    assert protocol.key == "fake-key"


def test_handle_unknown_packet():
    # Arrange
    protocol = DeviceProtocol2Test()

    # Act
    protocol.packet_received({"pack": {"t": "unknown"}}, ("0.0.0.0", 0))

    # Assert
    assert protocol.unknown is True


@pytest.mark.parametrize(
    "use_default_key,command,data",
    [
        (1, Commands.BIND, {"uid": 0}),
        (1, Commands.SCAN, None),
        (0, Commands.STATUS, {"cols": ["test"]}),
        (0, Commands.CMD, {"opt": ["key"], "p": ["value"]}),
    ],
)
def test_generate_payload(use_default_key, command, data):
    # Arrange
    device_info = DeviceInfo(*get_mock_info())
    protocol = DeviceProtocol2()

    # Act
    result = protocol._generate_payload(command, device_info, data)

    # Assert
    expected = {
        "cid": "app",
        "i": use_default_key,  # Device key encryption
        "t": Commands.PACK.value if data is not None else command.value,
        "uid": 0,
        "tcid": device_info.mac,
    }
    if data:
        expected["pack"] = {"t": command.value, "mac": device_info.mac}
        expected["pack"].update(data)

    assert isinstance(result, dict)
    assert result == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_name, data",
    [
        (Response.BIND_OK, {"key": "fake-key"}),
        (Response.DATA, {"cols": ["test"], "dat": ["value"]}),
        (Response.RESULT, {"opt": ["key"], "val": ["value"]}),
    ],
)
async def test_add_and_remove_handler(event_name, data):
    # Arrange
    protocol = DeviceProtocol2()
    callback = MagicMock()
    event_data = {"pack": {"t": event_name.value}}
    event_data["pack"].update(data)

    # Act
    protocol.add_handler(event_name, callback)

    # Assert that the handler was added
    assert event_name in protocol._handlers
    assert callback in protocol._handlers[event_name]

    # Trigger the event
    protocol.packet_received(event_data, ("0.0.0.0", 0))

    # Check that the callback was called
    callback.assert_called_once()

    # Now remove the handler
    protocol.remove_handler(event_name, callback)

    # Assert that the handler was removed
    assert callback not in protocol._handlers[event_name]

    # Reset the callback
    callback.reset_mock()

    # Trigger the event again
    protocol.packet_received(event_data, ("0.0.0.0", 0))

    # Check that the callback was not called this time
    callback.assert_not_called()


def test_packet_received_not_implemented():
    # Arrange
    protocol = DeviceProtocolBase2()

    # Act
    with pytest.raises(NotImplementedError):
        protocol.packet_received({}, ("0.0.0.0", 0))


def test_packet_received_invalid_data():
    # Arrange
    protocol = DeviceProtocol2()

    # Act
    protocol.packet_received(None, ("0.0.0.0", 0))
    protocol.packet_received({}, ("0.0.0.0", 0))
    protocol.packet_received({"pack"}, ("0.0.0.0", 0))

    with patch.object(protocol, "handle_unknown_packet") as mock:
        protocol.packet_received({"pack": {"t": "unknown"}}, ("0.0.0.0", 0))
        mock.assert_called_once()


def test_set_get_cipher():
    # Arrange
    protocol = DeviceProtocolBase2()
    cipher = FakeCipher(b"1234567890123456")

    # Act
    protocol.device_cipher = cipher

    # Assert
    assert protocol.device_cipher == cipher


def test_cipher_is_not_set():
    # Arrange
    protocol = DeviceProtocolBase2()

    # Act
    key = None
    with pytest.raises(ValueError):
        key = protocol.device_key

    assert key is None

    with pytest.raises(ValueError):
        protocol.device_key = "fake-key"


def test_add_invalid_handler():
    # Arrange
    protocol = DeviceProtocol2()
    callback = MagicMock()

    # Act
    with pytest.raises(ValueError):
        protocol.add_handler(Response("invalid"), callback)

    with pytest.raises(ValueError):
        protocol.add_handler(Response("invalid"), callback)


def test_device_key_get_set():
    # Arrange
    protocol = DeviceProtocolBase2
    key = "fake-key"

    # Act
    protocol.device_key = key

    # Assert
    assert protocol.device_key == key


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response",
    [
        # Test data response
        {
            "pack": {
                "t": "dat",
                "cols": ["test"],
                "dat": ["value"]
            }
        },
        # Test bind response
        {
            "pack": {
                "t": "bindok",
                "key": "fake-key"
            }
        },
        # Test result response
        {
            "pack": {
                "t": "res",
                "opt": ["test"],
                "val": ["value"]
            }
        },
        # Test unknown response type
        {
            "pack": {
                "t": "unknown"
            }
        },
        # Test invalid response (no pack)
        {
            "invalid": "data"
        },
        # Test invalid response (no t in pack)
        {
            "pack": {
                "invalid": "data"
            }
        }
    ]
)
async def test_drained_event_set_after_response(response):
    """Test that the _drained event is set after receiving a response.

    Tests various response types and error cases to ensure _drained is always set.
    """
    # Arrange
    protocol = DeviceProtocol2()
    protocol.device_cipher = FakeCipher(b"1234567890123456")

    # Clear the drained event (it's set in __init__)
    protocol._drained.clear()

    # Act
    protocol.packet_received(response, ("0.0.0.0", 0))

    # Assert
    assert protocol._drained.is_set()
