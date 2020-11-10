"""
Support to interface with LGE ThinQ Devices.
"""

__version__ = "0.1b"
PROJECT_URL = "https://github.com/brunostavares/ha-smartthinq-sensors"
ISSUE_URL = "{}issues".format(PROJECT_URL)

DOMAIN = "smartthinq_hvac"

CONF_LANGUAGE = "language"
CONF_OAUTH_URL = "outh_url"
CONF_OAUTH_USER_NUM = "outh_user_num"
CONF_USE_API_V2 = "use_api_v2"

ATTR_CONFIG = "config"
CLIENT = "client"
LGE_DEVICES = "lge_devices"

SMARTTHINQ_COMPONENTS = [
    "climate"
]

STARTUP = """
-------------------------------------------------------------------
{}
Version: {}
This is a custom component
If you have any issues with this you need to open an issue here:
{}
-------------------------------------------------------------------
""".format(
    DOMAIN, __version__, ISSUE_URL
)
