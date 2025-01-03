import enum

from greeclimate.base_device import BaseDevice

class AwhpProps(enum.Enum):
    T_WATER_IN_PE_W = "AllInWatTemHi" # Whole number - 100 = temp in celsius
    T_WATER_IN_PE_D = "AllInWatTemLo" # decimal of above number
    T_WATER_OUT_PE_W = "AllOutWatTemHi"
    T_WATER_OUT_PE_D = "AllOutWatTemLo"
    T_OPT_WATER_W = "HepOutWatTemHi"
    T_OPT_WATER_D = "HepOutWatTemLo"
    HOT_WATER_TEMP_W = "WatBoxTemHi"
    HOT_WATER_TEMP_D  = "WatBoxTemLo"
    REMOTE_HOME_TEMP_W = "RmoHomTemHi"
    REMOTE_HOME_TEMP_D = "RmoHomTemLo"
    TANK_HEATER_STATUS = "WatBoxElcHeRunSta"
    SYSTEM_DEFROSTING_STATUS = "SyAnFroRunSta"
    HP_HEATER_1_STATUS = "ElcHe1RunSta"
    HP_HEATER_2_STATUS = "ElcHe2RunSta"
    AUTOMATIC_FROST_PROTECTION = "AnFrzzRunSta"
    # HOT_WATER_EXT = "WatBoxExt"
    # TEMP_UNIT = "TemUn"
    # ALL_ERR = "AllErr"

    POWER = "Pow" # 1
    MODE = "Mod"  # 4
    COOL_TEMP_SET = "CoWatOutTemSet" # 18
    HEAT_TEMP_SET = "HeWatOutTemSet" # 33
    HOT_WATER_TEMP_SET = "WatBoxTemSet" # 55
    TEMP_UNIT = "TemUn" # 0
    TEMP_REC = "TemRec" # 0
    ALL_ERR = "AllErr" # 0

    COOL_AND_HOT_WATER = "ColHtWter" # 1
    HEAT_AND_HOT_WATER = "HetHtWter" # 1
    TEMP_REC_B = "TemRecB" # 0
    COOL_HOME_TEMP_SET = "CoHomTemSet" # 24
    HEAT_HOME_TEMP_SET = "HeHomTemSet" # 25
    
    FAST_HEAT_WATER = "FastHtWter" # 0
    QUIET = "Quiet" # 0
    LEFT_HOME = "LefHom" # 0
    DISINFECT = "SwDisFct" # Maybe Disinfect?

    POWER_SAVE = "SvSt" # 0
    VERSATI_SERIES = "VersatiSeries" # 0
    ROOM_HOME_TEMP_EXT = "RomHomTemExt" # 0
    HOT_WATER_EXT = "WatBoxExt" # 0
    FOC_MOD_SWH = "FocModSwh" # 0
    EMEGCY = "Emegcy" # 0
    HAND_FRO_SWH = "HanFroSwh" # 0
    WATER_SYS_EXH_SWH = "WatSyExhSwh" # 0
    BORD_TEST = "BordTest" # 0
    COL_COLET_SWH = "ColColetSwh" # 0
    END_TEMP_COT_SWH = "EndTemCotSwh" # 0
    MODEL_TYPE = "ModelType" # 0
    EVU = "EVU" # 0

class AwhpDevice(BaseDevice):

    def _get_celsius(self, whole, decimal) -> float:
        return whole - 100 + (decimal / 10)

    @property
    def t_water_in_pe(self) -> float:
        return self._get_celsius(
            self.get_property(AwhpProps.T_WATER_IN_PE_W), 
            self.get_property(AwhpProps.T_WATER_IN_PE_D)
        )
    
    @property
    def t_water_out_pe(self) -> float:
        return self._get_celsius(
            self.get_property(AwhpProps.T_WATER_OUT_PE_W), 
            self.get_property(AwhpProps.T_WATER_OUT_PE_D)
        )

    @property
    def t_opt_water(self) -> float:
        return self._get_celsius(
            self.get_property(AwhpProps.T_OPT_WATER_W), 
            self.get_property(AwhpProps.T_OPT_WATER_D)
        )
    
    @property
    def hot_water_temp(self) -> float:
        return self._get_celsius(
            self.get_property(AwhpProps.HOT_WATER_TEMP_W), 
            self.get_property(AwhpProps.HOT_WATER_TEMP_D)
        )
    
    @property
    def remote_home_temp(self) -> float:
        return self._get_celsius(
            self.get_property(AwhpProps.REMOTE_HOME_TEMP_W), 
            self.get_property(AwhpProps.REMOTE_HOME_TEMP_D)
        )

    @property
    def cool_temp_set(self) -> int:
        return self.get_property(AwhpProps.COOL_TEMP_SET)

    @cool_temp_set.setter
    def cool_temp_set(self, value: int):
        self.set_property(AwhpProps.COOL_TEMP_SET, value)

    @property
    def heat_temp_set(self) -> int:
        return self.get_property(AwhpProps.HEAT_TEMP_SET)

    @heat_temp_set.setter
    def heat_temp_set(self, value: int):
        self.set_property(AwhpProps.HEAT_TEMP_SET, value)

    @property
    def hot_water_temp_set(self) -> int:
        return self.get_property(AwhpProps.HOT_WATER_TEMP_SET)

    @hot_water_temp_set.setter
    def hot_water_temp_set(self, value: int):
        self.set_property(AwhpProps.HOT_WATER_TEMP_SET, value)

###
# The following setters are not yet implemented
# Need to figure out what they do exactly
###
    @property
    def cool_and_hot_water(self) -> bool:
        return bool(self.get_property(AwhpProps.COOL_AND_HOT_WATER))

#    @cool_and_hot_water.setter
#    def cool_and_hot_water(self, value: bool):
#        self.set_property(AWHPProps.COOL_AND_HOT_WATER, int(value))

    @property
    def heat_and_hot_water(self) -> bool:
        return bool(self.get_property(AwhpProps.HEAT_AND_HOT_WATER))

#    @heat_and_hot_water.setter
#    def heat_and_hot_water(self, value: bool):
#        self.set_property(AWHPProps.HEAT_AND_HOT_WATER, int(value))

    @property
    def cool_home_temp_set(self) -> int:
        return self.get_property(AwhpProps.COOL_HOME_TEMP_SET)

#    @cool_home_temp_set.setter
#    def cool_home_temp_set(self, value: int):
#        self.set_property(AWHPProps.COOL_HOME_TEMP_SET, value)

    @property
    def heat_home_temp_set(self) -> int:
        return self.get_property(AwhpProps.HEAT_HOME_TEMP_SET)

#    @heat_home_temp_set.setter
#    def heat_home_temp_set(self, value: int):
#        self.set_property(AWHPProps.HEAT_HOME_TEMP_SET, value)

    @property
    def fast_heat_water(self) -> bool:
        return bool(self.get_property(AwhpProps.FAST_HEAT_WATER))

#    @fast_heat_water.setter
#    def fast_heat_water_set(self, value: bool):
#        self.set_property(AWHPProps.FAST_HEAT_WATER, int(value))

    @property
    def left_home(self) -> bool:
        return bool(self.get_property(AwhpProps.LEFT_HOME))
    
#    @left_home.setter
#    def left_home(self, value: bool):
#        self.set_property(AWHPProps.LEFT_HOME, int(value))

    @property
    def disinfect(self) -> bool:
        return bool(self.get_property(AwhpProps.DISINFECT))
    
#    @disinfect.setter
#    def disinfect(self, value: bool):
#        self.set_property(AWHPProps.DISINFECT, int(value))

    @property
    def power_save(self) -> bool:
        return bool(self.get_property(AwhpProps.POWER_SAVE))
    
#    @power_save.setter
#    def power_save(self, value: bool):
#        self.set_property(AWHPProps.POWER_SAVE, int(value))

    @property
    def versati_series(self) -> bool:
        return bool(self.get_property(AwhpProps.VERSATI_SERIES))
    
#    @versati_series.setter
#    def versati_series(self, value: bool):
#        self.set_property(AWHPProps.VERSATI_SERIES, int(value))

    @property
    def room_home_temp_ext(self) -> bool:
        return bool(self.get_property(AwhpProps.ROOM_HOME_TEMP_EXT))
    
#    @room_home_temp_ext.setter
#    def room_home_temp_ext(self, value: bool):
#        self.set_property(AWHPProps.ROOM_HOME_TEMP_EXT, int(value))

    @property
    def hot_water_ext(self) -> bool:
        return bool(self.get_property(AwhpProps.HOT_WATER_EXT))
    
#    @hot_water_ext.setter
#    def hot_water_ext(self, value: bool):
#        self.set_property(AWHPProps.HOT_WATER_EXT, int(value))

    @property
    def foc_mod_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.FOC_MOD_SWH))
    
#    @foc_mod_swh.setter
#    def foc_mod_swh(self, value: bool):
#        self.set_property(AWHPProps.FOC_MOD_SWH, int(value))

    @property
    def emegcy(self) -> bool:
        return bool(self.get_property(AwhpProps.EMEGCY))
    
#    @emegcy.setter
#    def emegcy(self, value: bool):
#        self.set_property(AWHPProps.EMEGCY, int(value))

    @property
    def hand_fro_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.HAND_FRO_SWH))
    
#    @hand_fro_swh.setter
#    def hand_fro_swh(self, value: bool):
#        self.set_property(AWHPProps.HAND_FRO_SWH, int(value))

    @property
    def water_sys_exh_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.WATER_SYS_EXH_SWH))
    
#    @water_sys_exh_swh.setter
#    def water_sys_exh_swh(self, value: bool):
#        self.set_property(AWHPProps.WATER_SYS_EXH_SWH, int(value))

    @property
    def bord_test(self) -> bool:
        return bool(self.get_property(AwhpProps.BORD_TEST))
    
#    @bord_test.setter
#    def bord_test(self, value: bool):
#        self.set_property(AWHPProps.BORD_TEST, int(value))

    @property
    def col_colet_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.COL_COLET_SWH))
    
#    @col_colet_swh.setter
#    def col_colet_swh(self, value: bool):
#        self.set_property(AWHPProps.COL_COLET_SWH, int(value))

    @property
    def end_temp_cot_swh(self) -> bool:
        return bool(self.get_property(AwhpProps.END_TEMP_COT_SWH))
    
#    @end_temp_cot_swh.setter
#    def end_temp_cot_swh(self, value: bool):
#        self.set_property(AWHPProps.END_TEMP_COT_SWH, int(value))

    @property
    def model_type(self) -> bool:
        return bool(self.get_property(AwhpProps.MODEL_TYPE))
    
#    @model_type.setter
#    def model_type(self, value: bool):
#        self.set_property(AWHPProps.MODEL_TYPE, int(value))

    @property
    def evu(self) -> bool:
        return bool(self.get_property(AwhpProps.EVU))
    
#    @evu.setter
#    def evu(self, value: bool):
#        self.set_property(AWHPProps.EVU, int(value))

    @property
    def power(self) -> bool:
        return bool(self.get_property(AwhpProps.POWER))
    
#    @power.setter
#    def power(self, value: bool):
#        self.set_property(AWHPProps.POWER, int(value))

    @property
    def mode(self) -> int:
        return self.get_property(AwhpProps.MODE)
    
#    @mode.setter
#    def mode(self, value: int):
#        self.set_property(AWHPProps.MODE, int(value))

    @property
    def temp_unit(self) -> int:
        return self.get_property(AwhpProps.TEMP_UNIT)
    
#    @temp_unit.setter
#    def temp_unit(self, value: int):
#        self.set_property(AWHPProps.TEMP_UNIT, int(value))

    @property
    def temp_rec(self) -> int:
        return self.get_property(AwhpProps.TEMP_REC)
    
#    @temp_rec.setter
#    def temp_rec(self, value: int):
#        self.set_property(AWHPProps.TEMP_REC, int(value))

    @property
    def all_err(self) -> int:
        return self.get_property(AwhpProps.ALL_ERR)
    
#    @all_err.setter
#    def all_err(self, value: int):
#        self.set_property(AWHPProps.ALL_ERR, int(value))
