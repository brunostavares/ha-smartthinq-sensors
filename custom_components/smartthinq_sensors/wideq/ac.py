"""------------------for HVAC"""
import logging
from typing import Optional

from .device import (
    Device,
    DeviceStatus,
    STATE_OPTIONITEM_NONE,
)
from homeassistant.components.climate import const as cconst

_LOGGER = logging.getLogger(__name__)

STATE_AC_POWER_OFF = "@AC_MAIN_OPERATION_OFF_W"
STATE_AC_MODE_COOL = "@AC_MAIN_OPERATION_MODE_COOL_W"
STATE_AC_MODE_FAN = "@AC_MAIN_OPERATION_MODE_FAN_W"
STATE_AC_MODE_AI = "@AC_MAIN_OPERATION_MODE_AI_W"
STATE_AC_MODE_HEAT = "@AC_MAIN_OPERATION_MODE_HEAT_W"
STATE_AC_MODE_DRY = "@AC_MAIN_OPERATION_MODE_DRY_W"

STATE_AC_MODES = {
    STATE_AC_POWER_OFF: cconst.HVAC_MODE_OFF,
    STATE_AC_MODE_COOL: cconst.HVAC_MODE_COOL,
    STATE_AC_MODE_FAN: cconst.HVAC_MODE_FAN_ONLY,
    STATE_AC_MODE_AI: cconst.HVAC_MODE_AUTO,
    STATE_AC_MODE_HEAT: cconst.HVAC_MODE_HEAT,
    STATE_AC_MODE_DRY: cconst.HVAC_MODE_DRY,
}

STATE_AC_WIND_LOW = "@AC_MAIN_WIND_STRENGTH_LOW_W"
STATE_AC_WIND_MIDLOW = "@AC_MAIN_WIND_STRENGTH_LOW_MID_W"
STATE_AC_WIND_MID = "@AC_MAIN_WIND_STRENGTH_MID_W"
STATE_AC_WIND_MIDHIGH = "@AC_MAIN_WIND_STRENGTH_MID_HIGH_W"
STATE_AC_WIND_HIGH = "@AC_MAIN_WIND_STRENGTH_HIGH_W"
STATE_AC_WIND_MAX = "@AC_MAIN_WIND_STRENGTH_POWER_W"
STATE_AC_WIND_AUTO = "@AC_MAIN_WIND_STRENGTH_NATURE_W"

STATE_AC_WINDS = {
    STATE_AC_WIND_LOW: cconst.FAN_LOW,
    STATE_AC_WIND_MIDLOW: "Médio baixo",
    STATE_AC_WIND_MID: cconst.FAN_MEDIUM,
    STATE_AC_WIND_MIDHIGH: "Médio alto",
    STATE_AC_WIND_HIGH: cconst.FAN_HIGH,
    STATE_AC_WIND_MAX: "Máximo",
    STATE_AC_WIND_AUTO: cconst.FAN_AUTO,
}

STATE_AC_SWING_OFF = "@OFF"
STATE_AC_SWING_1 = "@1"
STATE_AC_SWING_2 = "@2"
STATE_AC_SWING_3 = "@3"
STATE_AC_SWING_4 = "@4"
STATE_AC_SWING_5 = "@5"
STATE_AC_SWING_6 = "@6"
STATE_AC_SWING_AUTO = "@100"

STATE_AC_SWINGS = {
    STATE_AC_SWING_OFF: cconst.SWING_OFF,
    STATE_AC_SWING_1: "Posição 1",
    STATE_AC_SWING_2: "Posição 2",
    STATE_AC_SWING_3: "Posição 3",
    STATE_AC_SWING_4: "Posição 4",
    STATE_AC_SWING_5: "Posição 5",
    STATE_AC_SWING_6: "Posição 6",
    STATE_AC_SWING_AUTO: "Auto",
}

STATE_AC_ERROR_OFF = "OFF"

STATE_AC_ERROR_NO_ERROR = [
    "ERROR_NOERROR",
    "ERROR_NOERROR_TITLE",
    "No Error",
    "No_Error",
]

class AcDevice(Device):
    """A higher-level interface for a dryer."""
    def __init__(self, client, device):
        super().__init__(client, device, AcStatus(self, None))

    def reset_status(self):
        self._status = AcStatus(self, None)
        return self._status

    def poll(self) -> Optional["AcStatus"]:
        """Poll the device's current state."""

        res = self.device_poll("Ac")
        if not res:
            return None

        self._status = AcStatus(self, res)
        return self._status

class AcStatus(DeviceStatus):
    """Higher-level information about a dryer's current status.

    :param device: The Device instance.
    :param data: JSON data from the API.
    """
    def __init__(self, device, data):
        super().__init__(device, data)
        self._run_state = None
        self._pre_state = None
        self._error = None

    def _get_run_state(self):
        if not self._run_state:
            state = self.lookup_enum("airState.operation")
            if not state:
                self._run_state = state
            else:
                self._run_state = state
        return self._run_state

    def _get_error(self):
        if not self._error:
            error = self.lookup_reference(["Error", "error"], ref_key="title")
            if not error:
                self._error = AC_ERROR_OFF
            else:
                self._error = error
        return self._error

    def _get_temp_val_v2(self, key):
        temp = self._data.get(key)
        if not temp:
            return STATE_OPTIONITEM_NONE
        temp = int(temp)
        return temp

    def _get_energy_kw(self, key):
        power = self._data.get(key)
        if not power:
            return STATE_OPTIONITEM_NONE
        power = str(int(power)/1000)
        return power

    def _get_ac_swing_mode(self, key):
        mode = self._data.get(key)
        if not mode:
            return STATE_OPTIONITEM_NONE
        return STATE_AC_SWINGS.get(mode)

    def _get_fan(self, key):
        fan = self.lookup_enum(key)
        if not fan:
            return STATE_OPTIONITEM_NONE
        return STATE_AC_WINDS.get(fan)

    def _get_operation_mode(self, key):
        power = self.lookup_enum("airState.operation")
        if not power:
            return STATE_OPTIONITEM_NONE
        elif power == STATE_AC_POWER_OFF:
            return STATE_AC_MODES.get(power)
        op = self.lookup_enum(key)
        if not op:
            return STATE_OPTIONITEM_NONE
        return STATE_AC_MODES.get(op)

    @property
    def is_on(self):
        run_state = self._get_run_state()
        return run_state != STATE_AC_POWER_OFF

    @property
    def run_state(self):
        run_state = self._get_run_state()
        if run_state == STATE_AC_POWER_OFF:
            return STATE_OPTIONITEM_NONE
        return self._device.get_enum_text(run_state)

    @property
    def error_state(self):
        if not self.is_error:
            return STATE_OPTIONITEM_NONE
        error = self._get_error()
        return self._device.get_enum_text(error)

    @property
    def is_error(self):
        return False

    @property
    def ac_current_temp(self):
        return self._get_temp_val_v2("airState.tempState.current")

    @property
    def ac_power_consumpion(self):
        return self._get_energy_kw("airState.energy.onCurrent")

    @property
    def ac_target_temperature(self):
        return self._get_temp_val_v2("airState.tempState.target")

    @property
    def ac_swing_mode(self):
        return self._get_ac_swing_mode("airState.wDir.vStep")

    @property
    def ac_fan_mode(self):
        return self._get_fan("airState.windStrength")

    @property
    def ac_operation_mode(self):
        return self._get_operation_mode("airState.opMode")