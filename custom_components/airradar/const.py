"""Constants for the AirRadar integration."""

DOMAIN = "airradar"

CONF_DISTANCE_KM = "distance_km"
CONF_ALTITUDE_M = "altitude_m"
CONF_POLL_INTERVAL = "poll_interval"
CONF_NOTIFICATIONS = "notifications"
CONF_NOTIFY_SERVICE = "notify_service"

DEFAULT_DISTANCE_KM = 2.0
DEFAULT_ALTITUDE_M = 5000
DEFAULT_POLL_INTERVAL = 15
DEFAULT_NOTIFICATIONS = True
DEFAULT_NOTIFY_SERVICE = ""

MIN_DISTANCE_KM = 0.5
MAX_DISTANCE_KM = 20.0
MIN_ALTITUDE_M = 500
MAX_ALTITUDE_M = 15000
MIN_POLL_INTERVAL = 10
MAX_POLL_INTERVAL = 60

HYSTERESIS_KM = 1.0

ADSB_PROVIDERS = (
    ("ADSB.lol", "https://api.adsb.lol/v2/point/{lat}/{lon}/{radius_nm}"),
    ("Airplanes.live", "https://api.airplanes.live/v2/point/{lat}/{lon}/{radius_nm}"),
    ("adsb.fi", "https://opendata.adsb.fi/api/v3/lat/{lat}/lon/{lon}/dist/{radius_nm}"),
)
ADSBDB_URL = "https://api.adsbdb.com/v0/callsign/{callsign}"

USER_AGENT = "HomeAssistant-AirRadar/1.0.2"
