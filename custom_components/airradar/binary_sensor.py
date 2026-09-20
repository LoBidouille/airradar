"""Binary sensor platform for AirRadar."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import AirRadarCoordinator
from .entity import AirRadarEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up AirRadar binary sensors."""
    coordinator: AirRadarCoordinator = entry.runtime_data
    async_add_entities([AirRadarAlertBinarySensor(coordinator)])


class AirRadarAlertBinarySensor(AirRadarEntity, BinarySensorEntity):
    """Whether at least one aircraft currently meets alert thresholds."""

    _attr_name = "Avion dans zone alerte"
    _attr_icon = "mdi:airplane-alert"

    def __init__(self, coordinator: AirRadarCoordinator) -> None:
        """Initialize binary sensor."""
        AirRadarEntity.__init__(self, coordinator, "alert_active")

    @property
    def is_on(self) -> bool:
        """Return alert state."""
        return bool((self.coordinator.data or {}).get("alert_active", False))
