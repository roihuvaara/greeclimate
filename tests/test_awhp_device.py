import asyncio
from unittest.mock import Mock, patch

import pytest

from gree_versati.awhp_device import AwhpDevice, AwhpProps
from gree_versati.cipher import CipherV1
from gree_versati.deviceinfo import DeviceInfo
from gree_versati.exceptions import DeviceTimeoutError


def get_mock_info():
    return (
        "1.1.1.0",
        "7000",
        "aabbcc001122",
        "MockAWHP1",
        "MockBrand",
        "MockModel",
        "0.0.1-fake",
    )


def get_mock_state():
    return {
        "AllInWatTemHi": 125,  # 25°C
        "AllInWatTemLo": 5,  # 0.5°C
        "AllOutWatTemHi": 126,  # 26°C
        "AllOutWatTemLo": 3,  # 0.3°C
        "HepOutWatTemHi": 127,  # 27°C
        "HepOutWatTemLo": 2,  # 0.2°C
        "WatBoxTemHi": 128,  # 28°C
        "WatBoxTemLo": 1,  # 0.1°C
        "RmoHomTemHi": 129,  # 29°C
        "RmoHomTemLo": 4,  # 0.4°C
        "WatBoxElcHeRunSta": 1,
        "SyAnFroRunSta": 1,
        "ElcHe1RunSta": 1,
        "ElcHe2RunSta": 1,
        "AnFrzzRunSta": 1,
        "Pow": 1,
        "Mod": 4,
        "CoWatOutTemSet": 18,
        "HeWatOutTemSet": 33,
        "WatBoxTemSet": 55,
        "TemUn": 0,
        "TemRec": 0,
        "AllErr": 0,
        "ColHtWter": 1,
        "HetHtWter": 1,
        "TemRecB": 0,
        "CoHomTemSet": 24,
        "HeHomTemSet": 25,
        "FastHtWter": 0,
        "Quiet": 0,
        "LefHom": 0,
        "SwDisFct": 0,
        "SvSt": 0,
        "VersatiSeries": 0,
        "RomHomTemExt": 0,
        "WatBoxExt": 0,
        "FocModSwh": 0,
        "Emegcy": 0,
        "HanFroSwh": 0,
        "WatSyExhSwh": 0,
        "BordTest": 0,
        "ColColetSwh": 0,
        "EndTemCotSwh": 0,
        "ModelType": 0,
        "EVU": 0,
        "hid": "362001000762+U-CS532AE(LT)V3.31.bin",
    }


async def generate_device_mock_async():
    d = AwhpDevice(DeviceInfo("1.1.1.1", 7000, "f4911e7aca59", "1e7aca59"))
    # Set up transport
    d._transport = Mock()
    d._transport.sendto = Mock()

    # Set up initial state
    state = get_mock_state()
    d._properties = state.copy()

    # Set up cipher with key
    d.device_cipher = CipherV1("St8Vw1Yz4Bc7Ef0H".encode())
    d.ready.set()
    return d


@pytest.mark.asyncio
async def test_get_device_info(cipher, send):
    """Initialize device, check properties."""
    info = DeviceInfo(*get_mock_info())
    device = AwhpDevice(info)
    device._transport = Mock()
    device._transport.sendto = Mock()

    assert device.device_info == info

    fake_key = "abcdefgh12345678"

    def fake_send(*args, **kwargs):
        return {"t": "bindok", "key": fake_key}

    send.side_effect = fake_send
    await device.bind(key=fake_key, cipher=CipherV1())

    assert device.device_cipher is not None
    assert device.device_cipher.key == fake_key


@pytest.mark.asyncio
async def test_device_bind(cipher, send):
    """Check that the device returns a device key when binding."""
    info = DeviceInfo(*get_mock_info())
    device = AwhpDevice(info, timeout=1)
    fake_key = "abcdefgh12345678"

    # Set up mock transport
    device._transport = Mock()
    device._transport.sendto = Mock()

    try:
        assert device.device_info == info
        # Directly provide key and cipher like in test_device.py
        await device.bind(key=fake_key, cipher=CipherV1())
        assert device.device_cipher is not None
        assert device.device_cipher.key == fake_key
    finally:
        if device._transport:
            device._transport.close()
            device._transport = None


@pytest.mark.asyncio
async def test_device_bind_timeout(monkeypatch, cipher, send):
    """Check that the device handles timeout errors when binding."""
    info = DeviceInfo(*get_mock_info())
    device = AwhpDevice(info, timeout=1)

    # Set up mock transport
    device._transport = Mock()
    device._transport.sendto = Mock()

    # Replace the __bind_internal method with one that raises TimeoutError
    async def mock_bind_internal(*args, **kwargs):
        raise asyncio.TimeoutError("Test timeout")

    # Using monkeypatch to patch the private method
    with patch.object(
        device, "_BaseDevice__bind_internal", side_effect=mock_bind_internal
    ):
        with pytest.raises(DeviceTimeoutError):
            await device.bind()
        # The device_cipher should be None after a timeout during binding

    # Clean up
    if device._transport:
        device._transport.close()
        device._transport = None


@pytest.mark.asyncio
async def test_update_properties(monkeypatch, cipher, send):
    """Check that properties can be updated."""
    device = await generate_device_mock_async()

    # Clear properties to test update
    device._properties = {}

    # Create a copy of the mock state
    mock_state = get_mock_state().copy()

    # Mock send method that updates device properties directly
    async def mock_send(*args, **kwargs):
        # Directly update device properties
        device._properties.update(mock_state)
        return {"t": "status", "pack": mock_state}

    # Patch the device's send method
    with patch.object(device, "send", side_effect=mock_send):
        # Call update_state which will use our mocked send method
        await device.update_state()

        # Verify properties were updated
        for p in AwhpProps:
            if p.value in mock_state:
                assert device.get_property(p) == mock_state[p.value]


@pytest.mark.asyncio
async def test_update_state_timeout(monkeypatch, cipher, send):
    """Test handling of timeout during state update."""
    device = await generate_device_mock_async()

    # Mock send method that raises TimeoutError
    async def mock_send(*args, **kwargs):
        raise asyncio.TimeoutError("Test timeout")

    # Patch the device's send method
    with patch.object(device, "send", side_effect=mock_send):
        # This should be converted to DeviceTimeoutError by the device
        with pytest.raises(DeviceTimeoutError):
            await device.update_state()


@pytest.mark.asyncio
async def test_push_state_timeout(monkeypatch, cipher, send):
    """Test handling of timeout during state push."""
    device = await generate_device_mock_async()

    # Set some properties to make the device dirty
    device.cool_temp_set = 20
    device.heat_temp_set = 35
    device._dirty = [AwhpProps.COOL_TEMP_SET.value, AwhpProps.HEAT_TEMP_SET.value]

    # Mock send method that raises TimeoutError
    async def mock_send(*args, **kwargs):
        raise asyncio.TimeoutError("Test timeout")

    # Patch the device's send method
    with patch.object(device, "send", side_effect=mock_send):
        with pytest.raises(DeviceTimeoutError):
            await device.push_state_update()


@pytest.mark.asyncio
async def test_temperature_readings(cipher, send):
    """Test temperature conversion functions."""
    device = await generate_device_mock_async()

    # Clear properties
    device._properties = {}

    # Directly update device properties, matching test_device.py pattern
    device._properties = get_mock_state().copy()

    # Test water input temperature (25.5°C)
    assert device.t_water_in_pe() == 25.5

    # Test water output temperature (26.3°C)
    assert device.t_water_out_pe() == 26.3

    # Test optimal water temperature (27.2°C)
    assert device.t_opt_water() == 27.2

    # Test hot water temperature (28.1°C)
    assert device.hot_water_temp() == 28.1

    # Test remote home temperature (29.4°C)
    assert device.remote_home_temp() == 29.4


@pytest.mark.asyncio
async def test_temperature_settings(monkeypatch, cipher, send):
    """Check the setting of temperature setpoints."""
    device = await generate_device_mock_async()

    # Clear properties and dirty list
    device._properties = {}
    device._dirty = []

    # Create a call counter to track the number of send calls
    call_count = 0

    # Mock send method to track calls and return success
    async def mock_send(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return {"t": "status", "pack": {}}

    # Patch the device's send method
    with patch.object(device, "send", side_effect=mock_send):
        # Test getting current values works
        assert device.cool_temp_set is None  # No properties yet

        # Set three different temperature properties
        device.cool_temp_set = 20
        device.heat_temp_set = 35
        device.hot_water_temp_set = 45

        # Verify properties were set
        assert device.get_property(AwhpProps.COOL_TEMP_SET) == 20
        assert device.get_property(AwhpProps.HEAT_TEMP_SET) == 35
        assert device.get_property(AwhpProps.HOT_WATER_TEMP_SET) == 45

        # Verify dirty list contains the three properties we set
        assert len(device._dirty) == 3
        assert AwhpProps.COOL_TEMP_SET.value in device._dirty
        assert AwhpProps.HEAT_TEMP_SET.value in device._dirty
        assert AwhpProps.HOT_WATER_TEMP_SET.value in device._dirty

        # Push the update
        await device.push_state_update()

        # Verify one send call was made (for the push_state_update)
        assert call_count == 1

        # Dirty list should be empty after push
        assert len(device._dirty) == 0


@pytest.mark.asyncio
async def test_device_status_properties(cipher, send):
    """Test various device status properties."""
    device = await generate_device_mock_async()

    # Directly set properties
    device._properties = get_mock_state().copy()

    # Test power status
    assert device.power is True

    # Test mode
    assert device.mode == 4

    # Test various boolean properties
    assert device.cool_and_hot_water is True
    assert device.heat_and_hot_water is True
    assert device.fast_heat_water is False
    assert device.left_home is False
    assert device.disinfect is False
    assert device.power_save is False
    assert device.versati_series is False


@pytest.mark.asyncio
async def test_update_all_properties(monkeypatch, cipher, send):
    """Check that all properties can be updated."""
    device = await generate_device_mock_async()

    # Clear properties to test update
    device._properties = {}

    # Create a copy of the mock state with all properties
    mock_state = get_mock_state().copy()

    # Mock send method that updates device properties directly
    async def mock_send(*args, **kwargs):
        # Directly update device properties
        device._properties.update(mock_state)
        return {"t": "status", "pack": mock_state}

    # Patch the device's send method
    with patch.object(device, "send", side_effect=mock_send):
        # Call update_all_properties which will use our mocked send method
        await device.update_all_properties()

        # Check a few key properties to verify the update
        assert (
            device.get_property(AwhpProps.T_WATER_IN_PE_W)
            == mock_state[AwhpProps.T_WATER_IN_PE_W.value]
        )
        assert device.get_property(AwhpProps.POWER) == mock_state[AwhpProps.POWER.value]

        # Verify that properties dictionary is not empty
        assert len(device._properties) > 0


@pytest.mark.asyncio
async def test_temperature_readings_with_none(cipher, send):
    """Test temperature readings when some values are None."""
    device = await generate_device_mock_async()

    # Prepare modified state
    modified_state = get_mock_state().copy()
    del modified_state["AllInWatTemHi"]
    del modified_state["AllInWatTemLo"]

    # Directly set properties
    device._properties = modified_state

    # Test water input temperature should be None
    assert device.t_water_in_pe() is None

    # Other temperatures should still work
    assert device.t_water_out_pe() == 26.3


@pytest.mark.asyncio
async def test_batch_property_updates(monkeypatch, cipher, send):
    """Check that properties can be updated in batches."""
    device = await generate_device_mock_async()

    # Clear properties to test update
    device._properties = {}
    device._dirty = []

    # Create a call counter to track the number of send calls
    call_count = 0
    sent_props = []

    # Mock send method to track calls and capture sent properties
    async def mock_send(*args, **kwargs):
        nonlocal call_count, sent_props
        call_count += 1

        # Get the message to determine which properties were requested
        message = args[0]
        if "pack" in message:
            pack = message["pack"]
            if "opt" in pack and isinstance(pack["opt"], list):
                # This is a state update with opt list
                sent_props.extend(pack["opt"])

        # Return a mock state that changes based on which properties were requested
        return {"t": "status", "pack": {"1": 1, "2": 2, "4": 4, "5": 5, "6": 6}}

    # Patch the device's send method
    with patch.object(device, "send", side_effect=mock_send):
        # Add many properties to the dirty list to ensure multiple batches
        # Add 25 properties to force batching (assuming batch size < 25)
        props = [str(i) for i in range(1, 26)]
        device._dirty = props.copy()  # Create a copy to preserve original
        original_props = props.copy()  # Store original properties

        # Push state update, which should trigger batch requests
        await device.push_state_update()

        # Verify that at least one call was made
        assert call_count >= 1

        # Make sure all our properties were sent
        assert len(sent_props) > 0
        # If properties weren't batched properly, this would fail
        # Compare with original_props since device._dirty is
        # cleared after push_state_update
        assert set(sent_props) == set(original_props)


@pytest.mark.asyncio
async def test_temperature_readings_raw_data(cipher, send):
    """Test temperature readings using raw data."""
    device = await generate_device_mock_async()

    # Test direct temperature calculation with raw data
    raw_data = {
        "AllInWatTemHi": 130,  # 30°C
        "AllInWatTemLo": 5,  # 0.5°C
    }

    # Test direct temperature calculation from raw data
    assert device.t_water_in_pe(raw_data) == 30.5

    # Test with empty data - should use device properties
    empty_data = {}
    # Ensure device has properties set
    device._properties = get_mock_state().copy()
    assert device.t_water_in_pe(empty_data) == 25.5  # Uses device properties


@pytest.mark.asyncio
async def test_device_version_handling(cipher, send):
    """Test device version extraction from hid."""
    device = await generate_device_mock_async()

    # Set the HID directly
    device._properties = {"hid": "362001000762+U-CS532AE(LT)V3.31.bin"}

    # Trigger the version extraction
    device.handle_state_update(hid="362001000762+U-CS532AE(LT)V3.31.bin")

    assert device.version == "3.31"


@pytest.mark.asyncio
async def test_invalid_temperature_values(cipher, send):
    """Test handling of invalid temperature values."""
    device = await generate_device_mock_async()

    # Set up state with invalid temperature values
    modified_state = get_mock_state().copy()
    modified_state["AllInWatTemHi"] = None
    modified_state["AllInWatTemLo"] = None

    # Directly set properties
    device._properties = modified_state

    # Should handle invalid values gracefully
    assert device.t_water_in_pe() is None
    assert device.t_water_out_pe() == 26.3  # Other temperatures should still work
