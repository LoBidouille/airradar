"""Base entity for AirRadar."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AirRadarCoordinator


class AirRadarEntity(CoordinatorEntity[AirRadarCoordinator]):
    """Base AirRadar coordinator entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AirRadarCoordinator, key: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name="AirRadar",
            manufacturer="AirRadar",
            model="ADSB.lol + ADSBDB",
            sw_version="1.0.0",
        )
