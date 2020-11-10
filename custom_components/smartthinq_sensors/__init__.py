"""
Support for LG SmartThinQ device.
"""
# REQUIREMENTS = ['wideq']

import asyncio
import logging
import time
from datetime import timedelta
from requests import exceptions as reqExc
from typing import Dict

from .wideq.core import Client
from .wideq.core_v2 import ClientV2
from .wideq.device import DeviceType
from .wideq.dishwasher import DishWasherDevice
from .wideq.dryer import DryerDevice
from .wideq.washer import WasherDevice
from .wideq.refrigerator import RefrigeratorDevice
from .wideq.ac import AcDevice

from .wideq.core_exceptions import (
    InvalidCredentialError,
    NotConnectedError,
    NotLoggedInError,
    TokenError,
)

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import Throttle

from homeassistant.const import CONF_REGION, CONF_TOKEN

from homeassistant.components.climate import const as c_const
from homeassistant import const
from homeassistant.components import climate

try:
    from homeassistant.components.climate import ClimateEntity
except ImportError:
    from homeassistant.components.climate import ClimateDevice \
         as ClimateEntity


from .const import (
    ATTR_CONFIG,
    CLIENT,
    CONF_LANGUAGE,
    CONF_OAUTH_URL,
    CONF_OAUTH_USER_NUM,
    CONF_USE_API_V2,
    DOMAIN,
    LGE_DEVICES,
    SMARTTHINQ_COMPONENTS,
    STARTUP,
)

ATTR_MODEL = "model"
ATTR_MAC_ADDRESS = "mac_address"

MAX_RETRIES = 3
MAX_CONN_RETRIES = 2
MAX_LOOP_WARN = 3
MAX_UPDATE_FAIL_ALLOWED = 10
# not stress to match cloud if multiple call
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

SMARTTHINQ_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
        vol.Required(CONF_REGION): str,
        vol.Required(CONF_LANGUAGE): str,
    }
)

CONFIG_SCHEMA = vol.Schema(
    vol.All(
        cv.deprecated(DOMAIN),
        {
            DOMAIN: SMARTTHINQ_SCHEMA
        },
    ),
    extra=vol.ALLOW_EXTRA,
)


_LOGGER = logging.getLogger(__name__)


class LGEAuthentication:
    def __init__(self, region, language, use_api_v2=True):
        self._region = region
        self._language = language
        self._use_api_v2 = use_api_v2

    def _create_client(self):
        if self._use_api_v2:
            client = ClientV2(country=self._region, language=self._language)
        else:
            client = Client(country=self._region, language=self._language)

        return client

    def getLoginUrl(self) -> str:

        login_url = None
        client = self._create_client()

        try:
            login_url = client.gateway.oauth_url()
        except Exception:
            _LOGGER.exception("Error retrieving login URL from ThinQ")

        return login_url

    def getOAuthInfoFromUrl(self, callback_url) -> Dict[str, str]:

        oauth_info = None
        try:
            if self._use_api_v2:
                oauth_info = ClientV2.oauthinfo_from_url(callback_url)
            else:
                oauth_info = Client.oauthinfo_from_url(callback_url)
        except Exception:
            _LOGGER.exception("Error retrieving OAuth info from ThinQ")

        return oauth_info

    def createClientFromToken(self, token, oauth_url=None, oauth_user_num=None):

        client = None
        try:
            if self._use_api_v2:
                client = ClientV2.from_token(
                    oauth_url, token, oauth_user_num, self._region, self._language
                )
            else:
                client = Client.from_token(token, self._region, self._language)
        except Exception:
            _LOGGER.exception("Error connecting to ThinQ")

        return client


def setup_platform(hass, config, add_devices, discovery_info=None):
    
    config_entry = hass.data[DOMAIN]
    
    refresh_token = config_entry.data.get(CONF_TOKEN)
    region = config_entry.data.get(CONF_REGION)
    language = config_entry.data.get(CONF_LANGUAGE)
    use_apiv2 = config_entry.data.get(CONF_USE_API_V2, False)
    oauth_url = config_entry.data.get(CONF_OAUTH_URL)
    oauth_user_num = config_entry.data.get(CONF_OAUTH_USER_NUM)


    hass.data.setdefault(DOMAIN, {})[LGE_DEVICES] = {}

    # if network is not connected we can have some error
    # raising ConfigEntryNotReady platform setup will be retried
    lgeauth = LGEAuthentication(region, language, use_apiv2)
    client = await hass.async_add_executor_job(
        lgeauth.createClientFromToken, refresh_token, oauth_url, oauth_user_num
    )
    if not client:
        _LOGGER.warning("Connection not available. SmartThinQ platform not ready")
        raise ConfigEntryNotReady()

    if not client.hasdevices:
        _LOGGER.error("No SmartThinQ devices found. Component setup aborted")
        return False

    _LOGGER.info("SmartThinQ client connected")

    hass.data.setdefault(DOMAIN, {}).update(
        {
            CLIENT: client,
            LGE_DEVICES: lge_devices,
        }
    )

    for platform in SMARTTHINQ_COMPONENTS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    add_devices(_ac_devices(hass, client, fahrenheit), True)


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await asyncio.gather(
        *[
            hass.config_entries.async_forward_entry_unload(config_entry, platform)
            for platform in SMARTTHINQ_COMPONENTS
        ]
    )

    hass.data.pop(DOMAIN)

    return True


def _ac_devices(hass, client, fahrenheit):
    """Generate all the AC (climate) devices associated with the user's
    LG account.
    Log errors for devices that can't be used for whatever reason.
    """
    persistent_notification = hass.components.persistent_notification

    for device in client.devices:
        d = LGDevice(client, device, fahrenheit)
        yield d


async def async_setup(hass, config):
    """
    This method gets called if HomeAssistant has a valid configuration entry within
    configurations.yaml.

    Thus, in this method we simply trigger the creation of a config entry.

    :return:
    """
    conf = config.get(DOMAIN)
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][ATTR_CONFIG] = conf

    if conf is not None:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data=conf
            )
        )

    return True

class LGDevice(ClimateEntity):
    def __init__(self, client, device, fahrenheit=True):
        self._client = client
        self._device = device
        self._fahrenheit = fahrenheit
        self._attrs = {}
        self._has_power = "maybe"

        import wideq
        self._ac = ACDevice(client, device)

        # The response from the monitoring query.
        self._state = None

        # Store a transient temperature when we've just set it. We also
        # store the timestamp for when we set this value.
        self._transient_temp = None
        self._transient_time = None
        
        self._swing_mode = SWING_MODE_DEFAULT

    @property
    def device_state_attributes(self):
        return self._attrs

    @property
    def temperature_unit(self):
        if self._fahrenheit:
            return const.TEMP_FAHRENHEIT
        else:
            return const.TEMP_CELSIUS

    @property
    def name(self):
        return self._device.name

    @property
    def available(self):
        return True

    @property
    def supported_features(self):
        return (
            c_const.SUPPORT_TARGET_TEMPERATURE |
            c_const.SUPPORT_FAN_MODE |
            c_const.SUPPORT_SWING_MODE
        )

    @property
    def hvac_modes(self):
        return [c_const.HVAC_MODE_OFF]

    @property
    def fan_modes(self):
        return ["aaaaaa","bbbbbb"]
    @property
    def hvac_mode(self):
        return HVAC_MODE_OFF
    @property
    def fan_mode(self):
        return "High"
    def set_hvac_mode(self, hvac_mode):
        _LOGGER.warning("SET HVAC")

    def set_fan_mode(self, fan_mode):
        _LOGGER.warning("SET FAN")


    def update(self):
        """Poll for updated device status."""