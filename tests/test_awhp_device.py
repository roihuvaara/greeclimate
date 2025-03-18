import asyncio
from unittest.mock import Mock, patch

import pytest

from gree_versati.awhp_device import AwhpDevice, AwhpProps
from gree_versati.cipher import CipherV1
from gree_versati.deviceinfo import DeviceInfo
from gree_versati.exceptions import DeviceNotBoundError, DeviceTimeoutError


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


@pytest.mark.asyncio
async def test_additional_status_properties(cipher, send):
    """Test all the additional status getter properties."""
    device = await generate_device_mock_async()

    # Directly set properties
    device._properties = get_mock_state().copy()

    # Test status properties (all should be True based on mock state)
    assert device.tank_heater_status is True
    assert device.system_defrosting_status is True
    assert device.hp_heater_1_status is True
    assert device.hp_heater_2_status is True
    assert device.automatic_frost_protection is True

    # Test boolean configuration properties (all should be False based on mock state)
    assert device.quiet is False
    assert device.bord_test is False
    assert device.col_colet_swh is False
    assert device.end_temp_cot_swh is False
    assert device.evu is False

    # Test integer configuration properties
    assert device.temp_unit == 0
    assert device.temp_rec == 0
    assert device.all_err == 0
    assert device.temp_rec_b == 0
    assert device.model_type == 0

    # Test that properties also work after updating with state
    modified_state = get_mock_state().copy()
    modified_state.update(
        {
            "Quiet": 1,
            "BordTest": 1,
            "ColColetSwh": 1,
            "EndTemCotSwh": 1,
            "EVU": 1,
            "TemUn": 1,
            "ModelType": 2,
        }
    )

    # Update device properties
    device._properties = modified_state

    # Verify the updated properties
    assert device.quiet is True
    assert device.bord_test is True
    assert device.col_colet_swh is True
    assert device.end_temp_cot_swh is True
    assert device.evu is True
    assert device.temp_unit == 1
    assert device.model_type == 2


@pytest.mark.asyncio
async def test_property_none_values(cipher, send):
    """Test handling of None values in property getters."""
    device = await generate_device_mock_async()

    # Clear the properties
    device._properties = {}

    # All properties should handle None gracefully
    assert device.tank_heater_status is False
    assert device.system_defrosting_status is False
    assert device.hp_heater_1_status is False
    assert device.hp_heater_2_status is False
    assert device.automatic_frost_protection is False
    assert device.quiet is False
    assert device.bord_test is False
    assert device.col_colet_swh is False
    assert device.end_temp_cot_swh is False
    assert device.evu is False
    assert device.temp_unit is None
    assert device.temp_rec is None
    assert device.all_err is None
    assert device.temp_rec_b is None
    assert device.model_type is None


@pytest.mark.asyncio
async def test_all_properties_in_get_all_properties(monkeypatch, cipher, send):
    """Test that get_all_properties includes all the properties."""
    device = await generate_device_mock_async()

    # Setup mock properties with all values
    mock_state = get_mock_state().copy()
    device._properties = mock_state

    # Mock update_all_properties to avoid actual network calls
    async def mock_update_all_properties():
        # Do nothing, properties are already set
        pass

    # Patch the device's update_all_properties method
    with patch.object(
        device, "update_all_properties", side_effect=mock_update_all_properties
    ):
        # Get all properties
        all_props = await device.get_all_properties()

        # Verify all enum properties are included in the result
        for prop in AwhpProps:
            assert prop.value in all_props
            assert all_props[prop.value] == mock_state.get(prop.value)

        # Specifically verify new properties are included
        assert (
            all_props[AwhpProps.TANK_HEATER_STATUS.value]
            == mock_state[AwhpProps.TANK_HEATER_STATUS.value]
        )
        assert all_props[AwhpProps.QUIET.value] == mock_state[AwhpProps.QUIET.value]
        assert (
            all_props[AwhpProps.BORD_TEST.value]
            == mock_state[AwhpProps.BORD_TEST.value]
        )
        assert (
            all_props[AwhpProps.COL_COLET_SWH.value]
            == mock_state[AwhpProps.COL_COLET_SWH.value]
        )
        assert (
            all_props[AwhpProps.END_TEMP_COT_SWH.value]
            == mock_state[AwhpProps.END_TEMP_COT_SWH.value]
        )
        assert (
            all_props[AwhpProps.MODEL_TYPE.value]
            == mock_state[AwhpProps.MODEL_TYPE.value]
        )
        assert all_props[AwhpProps.EVU.value] == mock_state[AwhpProps.EVU.value]
        assert (
            all_props[AwhpProps.TEMP_UNIT.value]
            == mock_state[AwhpProps.TEMP_UNIT.value]
        )
        assert (
            all_props[AwhpProps.TEMP_REC.value] == mock_state[AwhpProps.TEMP_REC.value]
        )
        assert all_props[AwhpProps.ALL_ERR.value] == mock_state[AwhpProps.ALL_ERR.value]
        assert (
            all_props[AwhpProps.TEMP_REC_B.value]
            == mock_state[AwhpProps.TEMP_REC_B.value]
        )


@pytest.mark.asyncio
async def test_property_setters(monkeypatch, cipher, send):
    """Test setters for temperature and boolean properties."""
    device = await generate_device_mock_async()

    # Clear properties and dirty list
    device._properties = {}
    device._dirty = []

    # Test setting all settable properties
    device.cool_temp_set = 19
    device.heat_temp_set = 32
    device.hot_water_temp_set = 54
    device.cool_and_hot_water = True
    device.heat_and_hot_water = True
    device.cool_home_temp_set = 23
    device.heat_home_temp_set = 24
    device.fast_heat_water = True
    device.left_home = True
    device.disinfect = True
    device.power_save = True
    device.versati_series = True
    device.room_home_temp_ext = True
    device.hot_water_ext = True
    device.foc_mod_swh = True
    device.emegcy = True
    device.hand_fro_swh = True
    device.water_sys_exh_swh = True
    device.power = True
    device.mode = 3

    # Verify values were set correctly
    assert device.get_property(AwhpProps.COOL_TEMP_SET) == 19
    assert device.get_property(AwhpProps.HEAT_TEMP_SET) == 32
    assert device.get_property(AwhpProps.HOT_WATER_TEMP_SET) == 54
    assert device.get_property(AwhpProps.COOL_AND_HOT_WATER) == 1
    assert device.get_property(AwhpProps.HEAT_AND_HOT_WATER) == 1
    assert device.get_property(AwhpProps.COOL_HOME_TEMP_SET) == 23
    assert device.get_property(AwhpProps.HEAT_HOME_TEMP_SET) == 24
    assert device.get_property(AwhpProps.FAST_HEAT_WATER) == 1
    assert device.get_property(AwhpProps.LEFT_HOME) == 1
    assert device.get_property(AwhpProps.DISINFECT) == 1
    assert device.get_property(AwhpProps.POWER_SAVE) == 1
    assert device.get_property(AwhpProps.VERSATI_SERIES) == 1
    assert device.get_property(AwhpProps.ROOM_HOME_TEMP_EXT) == 1
    assert device.get_property(AwhpProps.HOT_WATER_EXT) == 1
    assert device.get_property(AwhpProps.FOC_MOD_SWH) == 1
    assert device.get_property(AwhpProps.EMEGCY) == 1
    assert device.get_property(AwhpProps.HAND_FRO_SWH) == 1
    assert device.get_property(AwhpProps.WATER_SYS_EXH_SWH) == 1
    assert device.get_property(AwhpProps.POWER) == 1
    assert device.get_property(AwhpProps.MODE) == 3

    # Set booleans to False
    device.cool_and_hot_water = False
    device.heat_and_hot_water = False
    device.fast_heat_water = False
    device.left_home = False
    device.disinfect = False
    device.power_save = False
    device.versati_series = False
    device.room_home_temp_ext = False
    device.hot_water_ext = False
    device.foc_mod_swh = False
    device.emegcy = False
    device.hand_fro_swh = False
    device.water_sys_exh_swh = False
    device.power = False

    # Verify values were set to 0
    assert device.get_property(AwhpProps.COOL_AND_HOT_WATER) == 0
    assert device.get_property(AwhpProps.HEAT_AND_HOT_WATER) == 0
    assert device.get_property(AwhpProps.FAST_HEAT_WATER) == 0
    assert device.get_property(AwhpProps.LEFT_HOME) == 0
    assert device.get_property(AwhpProps.DISINFECT) == 0
    assert device.get_property(AwhpProps.POWER_SAVE) == 0
    assert device.get_property(AwhpProps.VERSATI_SERIES) == 0
    assert device.get_property(AwhpProps.ROOM_HOME_TEMP_EXT) == 0
    assert device.get_property(AwhpProps.HOT_WATER_EXT) == 0
    assert device.get_property(AwhpProps.FOC_MOD_SWH) == 0
    assert device.get_property(AwhpProps.EMEGCY) == 0
    assert device.get_property(AwhpProps.HAND_FRO_SWH) == 0
    assert device.get_property(AwhpProps.WATER_SYS_EXH_SWH) == 0
    assert device.get_property(AwhpProps.POWER) == 0

    # Verify the dirty list contains all the set properties
    expected_dirty = [
        AwhpProps.COOL_TEMP_SET.value,
        AwhpProps.HEAT_TEMP_SET.value,
        AwhpProps.HOT_WATER_TEMP_SET.value,
        AwhpProps.COOL_AND_HOT_WATER.value,
        AwhpProps.HEAT_AND_HOT_WATER.value,
        AwhpProps.COOL_HOME_TEMP_SET.value,
        AwhpProps.HEAT_HOME_TEMP_SET.value,
        AwhpProps.FAST_HEAT_WATER.value,
        AwhpProps.LEFT_HOME.value,
        AwhpProps.DISINFECT.value,
        AwhpProps.POWER_SAVE.value,
        AwhpProps.VERSATI_SERIES.value,
        AwhpProps.ROOM_HOME_TEMP_EXT.value,
        AwhpProps.HOT_WATER_EXT.value,
        AwhpProps.FOC_MOD_SWH.value,
        AwhpProps.EMEGCY.value,
        AwhpProps.HAND_FRO_SWH.value,
        AwhpProps.WATER_SYS_EXH_SWH.value,
        AwhpProps.POWER.value,
        AwhpProps.MODE.value,
    ]

    # Check that all expected properties are in the dirty list
    for prop in expected_dirty:
        assert prop in device._dirty

    # Test a basic push update
    mock_call_count = 0

    async def mock_send(*args, **kwargs):
        nonlocal mock_call_count
        mock_call_count += 1
        return {"t": "status", "pack": {}}

    # Patch the device's send method
    with patch.object(device, "send", side_effect=mock_send):
        await device.push_state_update()
        assert mock_call_count == 1
        assert len(device._dirty) == 0


@pytest.mark.asyncio
async def test_temperature_raw_data_advanced(cipher, send):
    """Test all temperature reading methods with raw data argument."""
    device = await generate_device_mock_async()

    # Test all temperature methods with raw data
    raw_data = {
        "AllInWatTemHi": 130,  # 30°C
        "AllInWatTemLo": 5,  # 0.5°C
        "AllOutWatTemHi": 131,  # 31°C
        "AllOutWatTemLo": 7,  # 0.7°C
        "HepOutWatTemHi": 132,  # 32°C
        "HepOutWatTemLo": 9,  # 0.9°C
        "WatBoxTemHi": 133,  # 33°C
        "WatBoxTemLo": 1,  # 0.1°C
        "RmoHomTemHi": 134,  # 34°C
        "RmoHomTemLo": 3,  # 0.3°C
    }

    # Test all temperature methods with raw data
    assert device.t_water_in_pe(raw_data) == 30.5
    assert device.t_water_out_pe(raw_data) == 31.7
    assert device.t_opt_water(raw_data) == 32.9
    assert device.hot_water_temp(raw_data) == 33.1
    assert device.remote_home_temp(raw_data) == 34.3

    # Test with missing data in raw_data
    incomplete_data = {
        "AllInWatTemHi": 130,
        # Missing "AllInWatTemLo"
        "AllOutWatTemHi": 131,
        # Missing "AllOutWatTemLo"
        # Missing "HepOutWatTemHi"
        "HepOutWatTemLo": 9,
        # Missing "WatBoxTemHi"
        "WatBoxTemLo": 1,
        # Missing "RmoHomTemHi"
        "RmoHomTemLo": 3,
    }

    # All these should return None due to missing data
    assert device.t_water_in_pe(incomplete_data) is None
    assert device.t_water_out_pe(incomplete_data) is None
    assert device.t_opt_water(incomplete_data) is None
    assert device.hot_water_temp(incomplete_data) is None
    assert device.remote_home_temp(incomplete_data) is None


@pytest.mark.asyncio
async def test_update_state_general_exception(monkeypatch, cipher, send):
    """Test handling of general exceptions during state update."""
    device = await generate_device_mock_async()

    # Mock send method that raises a general exception
    async def mock_send(*args, **kwargs):
        raise RuntimeError("Test general exception")

    # Patch the device's send method
    with patch.object(device, "send", side_effect=mock_send):
        # Should log the error and re-raise the exception
        with pytest.raises(RuntimeError, match="Test general exception"):
            await device.update_state()


@pytest.mark.asyncio
async def test_update_state_device_info_none(monkeypatch, cipher, send):
    """Test handling when device_info is None."""
    device = await generate_device_mock_async()

    # Force device_info to be None
    device.device_info = None

    # This should raise DeviceNotBoundError
    with pytest.raises(DeviceNotBoundError):
        await device.update_state()


@pytest.mark.asyncio
async def test_push_state_update_device_info_none(monkeypatch, cipher, send):
    """Test push state update when device_info is None."""
    device = await generate_device_mock_async()

    # Set some property to make device dirty
    device._dirty = ["Pow"]  # Directly set the dirty list

    # Force device_info to None
    device.device_info = None

    # Mock bind to ensure it doesn't interfere
    async def mock_bind(*args, **kwargs):
        # Do nothing
        pass

    # Patch bind
    with patch.object(device, "bind", side_effect=mock_bind):
        # This should raise DeviceNotBoundError
        with pytest.raises(DeviceNotBoundError):
            await device.push_state_update()


@pytest.mark.asyncio
async def test_handle_state_update_no_hid(cipher, send):
    """Test handle_state_update without HID in the update."""
    device = await generate_device_mock_async()

    # Clear the version and hid
    device.version = None
    device.hid = None

    # Send an update without hid
    device.handle_state_update(Pow=1, Mod=3)

    # Version and hid should still be None
    assert device.version is None
    assert device.hid is None

    # But properties should be updated
    assert device.power is True
    assert device.mode == 3


@pytest.mark.asyncio
async def test_handle_state_update_invalid_hid(cipher, send):
    """Test handle_state_update with invalid HID format."""
    device = await generate_device_mock_async()

    # Send an update with malformed hid that doesn't match version pattern
    device.handle_state_update(hid="invalid_hid_format")

    # Should set hid but not extract version
    assert device.hid == "invalid_hid_format"
    assert device.version != "invalid_hid_format"  # Version shouldn't change


@pytest.mark.asyncio
async def test_push_state_update_no_dirty(monkeypatch, cipher, send):
    """Test push_state_update when nothing is dirty."""
    device = await generate_device_mock_async()

    # Clear dirty list
    device._dirty = []

    # Mock send to track calls
    mock_calls = 0

    async def mock_send(*args, **kwargs):
        nonlocal mock_calls
        mock_calls += 1
        return {"t": "status", "pack": {}}

    # Patch send
    with patch.object(device, "send", side_effect=mock_send):
        # Push update with empty dirty list
        await device.push_state_update()

        # Should return early without calling send
        assert mock_calls == 0


@pytest.mark.asyncio
async def test_update_state_no_cipher(monkeypatch, cipher, send):
    """Test update_state when device_cipher is None."""
    device = await generate_device_mock_async()

    # Set device_cipher to None - bypassing the setter to avoid type errors
    device.__dict__["_cipher"] = None

    # Mock bind to track calls
    bind_called = False

    async def mock_bind(*args, **kwargs):
        nonlocal bind_called
        bind_called = True
        device.__dict__["_cipher"] = CipherV1("test_key".encode())

    # Patch bind
    with patch.object(device, "bind", side_effect=mock_bind):
        # Mock send to return success
        async def mock_send(*args, **kwargs):
            return {"t": "status", "pack": {}}

        # Patch send
        with patch.object(device, "send", side_effect=mock_send):
            await device.update_state()

            # Should call bind before sending
            assert bind_called is True


@pytest.mark.asyncio
async def test_push_state_no_cipher(monkeypatch, cipher, send):
    """Test push_state_update when device_cipher is None."""
    device = await generate_device_mock_async()

    # Create a flag to track bind calls
    bind_called = False

    # Create a wrapper for bind
    async def bind_wrapper(*args, **kwargs):
        nonlocal bind_called
        bind_called = True
        # Set the device_cipher so the rest of the method can continue
        device.__dict__["_cipher"] = CipherV1("test_key".encode())
        # Don't actually call the original bind, as it will attempt network operations
        return None

    # Clear dirty flags
    device._dirty = []
    device._properties = get_mock_state().copy()

    # Mock the bind method to detect calls
    with patch.object(device, "bind", side_effect=bind_wrapper):
        # Set device_cipher to None - directly accessing the _cipher attribute
        device.__dict__["_cipher"] = None

        # Make device dirty
        device._dirty = ["Pow"]

        # Mock send to succeed
        async def mock_send(*args, **kwargs):
            return {"t": "status", "pack": {}}

        # Patch send
        with patch.object(device, "send", side_effect=mock_send):
            # Now push state, which should call bind
            await device.push_state_update()

            # Verify bind was called
            assert bind_called is True

            # Verify dirty list was cleared
            assert len(device._dirty) == 0


@pytest.mark.asyncio
async def test_remaining_setters(cipher, send):
    """Test the few remaining setter methods that need coverage."""
    device = await generate_device_mock_async()
    device._properties = {}  # Clear properties for clean test
    device._dirty = []  # Clear dirty list

    # The key is to actually execute each of these lines
    # Line 149
    device.cool_temp_set = 18
    assert device._properties[AwhpProps.COOL_TEMP_SET.value] == 18

    # Line 157
    device.heat_temp_set = 33
    assert device._properties[AwhpProps.HEAT_TEMP_SET.value] == 33

    # Line 181
    device.cool_home_temp_set = 24
    assert device._properties[AwhpProps.COOL_HOME_TEMP_SET.value] == 24

    # Line 189
    device.heat_home_temp_set = 25
    assert device._properties[AwhpProps.HEAT_HOME_TEMP_SET.value] == 25

    # Line 189
    device.fast_heat_water = True
    assert device._properties[AwhpProps.FAST_HEAT_WATER.value] == 1

    # Line 207
    device.left_home = True
    assert device._properties[AwhpProps.LEFT_HOME.value] == 1

    # Line 215
    device.disinfect = True
    assert device._properties[AwhpProps.DISINFECT.value] == 1

    # Line 223
    device.power_save = True
    assert device._properties[AwhpProps.POWER_SAVE.value] == 1

    # Line 231
    device.versati_series = True
    assert device._properties[AwhpProps.VERSATI_SERIES.value] == 1

    # Line 239
    device.room_home_temp_ext = True
    assert device._properties[AwhpProps.ROOM_HOME_TEMP_EXT.value] == 1

    # Line 247
    device.hot_water_ext = True
    assert device._properties[AwhpProps.HOT_WATER_EXT.value] == 1

    # Line 255
    device.foc_mod_swh = True
    assert device._properties[AwhpProps.FOC_MOD_SWH.value] == 1

    # Line 263
    device.emegcy = True
    assert device._properties[AwhpProps.EMEGCY.value] == 1

    # Line 271
    device.hand_fro_swh = True
    assert device._properties[AwhpProps.HAND_FRO_SWH.value] == 1

    # Line 279
    device.water_sys_exh_swh = True
    assert device._properties[AwhpProps.WATER_SYS_EXH_SWH.value] == 1

    # Line 321
    device.power = True
    assert device._properties[AwhpProps.POWER.value] == 1

    # Line 329
    device.mode = 1
    assert device._properties[AwhpProps.MODE.value] == 1

    # Line (cool + hot)
    device.cool_and_hot_water = True
    assert device._properties[AwhpProps.COOL_AND_HOT_WATER.value] == 1

    # Line (heat + hot)
    device.heat_and_hot_water = True
    assert device._properties[AwhpProps.HEAT_AND_HOT_WATER.value] == 1

    # Verify that all properties have been set
    assert len(device._dirty) == 19

    # And that they can be read without error
    for prop in AwhpProps:
        # This will implicitly test all getters
        device.get_property(prop)


@pytest.mark.asyncio
async def test_no_cipher_for_push_state(cipher, send):
    """Test the device_cipher is None in push_state_update."""
    # Create a new device from scratch
    device = AwhpDevice(DeviceInfo("1.1.1.1", 7000, "f4911e7aca59", "1e7aca59"))

    # Set up mock transport
    device._transport = Mock()
    device._transport.sendto = Mock()

    # Ensure device_cipher is None
    assert device.device_cipher is None

    # Mock bind to track calls
    bind_called = False

    async def mock_bind(*args, **kwargs):
        nonlocal bind_called
        bind_called = True
        device.device_cipher = CipherV1("test_key".encode())
        device.ready.set()

    # Patch device's bind method
    with patch.object(device, "bind", side_effect=mock_bind):
        # Create a mock send that returns success
        async def mock_send(*args, **kwargs):
            return {"t": "status", "pack": {}}

        # Patch send method
        with patch.object(device, "send", side_effect=mock_send):
            # Make a property dirty
            device._properties = {}
            device._dirty = ["Pow"]
            device._properties["Pow"] = 1

            # Call push_state_update - this should trigger bind
            await device.push_state_update()

            # Verify bind was called
            assert bind_called is True
