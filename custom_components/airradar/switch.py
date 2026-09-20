"""Switch platform for AirRadar."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_NOTIFICATIONS, DEFAULT_NOTIFICATIONS
from .coordinator import AirRadarCoordinator, _setting
from .entity import AirRadarEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up AirRadar switches."""
    coordinator: AirRadarCoordinator = entry.runtime_data
    async_add_entities([AirRadarNotificationSwitch(coordinator)])


class AirRadarNotificationSwitch(AirRadarEntity, SwitchEntity):
    """Enable or disable direct AirRadar notifications."""

    _attr_name = "Notifications avions"
    _attr_icon = "mdi:bell-ring"

    def __init__(self, coordinator: AirRadarCoordinator) -> None:
        """Initialize switch."""
        AirRadarEntity.__init__(self, coordinator, "notifications")

    @property
    def is_on(self) -> bool:
        """Return notification setting."""
        return bool(
            _setting(
                self.coordinator.entry,
                CONF_NOTIFICATIONS,
                DEFAULT_NOTIFICATIONS,
            )
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Enable notifications."""
        await self._async_set(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable notifications."""
        await self._async_set(False)

    async def _async_set(self, enabled: bool) -> None:
        options = dict(self.coordinator.entry.options)
        options[CONF_NOTIFICATIONS] = enabled
        self.hass.config_entries.async_update_entry(
            self.coordinator.entry,
            options=options,
        )
        self.async_write_ha_state()
