"""Number platform for AirRadar."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_ALTITUDE_M,
    CONF_DISTANCE_KM,
    DEFAULT_ALTITUDE_M,
    DEFAULT_DISTANCE_KM,
    MAX_ALTITUDE_M,
    MAX_DISTANCE_KM,
    MIN_ALTITUDE_M,
    MIN_DISTANCE_KM,
)
from .coordinator import AirRadarCoordinator, _setting
from .entity import AirRadarEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up AirRadar numbers."""
    coordinator: AirRadarCoordinator = entry.runtime_data
    async_add_entities(
        [
            AirRadarDistanceNumber(coordinator),
            AirRadarAltitudeNumber(coordinator),
        ]
    )


class _AirRadarSettingNumber(AirRadarEntity, NumberEntity):
    """Base configurable number."""

    _attr_mode = NumberMode.SLIDER

    setting_key: str
    default_value: float

    @property
    def native_value(self) -> float:
        """Return current setting."""
        return float(
            _setting(
                self.coordinator.entry,
                self.setting_key,
                self.default_value,
            )
        )

    async def async_set_native_value(self, value: float) -> None:
        """Persist a new setting and refresh."""
        options = dict(self.coordinator.entry.options)
        options[self.setting_key] = value
        self.hass.config_entries.async_update_entry(
            self.coordinator.entry,
            options=options,
        )
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()


class AirRadarDistanceNumber(_AirRadarSettingNumber):
    """Alert distance setting."""

    _attr_name = "Distance alerte"
    _attr_icon = "mdi:map-marker-radius"
    _attr_native_min_value = MIN_DISTANCE_KM
    _attr_native_max_value = MAX_DISTANCE_KM
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    setting_key = CONF_DISTANCE_KM
    default_value = DEFAULT_DISTANCE_KM

    def __init__(self, coordinator: AirRadarCoordinator) -> None:
        """Initialize number."""
        AirRadarEntity.__init__(self, coordinator, "distance_setting")


class AirRadarAltitudeNumber(_AirRadarSettingNumber):
    """Alert altitude setting."""

    _attr_name = "Altitude maxi alerte"
    _attr_icon = "mdi:altimeter"
    _attr_native_min_value = MIN_ALTITUDE_M
    _attr_native_max_value = MAX_ALTITUDE_M
    _attr_native_step = 100
    _attr_native_unit_of_measurement = UnitOfLength.METERS
    setting_key = CONF_ALTITUDE_M
    default_value = DEFAULT_ALTITUDE_M

    def __init__(self, coordinator: AirRadarCoordinator) -> None:
        """Initialize number."""
        AirRadarEntity.__init__(self, coordinator, "altitude_setting")
