import asyncio
import enum
import re
from typing import Any, Dict, Optional

from gree_versati.base_device import BaseDevice
from gree_versati.exceptions import DeviceNotBoundError, DeviceTimeoutError


class AwhpProps(enum.Enum):
    T_WATER_IN_PE_W = "AllInWatTemHi"  # Whole number - 100 = temp in celsius
    T_WATER_IN_PE_D = "AllInWatTemLo"  # decimal of above number
    T_WATER_OUT_PE_W = "AllOutWatTemHi"
    T_WATER_OUT_PE_D = "AllOutWatTemLo"
    T_OPT_WATER_W = "HepOutWatTemHi"
    T_OPT_WATER_D = "HepOutWatTemLo"
    HOT_WATER_TEMP_W = "WatBoxTemHi"
    HOT_WATER_TEMP_D = "WatBoxTemLo"
    REMOTE_HOME_TEMP_W = "RmoHomTemHi"
    REMOTE_HOME_TEMP_D = "RmoHomTemLo"
    TANK_HEATER_STATUS = "WatBoxElcHeRunSta"
    SYSTEM_DEFROSTING_STATUS = "SyAnFroRunSta"
    HP_HEATER_1_STATUS = "ElcHe1RunSta"
    HP_HEATER_2_STATUS = "ElcHe2RunSta"
    AUTOMATIC_FROST_PROTECTION = "AnFrzzRunSta"

    POWER = "Pow"  # 1
    MODE = "Mod"  # 4
    COOL_TEMP_SET = "CoWatOutTemSet"  # 18
    HEAT_TEMP_SET = "HeWatOutTemSet"  # 33
    HOT_WATER_TEMP_SET = "WatBoxTemSet"  # 55
    TEMP_UNIT = "TemUn"  # 0
    TEMP_REC = "TemRec"  # 0
    ALL_ERR = "AllErr"  # 0

    COOL_AND_HOT_WATER = "ColHtWter"  # 1
    HEAT_AND_HOT_WATER = "HetHtWter"  # 1
    TEMP_REC_B = "TemRecB"  # 0
    COOL_HOME_TEMP_SET = "CoHomTemSet"  # 24
    HEAT_HOME_TEMP_SET = "HeHomTemSet"  # 25

    FAST_HEAT_WATER = "FastHtWter"  # 0
    QUIET = "Quiet"  # 0
    LEFT_HOME = "LefHom"  # 0
    DISINFECT = "SwDisFct"  # Maybe Disinfect?

    POWER_SAVE = "SvSt"  # 0
    VERSATI_SERIES = "VersatiSeries"  # 0
    ROOM_HOME_TEMP_EXT = "RomHomTemExt"  # 0
    HOT_WATER_EXT = "WatBoxExt"  # 0
    FOC_MOD_SWH = "FocModSwh"  # 0
    EMEGCY = "Emegcy"  # 0
    HAND_FRO_SWH = "HanFroSwh"  # 0
    WATER_SYS_EXH_SWH = "WatSyExhSwh"  # 0
    BORD_TEST = "BordTest"  # 0
    COL_COLET_SWH = "ColColetSwh"  # 0
    END_TEMP_COT_SWH = "EndTemCotSwh"  # 0
    MODEL_TYPE = "ModelType"  # 0
    EVU = "EVU"  # 0


class AwhpDevice(BaseDevice):
    """Device class for Air-Water Heat Pump."""

    def _get_celsius(self, whole, decimal) -> Optional[float]:
        """Helper to combine temperature values into celsius."""
        if whole is None or decimal is None:
            return None
        return whole - 100 + (decimal / 10)

    def t_water_in_pe(
        self, raw_data: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """Get water input temperature."""
        if raw_data:
            return self._get_celsius(
                raw_data.get(AwhpProps.T_WATER_IN_PE_W.value),
                raw_data.get(AwhpProps.T_WATER_IN_PE_D.value),
            )
        return self._get_celsius(
            self.get_property(AwhpProps.T_WATER_IN_PE_W),
            self.get_property(AwhpProps.T_WATER_IN_PE_D),
        )

    def t_water_out_pe(
        self, raw_data: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """Get water output temperature."""
        if raw_data:
            return self._get_celsius(
                raw_data.get(AwhpProps.T_WATER_OUT_PE_W.value),
                raw_data.get(AwhpProps.T_WATER_OUT_PE_D.value),
            )
        return self._get_celsius(
            self.get_property(AwhpProps.T_WATER_OUT_PE_W),
            self.get_property(AwhpProps.T_WATER_OUT_PE_D),
        )

    def t_opt_water(self, raw_data: Optional[Dict[str, Any]] = None) -> Optional[float]:
        """Get optimal water temperature."""
        if raw_data:
            return self._get_celsius(
                raw_data.get(AwhpProps.T_OPT_WATER_W.value),
                raw_data.get(AwhpProps.T_OPT_WATER_D.value),
            )
        return self._get_celsius(
            self.get_property(AwhpProps.T_OPT_WATER_W),
            self.get_property(AwhpProps.T_OPT_WATER_D),
        )

    def hot_water_temp(
        self, raw_data: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """Get hot water temperature."""
        if raw_data:
            return self._get_celsius(
                raw_data.get(AwhpProps.HOT_WATER_TEMP_W.value),
                raw_data.get(AwhpProps.HOT_WATER_TEMP_D.value),
            )
        return self._get_celsius(
            self.get_property(AwhpProps.HOT_WATER_TEMP_W),
            self.get_property(AwhpProps.HOT_WATER_TEMP_D),
        )

    def remote_home_temp(
        self, raw_data: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """Get remote home temperature."""
        if raw_data:
            return self._get_celsius(
                raw_data.get(AwhpProps.REMOTE_HOME_TEMP_W.value),
                raw_data.get(AwhpProps.REMOTE_HOME_TEMP_D.value),
            )
        return self._get_celsius(
            self.get_property(AwhpProps.REMOTE_HOME_TEMP_W),
            self.get_property(AwhpProps.REMOTE_HOME_TEMP_D),
        )

    @property
    def cool_temp_set(self) -> Optional[int]:
        return self.get_property(AwhpProps.COOL_TEMP_SET)

    @cool_temp_set.setter
    def cool_temp_set(self, value: int):
        self.set_property(AwhpProps.COOL_TEMP_SET, value)

    @property
    def heat_temp_set(self) -> Optional[int]:
        return self.get_property(AwhpProps.HEAT_TEMP_SET)

    @heat_temp_set.setter
    def heat_temp_set(self, value: int):
        self.set_property(AwhpProps.HEAT_TEMP_SET, value)

    @property
    def hot_water_temp_set(self) -> Optional[int]:
        return self.get_property(AwhpProps.HOT_WATER_TEMP_SET)

    @hot_water_temp_set.setter
    def hot_water_temp_set(self, value: int):
        self.set_property(AwhpProps.HOT_WATER_TEMP_SET, value)

    @property
    def cool_and_hot_water(self) -> bool:
        return bool(self.get_property(AwhpProps.COOL_AND_HOT_WATER))

    @cool_and_hot_water.setter
    def cool_and_hot_water(self, value: bool):
        self.set_property(AwhpProps.COOL_AND_HOT_WATER, int(value))

    @property
    def heat_and_hot_water(self) -> bool:
        return bool(self.get_property(AwhpProps.HEAT_AND_HOT_WATER))

    @heat_and_hot_water.setter
    def heat_and_hot_water(self, value: bool):
        self.set_property(AwhpProps.HEAT_AND_HOT_WATER, int(value))

    @property
    def cool_home_temp_set(self) -> Optional[int]:
        return self.get_property(AwhpProps.COOL_HOME_TEMP_SET)

    @cool_home_temp_set.setter
    def cool_home_temp_set(self, value: int):
        self.set_property(AwhpProps.COOL_HOME_TEMP_SET, value)

    @property
    def heat_home_temp_set(self) -> Optional[int]:
        return self.get_property(AwhpProps.HEAT_HOME_TEMP_SET)

    @heat_home_temp_set.setter
    def heat_home_temp_set(self, value: int):
        self.set_property(AwhpProps.HEAT_HOME_TEMP_SET, value)

    @property
    def fast_heat_water(self) -> bool:
        return bool(self.get_property(AwhpProps.FAST_HEAT_WATER))

    @fast_heat_water.setter
    def fast_heat_water(self, value: bool):
        self.set_property(AwhpProps.FAST_HEAT_WATER, int(value))

    @property
    def left_home(self) -> bool:
        return bool(self.get_property(AwhpProps.LEFT_HOME))

    @left_home.setter
    def left_home(self, value: bool):
        self.set_property(AwhpProps.LEFT_HOME, int(value))

    @property
    def disinfect(self) -> bool:
        return bool(self.get_property(AwhpProps.DISINFECT))

    @disinfect.setter
    def disinfect(self, value: bool):
        self.set_property(AwhpProps.DISINFECT, int(value))

    @property
    def power_save(self) -> bool:
        return bool(self.get_property(AwhpProps.POWER_SAVE))

    @power_save.setter
    def power_save(self, value: bool):
        self.set_property(AwhpProps.POWER_SAVE, int(value))

    @property
    def versati_series(self) -> bool:
        return bool(self.get_property(AwhpProps.VERSATI_SERIES))

    @versati_series.setter
    def versati_series(self, value: bool):
        self.set_property(AwhpProps.VERSATI_SERIES, int(value))

    @property
    def room_home_temp_ext(self) -> bool:
        return bool(self.get_property(AwhpProps.ROOM_HOME_TEMP_EXT))

    @room_home_temp_ext.setter
    def room_home_temp_ext(self, value: bool):
        self.set_property(AwhpProps.ROOM_HOME_TEMP_EXT, int(value))

    @property
    def hot_water_ext(self) -> bool:
        return bool(self.get_property(AwhpProps.HOT_WATER_EXT))

    @hot_water_ext.setter
    def hot_water_ext(self, value: bool):
        self.set_property(AwhpProps.HOT_WATER_EXT, int(value))

    @property
    def foc_mod_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.FOC_MOD_SWH))

    @foc_mod_swh.setter
    def foc_mod_swh(self, value: bool):
        self.set_property(AwhpProps.FOC_MOD_SWH, int(value))

    @property
    def emegcy(self) -> bool:
        return bool(self.get_property(AwhpProps.EMEGCY))

    @emegcy.setter
    def emegcy(self, value: bool):
        self.set_property(AwhpProps.EMEGCY, int(value))

    @property
    def hand_fro_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.HAND_FRO_SWH))

    @hand_fro_swh.setter
    def hand_fro_swh(self, value: bool):
        self.set_property(AwhpProps.HAND_FRO_SWH, int(value))

    @property
    def water_sys_exh_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.WATER_SYS_EXH_SWH))

    @water_sys_exh_swh.setter
    def water_sys_exh_swh(self, value: bool):
        self.set_property(AwhpProps.WATER_SYS_EXH_SWH, int(value))

    @property
    def tank_heater_status(self) -> bool:
        return bool(self.get_property(AwhpProps.TANK_HEATER_STATUS))

    @property
    def system_defrosting_status(self) -> bool:
        return bool(self.get_property(AwhpProps.SYSTEM_DEFROSTING_STATUS))

    @property
    def hp_heater_1_status(self) -> bool:
        return bool(self.get_property(AwhpProps.HP_HEATER_1_STATUS))

    @property
    def hp_heater_2_status(self) -> bool:
        return bool(self.get_property(AwhpProps.HP_HEATER_2_STATUS))

    @property
    def automatic_frost_protection(self) -> bool:
        return bool(self.get_property(AwhpProps.AUTOMATIC_FROST_PROTECTION))

    @property
    def temp_unit(self) -> Optional[int]:
        return self.get_property(AwhpProps.TEMP_UNIT)

    @property
    def temp_rec(self) -> Optional[int]:
        return self.get_property(AwhpProps.TEMP_REC)

    @property
    def all_err(self) -> Optional[int]:
        return self.get_property(AwhpProps.ALL_ERR)

    @property
    def temp_rec_b(self) -> Optional[int]:
        return self.get_property(AwhpProps.TEMP_REC_B)

    @property
    def quiet(self) -> bool:
        return bool(self.get_property(AwhpProps.QUIET))

    @property
    def bord_test(self) -> bool:
        return bool(self.get_property(AwhpProps.BORD_TEST))

    @property
    def col_colet_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.COL_COLET_SWH))

    @property
    def end_temp_cot_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.END_TEMP_COT_SWH))

    @property
    def model_type(self) -> Optional[int]:
        return self.get_property(AwhpProps.MODEL_TYPE)

    @property
    def evu(self) -> bool:
        return bool(self.get_property(AwhpProps.EVU))

    @property
    def power(self) -> bool:
        return bool(self.get_property(AwhpProps.POWER))

    @power.setter
    def power(self, value: bool):
        self.set_property(AwhpProps.POWER, int(value))

    @property
    def mode(self) -> Optional[int]:
        return self.get_property(AwhpProps.MODE)

    @mode.setter
    def mode(self, value: int):
        self.set_property(AwhpProps.MODE, int(value))

    async def update_all_properties(self) -> None:
        """Update all device properties in a single request."""
        await self.update_state()
        # After update_state(), all properties are available in self._properties
        return None

    async def get_all_properties(self) -> dict:
        """Get all properties in a single request and return them."""
        await self.update_all_properties()

        # Create a dictionary of all defined properties
        return {
            prop.value: self.get_property(prop)
            for prop in AwhpProps
        }

    async def update_state(self, wait_for: float = 30):
        """Update the internal state of the device."""
        if not self.device_cipher:
            await self.bind()

        self._logger.debug(
            "Updating AWHP device properties for (%s)", str(self.device_info)
        )

        # Get all properties from the enum
        all_props = [prop.value for prop in AwhpProps]
        if not self.hid:
            all_props.append("hid")

        # Split into batches of 23 properties to get all properties in 2 calls
        batch_size = 23
        property_batches = [
            all_props[i: i + batch_size] for i in range(0, len(all_props), batch_size)
        ]

        self._logger.debug(
            f"Split properties into {len(property_batches)} batches")

        try:
            for i, batch in enumerate(property_batches):
                self._logger.debug(
                    f"Requesting batch {i + 1}/{len(property_batches)}: {batch}"
                )
                # Type check to satisfy pyright
                if self.device_info is None:
                    raise DeviceNotBoundError("device_info is None")

                # Send the request and get the response
                res = await self.send(
                    self.create_status_message(self.device_info, *batch)
                )
                self._logger.debug(
                    f"Received response for batch {i + 1}: {res}")

            self._logger.debug(
                f"All batches complete. Current device properties: {self._properties}"
            )

        except asyncio.TimeoutError as err:
            self._logger.error("Timeout while requesting device state")
            raise DeviceTimeoutError from err
        except Exception as e:
            self._logger.error(f"Error updating state: {e}", exc_info=True)
            raise

    def handle_state_update(self, **kwargs) -> None:
        """Handle incoming information about the firmware version of the device"""
        self._logger.debug("Received state update: %s", kwargs)

        # Ex: hid = 362001000762+U-CS532AE(LT)V3.31.bin
        if "hid" in kwargs:
            self.hid = kwargs.pop("hid")
            match = re.search(r"(?<=V)([\d.]+)\.bin$", self.hid or "")
            if match:
                self.version = match.group(1)
            self._logger.debug(
                "Device version changed to %s, hid %s", self.version, self.hid
            )

        # Store previous property values for comparison
        previous_properties = {k: v for k,
                               v in self._properties.items() if k in kwargs}

        # Update properties with new values
        self._properties.update(kwargs)

        # Log property changes
        for key, new_value in kwargs.items():
            old_value = previous_properties.get(key, "N/A")
            if old_value != new_value:
                self._logger.debug(
                    "Property updated: %s changed from %s to %s",
                    key, old_value, new_value)
            else:
                self._logger.debug(
                    "Property unchanged: %s remains %s", key, new_value)

        self._logger.debug("Properties after update: %s",
                           {k: v for k, v in self._properties.items() if k in kwargs})

    async def push_state_update(self, wait_for: float = 30):
        """Push any pending state updates to the unit

        Args:
            wait_for (object): How long to wait for an update from the device,
                0 for no wait
        """
        if not self._dirty:
            return

        if not self.device_cipher:
            await self.bind()

        self._logger.debug("Pushing state updates to (%s)",
                           str(self.device_info))

        props = {}
        for name in self._dirty:
            value = self._properties.get(name)
            self._logger.debug(
                "Sending remote state update %s -> %s", name, value)
            props[name] = value

        self._dirty.clear()

        try:
            # Type check to satisfy pyright
            if self.device_info is None:
                raise DeviceNotBoundError("device_info is None")
            await self.send(self.create_command_message(self.device_info, **props))

        except asyncio.TimeoutError as err:
            raise DeviceTimeoutError from err
