# REQUIREMENTS = ['wideq']
# DEPENDENCIES = ['smartthinq']

import logging
from datetime import timedelta

from .wideq.device import (
    STATE_OPTIONITEM_OFF,
    STATE_OPTIONITEM_ON,
    UNIT_TEMP_CELSIUS,
    UNIT_TEMP_FAHRENHEIT,
    DeviceType,
)

from homeassistant.components.binary_sensor import DEVICE_CLASS_PROBLEM, DEVICE_CLASS_OPENING
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.components.climate import ClimateEntity


from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_POWER,
    STATE_ON,
    STATE_OFF,
    STATE_UNAVAILABLE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    ENERGY_KILO_WATT_HOUR
)

from .const import DOMAIN, LGE_DEVICES

from homeassistant.components.climate import const as c_const

from . import LGEDevice

# sensor definition
ATTR_MEASUREMENT_NAME = "measurement_name"
ATTR_ICON = "icon"
ATTR_UNIT_FN = "unit_fn"
ATTR_DEVICE_CLASS = "device_class"
ATTR_VALUE_FN = "value_fn"
ATTR_ENABLED_FN = "enabled"

# general sensor attributes
ATTR_CURRENT_STATUS = "current_status"
ATTR_RUN_STATE = "run_state"
ATTR_PRE_STATE = "pre_state"
ATTR_RUN_COMPLETED = "run_completed"
ATTR_REMAIN_TIME = "remain_time"
ATTR_INITIAL_TIME = "initial_time"
ATTR_RESERVE_TIME = "reserve_time"
ATTR_CURRENT_COURSE = "current_course"
ATTR_ERROR_STATE = "error_state"
ATTR_ERROR_MSG = "error_message"

# ac sensor attributes
ATTR_AC_CURRENT_TEMP = "tempState_current"
ATTR_AC_POWER_CONSUMPTION = "consumo_de_energia"

STATE_LOOKUP = {
    STATE_OPTIONITEM_OFF: STATE_OFF,
    STATE_OPTIONITEM_ON: STATE_ON,
}

TEMP_UNIT_LOOKUP = {
    UNIT_TEMP_CELSIUS: TEMP_CELSIUS,
    UNIT_TEMP_FAHRENHEIT: TEMP_FAHRENHEIT,
}

DEFAULT_SENSOR = "default"
DISPATCHER_REMOTE_UPDATE = "thinq_remote_update"

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

AC_SENSORS = {
    DEFAULT_SENSOR: {
        ATTR_MEASUREMENT_NAME: "Default",
        ATTR_ICON: "mdi:air-conditioner",
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._power_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}


def setup_platform(hass, config, async_add_entities, discovery_info=None):
    pass


async def async_setup_sensors(hass, config_entry, async_add_entities, type_binary):
    """Set up LGE device sensors and bynary sensor based on config_entry."""
    lge_sensors = []
    ac_sensors = AC_SENSORS

    entry_config = hass.data[DOMAIN]
    lge_devices = entry_config.get(LGE_DEVICES, [])

    lge_sensors.extend(
        [
            LGEAcSensor(lge_device, measurement, definition, type_binary)
            for measurement, definition in ac_sensors.items()
            for lge_device in lge_devices.get(DeviceType.AC, [])
            if definition[ATTR_ENABLED_FN](lge_device)
        ]
    )

    async_add_entities(lge_sensors, True)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the LGE sensors."""
    _LOGGER.info("Starting LGE ThinQ sensors...")
    await async_setup_sensors(hass, config_entry, async_add_entities, False)

class LGESensor(ClimateEntity):
    def __init__(self, device: LGEDevice, measurement, definition, is_binary):
        """Initialize the sensor."""
        self._api = device
        self._name_slug = device.name
        self._measurement = measurement
        self._def = definition
        self._is_binary = is_binary
        self._is_default = self._measurement == DEFAULT_SENSOR
        self._unsub_dispatcher = None
        self._dispatcher_queue = f"{DISPATCHER_REMOTE_UPDATE}-{self._name_slug}"

    @staticmethod
    def format_time(hours, minutes):
        if not minutes:
            return "0:00"
        if not hours:
            if int(minutes) >= 60:
                int_minutes = int(minutes)
                int_hours = int(int_minutes / 60)
                minutes = str(int_minutes - (int_hours * 60))
                hours = str(int_hours)
            else:
                hours = "0"
        remain_time = [hours, minutes]
        if int(minutes) < 10:
            return ":0".join(remain_time)
        else:
            return ":".join(remain_time)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if self._is_default:
            return self._name_slug
        return f"{self._name_slug} {self._def[ATTR_MEASUREMENT_NAME]}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        if self._is_default:
            return self._api.unique_id
        return f"{self._api.unique_id}-{self._measurement}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._def[ATTR_UNIT_FN](self)

    @property
    def device_class(self):
        """Return device class."""
        return self._def[ATTR_DEVICE_CLASS]

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._def[ATTR_ICON]

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        if self._is_binary:
            ret_val = self._def[ATTR_VALUE_FN](self)
            if isinstance(ret_val, bool):
                return ret_val
            return True if ret_val == STATE_ON else False
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        if not self.available:
            return STATE_UNAVAILABLE
        if self._is_binary:
            return STATE_ON if self.is_on else STATE_OFF
        return self._def[ATTR_VALUE_FN](self)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._api.available

    @property
    def assumed_state(self) -> bool:
        """Return True if unable to access real state of the entity."""
        return self._api.assumed_state

    @property
    def state_attributes(self):
        """Return the optional state attributes."""
        return self._api.state_attributes

    @property
    def device_info(self):
        """Return the device info."""
        return self._api.device_info

    @property
    def should_poll(self) -> bool:
        """ This sensors must be polled only by default entity """
        return self._is_default

    def update(self):
        """Update the device status"""
        self._api.device_update()
        dispatcher_send(self.hass, self._dispatcher_queue)

    async def async_added_to_hass(self):
        """Register update dispatcher."""

        async def async_state_update():
            """Update callback."""
            _LOGGER.debug("Updating %s state by dispatch", self.name)
            self.async_write_ha_state()

        if not self._is_default:
            self._unsub_dispatcher = async_dispatcher_connect(
                self.hass, self._dispatcher_queue, async_state_update
            )

    async def async_will_remove_from_hass(self):
        """Unregister update dispatcher."""
        if self._unsub_dispatcher is not None:
            self._unsub_dispatcher()
            self._unsub_dispatcher = None

    @property
    def _power_state(self):
        """Current power state"""
        if self._api.state:
            if self._api.state.is_on:
                return STATE_ON
        return STATE_OFF

# For Climate platform

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        return self._api.ac_current_temp
    
    @property
    def target_temperature(self):
        return self._api.ac_target_temperature
    
    @property
    def target_temperature_high(self):
        return 30

    @property
    def target_temperature_low(self):
        return 18

#    @property
#    def target_temperature_step(self):
#        return 1

    @property
    def hvac_mode(self):
        return self._api.ac_operation_mode

    @property
    def hvac_modes(self):
        return [c_const.HVAC_MODE_COOL, c_const.HVAC_MODE_FAN_ONLY, c_const.HVAC_MODE_AUTO, c_const.HVAC_MODE_HEAT, c_const.HVAC_MODE_DRY]

    @property
    def fan_mode(self):
        return self._api.ac_fan_mode

    @property
    def fan_modes(self):
        return ["aa","bb","cc"]

    @property
    def swing_mode(self):
        return self._api.ac_swing_mode
    
    @property
    def swing_modes(self):
        return ["aa","bb","cc"]

    @property
    def supported_features(self):
        return (
            c_const.SUPPORT_TARGET_TEMPERATURE |
            c_const.SUPPORT_TARGET_TEMPERATURE_RANGE |
            c_const.SUPPORT_FAN_MODE |
            c_const.SUPPORT_SWING_MODE
        )

    async def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""

    async def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""

    async def set_swing_mode(self, swing_mode):
        """Set new target swing operation."""

    async def set_temperature(self, **kwargs):
        """Set new target temperature."""

class LGEAcSensor(LGESensor):
    """A sensor to monitor LGE Dryer devices"""

    @property
    def device_state_attributes(self):
        """Return the optional state attributes."""
        if not self._is_default:
            return None

        data = {
            ATTR_AC_CURRENT_TEMP: self._ac_current_temp,
            ATTR_AC_POWER_CONSUMPTION: self._ac_power_consumption,
            #ATTR_RUN_COMPLETED: self._run_completed,
            #ATTR_ERROR_STATE: self._error_state,
            #ATTR_ERROR_MSG: self._error_msg,
            ATTR_RUN_STATE: self._current_run_state,
            #ATTR_PRE_STATE: self._pre_state,
            #ATTR_CURRENT_COURSE: self._current_course,
            #ATTR_TEMPCONTROL_OPTION_STATE: self._tempcontrol_option_state,
            #ATTR_DRYLEVEL_OPTION_STATE: self._drylevel_option_state,
            # ATTR_TIMEDRY_OPTION_STATE: self._timedry_option_state,
            #ATTR_REMAIN_TIME: self._remain_time,
            #ATTR_INITIAL_TIME: self._initial_time,
            #ATTR_RESERVE_TIME: self._reserve_time,
            #ATTR_DOORLOCK_MODE: self._doorlock_mode,
            #ATTR_CHILDLOCK_MODE: self._childlock_mode,
        }
        return data

    @property
    def _run_completed(self):
        return STATE_ON

    @property
    def _error_state(self):
        if self._api.state:
            if self._api.state.is_error:
                # self._api.state = AcStatus ac.py
                return STATE_ON
        return STATE_OFF

    @property
    def _error_msg(self):
        if self._api.state:
            error = self._api.state.error_state
            return error
        return "-"

    @property
    def _current_run_state(self):
        if self._api.state:
            run_state = self._api.state.run_state
            return run_state
        return "-"

    @property
    def _temp_unit(self):
        return TEMP_CELSIUS
    @property
    def _energy_unit(self):
        return ENERGY_KILO_WATT_HOUR
    @property
    def _ac_current_temp(self):
        return self._api.state.ac_current_temp
    @property
    def _ac_power_consumption(self):
        return self._api.state.ac_power_consumpion
