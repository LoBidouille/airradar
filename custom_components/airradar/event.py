"""Event platform for AirRadar."""

from __future__ import annotations

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import AirRadarCoordinator

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up AirRadar event entity."""
    coordinator: AirRadarCoordinator = entry.runtime_data
    async_add_entities([AirRadarPassageEvent(coordinator)])


class AirRadarPassageEvent(EventEntity):
    """Event fired when a new aircraft enters the configured alert zone."""

    _attr_has_entity_name = True
    _attr_name = "Passage avion"
    _attr_icon = "mdi:airplane"
    _attr_event_types = ["passage"]

    def __init__(self, coordinator: AirRadarCoordinator) -> None:
        """Initialize passage event."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.entry.entry_id}_passage"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name="AirRadar",
            manufacturer="AirRadar",
            model="ADSB.lol + ADSBDB",
            sw_version="1.0.0",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe after entity registration."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_passage_listener(self._handle_passage)
        )

    @callback
    def _handle_passage(self, passage: dict) -> None:
        """Publish the AirRadar passage event."""
        self._trigger_event("passage", passage)
        self.async_write_ha_state()
