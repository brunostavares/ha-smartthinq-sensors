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

from homeassistant.const import CONF_REGION, CONF_TOKEN

from homeassistant.components.binary_sensor import DEVICE_CLASS_PROBLEM, DEVICE_CLASS_OPENING
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import Entity

from homeassistant.components import climate
from homeassistant.components.climate import const as c_const
try:
    from homeassistant.components.climate import ClimateEntity
except ImportError:
    from homeassistant.components.climate import ClimateDevice \
         as ClimateEntity

from . import LGEAuthentication


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

from .const import DOMAIN, LGE_DEVICES, CONF_LANGUAGE, CONF_OAUTH_URL, CONF_OAUTH_USER_NUM
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

# washer sensor attributes
ATTR_SPIN_OPTION_STATE = "spin_option_state"
ATTR_WATERTEMP_OPTION_STATE = "watertemp_option_state"
ATTR_CREASECARE_MODE = "creasecare_mode"
ATTR_CHILDLOCK_MODE = "childlock_mode"
ATTR_STEAM_MODE = "steam_mode"
ATTR_STEAM_SOFTENER_MODE = "steam_softener_mode"
ATTR_DOORLOCK_MODE = "doorlock_mode"
ATTR_DOORCLOSE_MODE = "doorclose_mode"
ATTR_PREWASH_MODE = "prewash_mode"
ATTR_REMOTESTART_MODE = "remotestart_mode"
ATTR_TURBOWASH_MODE = "turbowash_mode"
ATTR_TUBCLEAN_COUNT = "tubclean_count"

# dryer sensor attributes
ATTR_TEMPCONTROL_OPTION_STATE = "tempcontrol_option_state"
ATTR_DRYLEVEL_OPTION_STATE = "drylevel_option_state"
ATTR_TIMEDRY_OPTION_STATE = "timedry_option_state"

# ac sensor attributes
ATTR_AC_CURRENT_TEMP = "tempState_current"
ATTR_AC_POWER_CONSUMPTION = "consumo_de_energia"

# dishwasher sensor attributes
ATTR_PROCESS_STATE = "process_state"
ATTR_DELAYSTART_MODE = "delay_start_mode"
ATTR_ENERGYSAVER_MODE = "energy_saver_mode"
ATTR_DUALZONE_MODE = "dual_zone_mode"
ATTR_HALFLOAD_MODE = "half_load_mode"
ATTR_RINSEREFILL_STATE = "rinse_refill_state"
ATTR_SALTREFILL_STATE = "salt_refill_state"

# refrigerator sensor attributes
ATTR_REFRIGERATOR_TEMP = "refrigerator_temp"
ATTR_FREEZER_TEMP = "freezer_temp"
ATTR_TEMP_UNIT = "temp_unit"
ATTR_DOOROPEN_STATE = "door_open_state"

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

WASHER_SENSORS = {
    DEFAULT_SENSOR: {
        ATTR_MEASUREMENT_NAME: "Default",
        ATTR_ICON: "mdi:washing-machine",
        ATTR_UNIT_FN: lambda x: None,
        # ATTR_UNIT_FN: lambda x: "dBm",
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._power_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

WASHER_BINARY_SENSORS = {
    ATTR_RUN_COMPLETED: {
        ATTR_MEASUREMENT_NAME: "Wash Completed",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._run_completed,
        ATTR_ENABLED_FN: lambda x: True,
    },
    ATTR_ERROR_STATE: {
        ATTR_MEASUREMENT_NAME: "Error State",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PROBLEM,
        ATTR_VALUE_FN: lambda x: x._error_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

DRYER_SENSORS = {
    DEFAULT_SENSOR: {
        ATTR_MEASUREMENT_NAME: "Default",
        ATTR_ICON: "mdi:tumble-dryer",
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._power_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

DRYER_BINARY_SENSORS = {
    ATTR_RUN_COMPLETED: {
        ATTR_MEASUREMENT_NAME: "Dry Completed",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._run_completed,
        ATTR_ENABLED_FN: lambda x: True,
    },
    ATTR_ERROR_STATE: {
        ATTR_MEASUREMENT_NAME: "Error State",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PROBLEM,
        ATTR_VALUE_FN: lambda x: x._error_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

AC_SENSORS = {
    DEFAULT_SENSOR: {
        ATTR_MEASUREMENT_NAME: "Default",
        ATTR_ICON: "mdi:air-conditioner",
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._power_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
    ATTR_AC_CURRENT_TEMP: {
        ATTR_MEASUREMENT_NAME: "Temperatura ambiente",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: x._temp_unit,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_VALUE_FN: lambda x: x._ac_current_temp,
        ATTR_ENABLED_FN: lambda x: True,
    },
    ATTR_AC_POWER_CONSUMPTION: {
        ATTR_MEASUREMENT_NAME: "consumo de energia",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: x._energy_unit,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_POWER,
        ATTR_VALUE_FN: lambda x: x._ac_power_consumption,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

AC_BINARY_SENSORS = {
    ATTR_RUN_COMPLETED: {
        ATTR_MEASUREMENT_NAME: "Turn on",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._power_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
    ATTR_ERROR_STATE: {
        ATTR_MEASUREMENT_NAME: "Error State",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PROBLEM,
        ATTR_VALUE_FN: lambda x: x._error_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

DISHWASHER_SENSORS = {
    DEFAULT_SENSOR: {
        ATTR_MEASUREMENT_NAME: "Default",
        ATTR_ICON: "mdi:dishwasher",
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._power_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

DISHWASHER_BINARY_SENSORS = {
    ATTR_RUN_COMPLETED: {
        ATTR_MEASUREMENT_NAME: "Wash Completed",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._run_completed,
        ATTR_ENABLED_FN: lambda x: True,
    },
    ATTR_ERROR_STATE: {
        ATTR_MEASUREMENT_NAME: "Error State",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PROBLEM,
        ATTR_VALUE_FN: lambda x: x._error_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

REFRIGERATOR_SENSORS = {
    DEFAULT_SENSOR: {
        ATTR_MEASUREMENT_NAME: "Default",
        ATTR_ICON: "mdi:fridge-outline",
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: None,
        ATTR_VALUE_FN: lambda x: x._power_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
    ATTR_REFRIGERATOR_TEMP: {
        ATTR_MEASUREMENT_NAME: "Refrigerator Temp",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: x._temp_unit,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_VALUE_FN: lambda x: x._temp_refrigerator,
        ATTR_ENABLED_FN: lambda x: True,
    },
    ATTR_FREEZER_TEMP: {
        ATTR_MEASUREMENT_NAME: "Freezer Temp",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: x._temp_unit,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_VALUE_FN: lambda x: x._temp_freezer,
        ATTR_ENABLED_FN: lambda x: True,
    },
}

REFRIGERATOR_BINARY_SENSORS = {
    ATTR_DOOROPEN_STATE: {
        ATTR_MEASUREMENT_NAME: "Door Open",
        ATTR_ICON: None,
        ATTR_UNIT_FN: lambda x: None,
        ATTR_DEVICE_CLASS: DEVICE_CLASS_OPENING,
        ATTR_VALUE_FN: lambda x: x._dooropen_state,
        ATTR_ENABLED_FN: lambda x: True,
    },
}


def setup_platform(hass, config, async_add_entities, discovery_info=None):
    pass


async def async_setup_sensors(hass, config_entry, async_add_entities, type_binary):
    """Set up LGE device sensors and bynary sensor based on config_entry."""


    refresh_token = config_entry.data.get(CONF_TOKEN)
    region = config_entry.data.get(CONF_REGION)
    language = config_entry.data.get(CONF_LANGUAGE)
    use_apiv2 = config_entry.data.get(CONF_USE_API_V2, False)
    oauth_url = config_entry.data.get(CONF_OAUTH_URL)
    oauth_user_num = config_entry.data.get(CONF_OAUTH_USER_NUM)

    _LOGGER.info(
        "Initializing SmartThinQ platform with region: %s - language: %s",
        region,
        language,
    )

    hass.data.setdefault(DOMAIN, {})[LGE_DEVICES] = {}

    # if network is not connected we can have some error
    # raising ConfigEntryNotReady platform setup will be retried
    lgeauth = LGEAuthentication(region, language, use_apiv2)
    client = await hass.async_add_executor_job(
        lgeauth.createClientFromToken, refresh_token, oauth_url, oauth_user_num
    )

    async_add_entities(_ac_devices(hass, client), True)

def _ac_devices(hass, client):
    """Generate all the AC (climate) devices associated with the user's
    LG account.
    Log errors for devices that can't be used for whatever reason.
    """
    persistent_notification = hass.components.persistent_notification

    for device in client.devices:
        try:
            d = LGESensor(client, device)
        except wideq.NotConnectedError:
            LOGGER.error(
                'SmartThinQ device not available: %s', device.name
            )
            persistent_notification.async_create(
                'SmartThinQ device not available: %s' % device.name,
                title='SmartThinQ Error',
            )
        else:
            yield d

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the LGE sensors."""
    _LOGGER.info("Starting LGE ThinQ sensors...")
    await async_setup_sensors(hass, config_entry, async_add_entities, False)


class LGESensor(ClimateEntity):
    def __init__(self, client, device):
        """Initialize the sensor."""
        self._api = device
        self._name_slug = device.name
        self._is_default = DEFAULT_SENSOR
        self._unsub_dispatcher = None

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def hvac_modes(self):
        return [c_const.HVAC_MODE_OFF]

    @property
    def hvac_mode(self):
        return "Selected mode"

    def set_hvac_mode(self, hvac_mode):
        _LOGGER.warning(hvac_mode)
        return

    @property
    def fan_modes(self):
        import wideq
        return ["aaaaaaaaaaaaaaaaaaa"]

    @property
    def supported_features(self):
        return (
            c_const.SUPPORT_TARGET_TEMPERATURE |
            c_const.SUPPORT_FAN_MODE |
            c_const.SUPPORT_SWING_MODE
        )


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
        return self._name_slug
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._api.available

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

    def set_swing_mode(self, swing_mode):
        self._swing_mode = swing_mode
        LOGGER.info('Setting swing mode to %s...', self._swing_mode)
    
    @property
    def swing_modes(self):
        return ["AAAAAAAAAAAAAAAA"]
            
    @property
    def swing_mode(self):
        return "SWING_MODE_DEFAULT"

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


class LGEWasherSensor(LGESensor):
    """A sensor to monitor LGE Washer devices"""

    @property
    def device_state_attributes(self):
        """Return the optional state attributes."""
        if not self._is_default:
            return None

        data = {
            ATTR_RUN_COMPLETED: self._run_completed,
            ATTR_ERROR_STATE: self._error_state,
            ATTR_ERROR_MSG: self._error_msg,
            ATTR_RUN_STATE: self._current_run_state,
            ATTR_PRE_STATE: self._pre_state,
            ATTR_CURRENT_COURSE: self._current_course,
            ATTR_SPIN_OPTION_STATE: self._spin_option_state,
            ATTR_WATERTEMP_OPTION_STATE: self._watertemp_option_state,
            ATTR_DRYLEVEL_OPTION_STATE: self._drylevel_option_state,
            ATTR_TUBCLEAN_COUNT: self._tubclean_count,
            ATTR_REMAIN_TIME: self._remain_time,
            ATTR_INITIAL_TIME: self._initial_time,
            ATTR_RESERVE_TIME: self._reserve_time,
            ATTR_DOORLOCK_MODE: self._doorlock_mode,
            ATTR_DOORCLOSE_MODE: self._doorclose_mode,
            ATTR_CHILDLOCK_MODE: self._childlock_mode,
            ATTR_REMOTESTART_MODE: self._remotestart_mode,
            ATTR_CREASECARE_MODE: self._creasecare_mode,
            ATTR_STEAM_MODE: self._steam_mode,
            ATTR_STEAM_SOFTENER_MODE: self._steam_softener_mode,
            ATTR_PREWASH_MODE: self._prewash_mode,
            ATTR_TURBOWASH_MODE: self._turbowash_mode,
        }
        return data

    @property
    def _run_completed(self):
        if self._api.state:
            if self._api.state.is_run_completed:
                return STATE_ON
        return STATE_OFF

    @property
    def _current_run_state(self):
        if self._api.state:
            run_state = self._api.state.run_state
            return run_state
        return "-"

    @property
    def _pre_state(self):
        if self._api.state:
            pre_state = self._api.state.pre_state
            return pre_state
        return "-"

    @property
    def _remain_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.remaintime_hour,
                    self._api.state.remaintime_min
                )
        return "0:00"

    @property
    def _initial_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.initialtime_hour,
                    self._api.state.initialtime_min
                )
        return "0:00"

    @property
    def _reserve_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.reservetime_hour,
                    self._api.state.reservetime_min
                )
        return "0:00"

    @property
    def _current_course(self):
        if self._api.state:
            if self._api.state.is_on:
                course = self._api.state.current_course
                if course:
                    return course
                smartcourse = self._api.state.current_smartcourse
                if smartcourse:
                    return smartcourse
        return "-"

    @property
    def _error_state(self):
        if self._api.state:
            if self._api.state.is_error:
                return STATE_ON
        return STATE_OFF

    @property
    def _error_msg(self):
        if self._api.state:
            error = self._api.state.error_state
            return error
        return "-"

    @property
    def _spin_option_state(self):
        if self._api.state:
            spin_option = self._api.state.spin_option_state
            return spin_option
        return "-"

    @property
    def _watertemp_option_state(self):
        if self._api.state:
            watertemp_option = self._api.state.water_temp_option_state
            return watertemp_option
        return "-"

    @property
    def _drylevel_option_state(self):
        if self._api.state:
            drylevel_option = self._api.state.dry_level_option_state
            return drylevel_option
        return "-"

    @property
    def _tubclean_count(self):
        if self._api.state:
            tubclean_count = self._api.state.tubclean_count
            return tubclean_count
        return "N/A"

    @property
    def _doorlock_mode(self):
        if self._api.state:
            mode = self._api.state.doorlock_state
            return mode
        return None

    @property
    def _doorclose_mode(self):
        if self._api.state:
            mode = self._api.state.doorclose_state
            return mode
        return None

    @property
    def _childlock_mode(self):
        if self._api.state:
            mode = self._api.state.childlock_state
            return mode
        return None

    @property
    def _remotestart_mode(self):
        if self._api.state:
            mode = self._api.state.remotestart_state
            return mode
        return None

    @property
    def _creasecare_mode(self):
        if self._api.state:
            mode = self._api.state.creasecare_state
            return mode
        return None

    @property
    def _steam_mode(self):
        if self._api.state:
            mode = self._api.state.steam_state
            return mode
        return None

    @property
    def _steam_softener_mode(self):
        if self._api.state:
            mode = self._api.state.steam_softener_state
            return mode
        return None

    @property
    def _prewash_mode(self):
        if self._api.state:
            mode = self._api.state.prewash_state
            return mode
        return None

    @property
    def _turbowash_mode(self):
        if self._api.state:
            mode = self._api.state.turbowash_state
            return mode
        return None


class LGEDryerSensor(LGESensor):
    """A sensor to monitor LGE Dryer devices"""

    @property
    def device_state_attributes(self):
        """Return the optional state attributes."""
        if not self._is_default:
            return None

        data = {
            ATTR_RUN_COMPLETED: self._run_completed,
            ATTR_ERROR_STATE: self._error_state,
            ATTR_ERROR_MSG: self._error_msg,
            ATTR_RUN_STATE: self._current_run_state,
            ATTR_PRE_STATE: self._pre_state,
            ATTR_CURRENT_COURSE: self._current_course,
            ATTR_TEMPCONTROL_OPTION_STATE: self._tempcontrol_option_state,
            ATTR_DRYLEVEL_OPTION_STATE: self._drylevel_option_state,
            # ATTR_TIMEDRY_OPTION_STATE: self._timedry_option_state,
            ATTR_REMAIN_TIME: self._remain_time,
            ATTR_INITIAL_TIME: self._initial_time,
            ATTR_RESERVE_TIME: self._reserve_time,
            ATTR_DOORLOCK_MODE: self._doorlock_mode,
            ATTR_CHILDLOCK_MODE: self._childlock_mode,
        }
        return data

    @property
    def _run_completed(self):
        if self._api.state:
            if self._api.state.is_run_completed:
                return STATE_ON
        return STATE_OFF

    @property
    def _current_run_state(self):
        if self._api.state:
            run_state = self._api.state.run_state
            return run_state
        return "-"

    @property
    def _pre_state(self):
        if self._api.state:
            pre_state = self._api.state.pre_state
            return pre_state
        return "-"

    @property
    def _remain_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.remaintime_hour,
                    self._api.state.remaintime_min
                )
        return "0:00"

    @property
    def _initial_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.initialtime_hour,
                    self._api.state.initialtime_min
                )
        return "0:00"

    @property
    def _reserve_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.reservetime_hour,
                    self._api.state.reservetime_min
                )
        return "0:00"

    @property
    def _current_course(self):
        if self._api.state:
            if self._api.state.is_on:
                course = self._api.state.current_course
                if course:
                    return course
                smartcourse = self._api.state.current_smartcourse
                if smartcourse:
                    return smartcourse
        return "-"

    @property
    def _error_state(self):
        if self._api.state:
            if self._api.state.is_error:
                return STATE_ON
        return STATE_OFF

    @property
    def _error_msg(self):
        if self._api.state:
            error = self._api.state.error_state
            return error
        return "-"

    @property
    def _tempcontrol_option_state(self):
        if self._api.state:
            temp_option = self._api.state.temp_control_option_state
            return temp_option
        return "-"

    @property
    def _drylevel_option_state(self):
        if self._api.state:
            drylevel_option = self._api.state.dry_level_option_state
            return drylevel_option
        return "-"

    @property
    def _timedry_option_state(self):
        if self._api.state:
            timedry_option = self._api.state.time_dry_option_state
            return timedry_option
        return "-"

    @property
    def _doorlock_mode(self):
        if self._api.state:
            mode = self._api.state.doorlock_state
            return mode
        return None

    @property
    def _childlock_mode(self):
        if self._api.state:
            mode = self._api.state.childlock_state
            return mode
        return None

class LGEAcSensor(LGESensor):
    """A sensor to monitor LGE Dryer devices"""

    @property
    def device_state_attributes(self):
        """Return the optional state attributes."""
        if not self._is_default:
            return None

        data = {
            ATTR_TEMP_UNIT: self._temp_unit,
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

class LGEDishWasherSensor(LGESensor):
    """A sensor to monitor LGE DishWasher devices"""

    @property
    def device_state_attributes(self):
        """Return the optional state attributes."""
        if not self._is_default:
            return None

        data = {
            ATTR_RUN_COMPLETED: self._run_completed,
            ATTR_ERROR_STATE: self._error_state,
            ATTR_ERROR_MSG: self._error_msg,
            ATTR_DOOROPEN_STATE: self._dooropen_state,
            ATTR_RINSEREFILL_STATE: self._rinserefill_state,
            ATTR_SALTREFILL_STATE: self._saltrefill_state,
            ATTR_RUN_STATE: self._current_run_state,
            ATTR_PROCESS_STATE: self._process_state,
            ATTR_CURRENT_COURSE: self._current_course,
            ATTR_TUBCLEAN_COUNT: self._tubclean_count,
            ATTR_REMAIN_TIME: self._remain_time,
            ATTR_INITIAL_TIME: self._initial_time,
            ATTR_RESERVE_TIME: self._reserve_time,
            ATTR_HALFLOAD_MODE: self._halfload_mode,
            ATTR_CHILDLOCK_MODE: self._childlock_mode,
            ATTR_DELAYSTART_MODE: self._delaystart_mode,
            ATTR_ENERGYSAVER_MODE: self._energysaver_mode,
            ATTR_DUALZONE_MODE: self._dualzone_mode,
        }
        return data

    @property
    def _run_completed(self):
        if self._api.state:
            if self._api.state.is_run_completed:
                return STATE_ON
        return STATE_OFF

    @property
    def _current_run_state(self):
        if self._api.state:
            run_state = self._api.state.run_state
            return run_state
        return "-"

    @property
    def _process_state(self):
        if self._api.state:
            process = self._api.state.process_state
            return process
        return "-"

    @property
    def _remain_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.remaintime_hour,
                    self._api.state.remaintime_min
                )
        return "0:00"

    @property
    def _initial_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.initialtime_hour,
                    self._api.state.initialtime_min
                )
        return "0:00"

    @property
    def _reserve_time(self):
        if self._api.state:
            if self._api.state.is_on:
                return LGESensor.format_time(
                    self._api.state.reservetime_hour,
                    self._api.state.reservetime_min
                )
        return "0:00"

    @property
    def _current_course(self):
        if self._api.state:
            if self._api.state.is_on:
                course = self._api.state.current_course
                if course:
                    return course
                smartcourse = self._api.state.current_smartcourse
                if smartcourse:
                    return smartcourse
        return "-"

    @property
    def _error_state(self):
        if self._api.state:
            if self._api.state.is_error:
                return STATE_ON
        return STATE_OFF

    @property
    def _error_msg(self):
        if self._api.state:
            error = self._api.state.error_state
            return error
        return "-"

    @property
    def _tubclean_count(self):
        if self._api.state:
            tubclean_count = self._api.state.tubclean_count
            return tubclean_count
        return "N/A"

    @property
    def _dooropen_state(self):
        if self._api.state:
            state = self._api.state.door_opened_state
            return STATE_LOOKUP.get(state, STATE_OFF)
        return None

    @property
    def _rinserefill_state(self):
        if self._api.state:
            state = self._api.state.rinserefill_state
            return STATE_LOOKUP.get(state, STATE_OFF)
        return STATE_OFF

    @property
    def _saltrefill_state(self):
        if self._api.state:
            state = self._api.state.saltrefill_state
            return STATE_LOOKUP.get(state, STATE_OFF)
        return STATE_OFF

    @property
    def _halfload_mode(self):
        if self._api.state:
            mode = self._api.state.halfload_state
            return mode
        return None

    @property
    def _childlock_mode(self):
        if self._api.state:
            mode = self._api.state.childlock_state
            return mode
        return None

    @property
    def _delaystart_mode(self):
        if self._api.state:
            mode = self._api.state.delaystart_state
            return mode
        return None

    @property
    def _energysaver_mode(self):
        if self._api.state:
            mode = self._api.state.energysaver_state
            return mode
        return None

    @property
    def _dualzone_mode(self):
        if self._api.state:
            mode = self._api.state.dualzone_state
            return mode
        return None


class LGERefrigeratorSensor(LGESensor):
    """A sensor to monitor LGE Refrigerator devices"""

    @property
    def device_state_attributes(self):
        """Return the optional state attributes."""
        if not self._is_default:
            return None

        data = {
            ATTR_REFRIGERATOR_TEMP: self._temp_refrigerator,
            ATTR_FREEZER_TEMP: self._temp_freezer,
            ATTR_TEMP_UNIT: self._temp_unit,
            ATTR_DOOROPEN_STATE: self._dooropen_state,
        }

        if self._api.state:
            for name, value in self._api.state.device_features.items():
                data[name] = value

        return data

    @property
    def _temp_refrigerator(self):
        if self._api.state:
            return self._api.state.temp_refrigerator
        return None

    @property
    def _temp_freezer(self):
        if self._api.state:
            return self._api.state.temp_freezer
        return None

    @property
    def _temp_unit(self):
        if self._api.state:
            unit = self._api.state.temp_unit
            return TEMP_UNIT_LOOKUP.get(unit, TEMP_CELSIUS)
        return TEMP_CELSIUS

    @property
    def _dooropen_state(self):
        if self._api.state:
            state = self._api.state.door_opened_state
            return STATE_LOOKUP.get(state, STATE_OFF)
        return STATE_OFF
