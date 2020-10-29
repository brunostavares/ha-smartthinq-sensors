"""------------------for HVAC"""
import logging
from typing import Optional

from .device import (
    Device,
    DeviceStatus,
    STATE_OPTIONITEM_NONE,
)
_LOGGER = logging.getLogger(__name__)

STATE_AC_POWER_OFF = "@AC_MAIN_OPERATION_OFF_W"

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
        self._status = DryerStatus(self, None)
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
        temp = str(temp)
        return temp

    def _get_energy_kw(self,key):
        power = self._data.get(key)
        if not power:
            return STATE_OPTIONITEM_NONE
        power = str(power/1000)
        return power


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
    def ac_power_consumpion(self)
        return self._get_energy_kw("airState.energy.onCurrent")

