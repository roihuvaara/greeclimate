import logging
from enum import IntEnum, unique

from greeclimate_versati_fork.base_device import TEMP_OFFSET, BaseDevice, Props


@unique
class TemperatureUnits(IntEnum):
    C = 0
    F = 1


@unique
class Mode(IntEnum):
    Auto = 0
    Cool = 1
    Dry = 2
    Fan = 3
    Heat = 4


@unique
class FanSpeed(IntEnum):
    Auto = 0
    Low = 1
    MediumLow = 2
    Medium = 3
    MediumHigh = 4
    High = 5


@unique
class HorizontalSwing(IntEnum):
    Default = 0
    FullSwing = 1
    Left = 2
    LeftCenter = 3
    Center = 4
    RightCenter = 5
    Right = 6


@unique
class VerticalSwing(IntEnum):
    Default = 0
    FullSwing = 1
    FixedUpper = 2
    FixedUpperMiddle = 3
    FixedMiddle = 4
    FixedLowerMiddle = 5
    FixedLower = 6
    SwingUpper = 7
    SwingUpperMiddle = 8
    SwingMiddle = 9
    SwingLowerMiddle = 10
    SwingLower = 11


class DehumidifierMode(IntEnum):
    Default = 0
    AnionOnly = 9


def generate_temperature_record(temp_f):
    temSet = round((temp_f - 32.0) * 5.0 / 9.0)
    temRec = (int)((((temp_f - 32.0) * 5.0 / 9.0) - temSet) > 0)
    return {"f": temp_f, "temSet": temSet, "temRec": temRec}


TEMP_MIN = 8
TEMP_MAX = 30
TEMP_MIN_F = 46
TEMP_MAX_F = 86
TEMP_MIN_TABLE = -60
TEMP_MAX_TABLE = 60
TEMP_MIN_TABLE_F = -76
TEMP_MAX_TABLE_F = 140
TEMP_TABLE = [generate_temperature_record(x) for x in range(TEMP_MIN_TABLE_F, TEMP_MAX_TABLE_F + 1)]
HUMIDITY_MIN = 30
HUMIDITY_MAX = 80 

class Device(BaseDevice):
    @property
    def power(self) -> bool:
        return bool(self.get_property(Props.POWER))

    @power.setter
    def power(self, value: int):
        self.set_property(Props.POWER, int(value))

    @property
    def mode(self) -> int:
        return self.get_property(Props.MODE)

    @mode.setter
    def mode(self, value: int):
        self.set_property(Props.MODE, int(value))

    def _convert_to_units(self, value, bit):
        if self.temperature_units != TemperatureUnits.F.value:
            return value

        if value < TEMP_MIN_TABLE or value > TEMP_MAX_TABLE:
            raise ValueError(f"Specified temperature {value} is out of range.")

        matching_temset = [t for t in TEMP_TABLE if t["temSet"] == value]

        try:
            f = next(t for t in matching_temset if t["temRec"] == bit)
        except StopIteration:
            f = matching_temset[0]

        return f["f"]

    @property
    def target_temperature(self) -> int:
        temset = self.get_property(Props.TEMP_SET)
        temrec = self.get_property(Props.TEMP_BIT)
        return self._convert_to_units(temset, temrec)

    @target_temperature.setter
    def target_temperature(self, value: int):
        def validate(val):
            if val > TEMP_MAX or val < TEMP_MIN:
                raise ValueError(f"Specified temperature {val} is out of range.")

        if self.temperature_units == 1:
            rec = generate_temperature_record(value)
            validate(rec["temSet"])
            self.set_property(Props.TEMP_SET, rec["temSet"])
            self.set_property(Props.TEMP_BIT, rec["temRec"])
        else:
            validate(value)
            self.set_property(Props.TEMP_SET, int(value))

    @property
    def temperature_units(self) -> int:
        return self.get_property(Props.TEMP_UNIT)

    @temperature_units.setter
    def temperature_units(self, value: int):
        self.set_property(Props.TEMP_UNIT, int(value))

    @property
    def current_temperature(self) -> int:
        prop = self.get_property(Props.TEMP_SENSOR)
        bit = self.get_property(Props.TEMP_BIT)
        if prop is not None:
            v = self.version and int(self.version.split(".")[0])
            try:
                if v == 4:
                    return self._convert_to_units(prop, bit)
                elif prop != 0:
                    return self._convert_to_units(prop - TEMP_OFFSET, bit)
            except ValueError:
                logging.warning("Converting unexpected set temperature value %s", prop)

        return self.target_temperature

    @property
    def fan_speed(self) -> int:
        return self.get_property(Props.FAN_SPEED)

    @fan_speed.setter
    def fan_speed(self, value: int):
        self.set_property(Props.FAN_SPEED, int(value))

    @property
    def fresh_air(self) -> bool:
        return bool(self.get_property(Props.FRESH_AIR))

    @fresh_air.setter
    def fresh_air(self, value: bool):
        self.set_property(Props.FRESH_AIR, int(value))

    @property
    def xfan(self) -> bool:
        return bool(self.get_property(Props.XFAN))

    @xfan.setter
    def xfan(self, value: bool):
        self.set_property(Props.XFAN, int(value))

    @property
    def anion(self) -> bool:
        return bool(self.get_property(Props.ANION))

    @anion.setter
    def anion(self, value: bool):
        self.set_property(Props.ANION, int(value))

    @property
    def sleep(self) -> bool:
        return bool(self.get_property(Props.SLEEP))

    @sleep.setter
    def sleep(self, value: bool):
        self.set_property(Props.SLEEP, int(value))
        self.set_property(Props.SLEEP_MODE, int(value))

    @property
    def light(self) -> bool:
        return bool(self.get_property(Props.LIGHT))

    @light.setter
    def light(self, value: bool):
        self.set_property(Props.LIGHT, int(value))

    @property
    def horizontal_swing(self) -> int:
        return self.get_property(Props.SWING_HORIZ)

    @horizontal_swing.setter
    def horizontal_swing(self, value: int):
        self.set_property(Props.SWING_HORIZ, int(value))

    @property
    def vertical_swing(self) -> int:
        return self.get_property(Props.SWING_VERT)

    @vertical_swing.setter
    def vertical_swing(self, value: int):
        self.set_property(Props.SWING_VERT, int(value))

    @property
    def quiet(self) -> bool:
        return self.get_property(Props.QUIET)

    @quiet.setter
    def quiet(self, value: bool):
        self.set_property(Props.QUIET, 2 if value else 0)

    @property
    def turbo(self) -> bool:
        return bool(self.get_property(Props.TURBO))

    @turbo.setter
    def turbo(self, value: bool):
        self.set_property(Props.TURBO, int(value))

    @property
    def steady_heat(self) -> bool:
        return bool(self.get_property(Props.STEADY_HEAT))

    @steady_heat.setter
    def steady_heat(self, value: bool):
        self.set_property(Props.STEADY_HEAT, int(value))

    @property
    def power_save(self) -> bool:
        return bool(self.get_property(Props.POWER_SAVE))

    @power_save.setter
    def power_save(self, value: bool):
        self.set_property(Props.POWER_SAVE, int(value))

    @property
    def target_humidity(self) -> int:
        15 + (self.get_property(Props.HUM_SET) * 5)

    @target_humidity.setter
    def target_humidity(self, value: int):
        def validate(val):
            if value > HUMIDITY_MAX or val < HUMIDITY_MIN:
                raise ValueError(f"Specified temperature {val} is out of range.")

        self.set_property(Props.HUM_SET, (value - 15) // 5)

    @property
    def dehumidifier_mode(self):
        return self.get_property(Props.DEHUMIDIFIER_MODE)

    @property
    def current_humidity(self) -> int:
        return self.get_property(Props.HUM_SENSOR)

    @property
    def clean_filter(self) -> bool:
        return bool(self.get_property(Props.CLEAN_FILTER))

    @property
    def water_full(self) -> bool:
        return bool(self.get_property(Props.WATER_FULL))
