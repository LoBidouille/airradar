"""Sensor platform for AirRadar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength, UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import AirRadarCoordinator
from .entity import AirRadarEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class AirRadarSensorDescription(SensorEntityDescription):
    """Describe an AirRadar sensor."""

    value_fn: Callable[[dict[str, Any]], StateType]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None


def _nearest(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("nearest") or {}


def _last(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("last_passage") or {}


SENSORS: tuple[AirRadarSensorDescription, ...] = (
    AirRadarSensorDescription(
        key="nearest_callsign",
        name="Avion le plus proche",
        icon="mdi:airplane",
        value_fn=lambda d: _nearest(d).get("callsign"),
    ),
    AirRadarSensorDescription(
        key="nearest_distance",
        name="Distance avion",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=2,
        value_fn=lambda d: _nearest(d).get("distance_km"),
    ),
    AirRadarSensorDescription(
        key="nearest_altitude",
        name="Altitude avion",
        icon="mdi:altimeter",
        native_unit_of_measurement=UnitOfLength.METERS,
        value_fn=lambda d: _nearest(d).get("altitude_m"),
    ),
    AirRadarSensorDescription(
        key="nearest_speed",
        name="Vitesse avion",
        icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        value_fn=lambda d: _nearest(d).get("speed_kmh"),
    ),
    AirRadarSensorDescription(
        key="nearest_company",
        name="Compagnie",
        icon="mdi:office-building",
        value_fn=lambda d: _nearest(d).get("company") or None,
    ),
    AirRadarSensorDescription(
        key="nearest_route",
        name="Trajet",
        icon="mdi:map-marker-path",
        value_fn=lambda d: _nearest(d).get("route") or None,
    ),
    AirRadarSensorDescription(
        key="nearest_registration",
        name="Immatriculation",
        icon="mdi:identifier",
        value_fn=lambda d: _nearest(d).get("registration") or None,
    ),
    AirRadarSensorDescription(
        key="nearest_type",
        name="Type avion",
        icon="mdi:airplane-settings",
        value_fn=lambda d: (
            _nearest(d).get("model")
            or _nearest(d).get("type")
            or None
        ),
    ),
    AirRadarSensorDescription(
        key="aircraft_count",
        name="Avions détectés",
        icon="mdi:airplane-marker",
        value_fn=lambda d: d.get("aircraft_count", 0),
    ),
    AirRadarSensorDescription(
        key="last_passage",
        name="Dernier passage",
        icon="mdi:airplane-clock",
        value_fn=lambda d: _last(d).get("callsign"),
        attrs_fn=lambda d: _last(d) or None,
    ),
    AirRadarSensorDescription(
        key="last_passage_distance",
        name="Distance dernier passage",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        suggested_display_precision=2,
        value_fn=lambda d: _last(d).get("distance_km"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up AirRadar sensors."""
    coordinator: AirRadarCoordinator = entry.runtime_data
    async_add_entities(
        AirRadarSensor(coordinator, description) for description in SENSORS
    )


class AirRadarSensor(AirRadarEntity, SensorEntity):
    """AirRadar sensor."""

    entity_description: AirRadarSensorDescription

    def __init__(
        self,
        coordinator: AirRadarCoordinator,
        description: AirRadarSensorDescription,
    ) -> None:
        """Initialize a sensor."""
        AirRadarEntity.__init__(self, coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_suggested_display_precision = description.suggested_display_precision

    @property
    def native_value(self) -> StateType:
        """Return current value."""
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return optional attributes."""
        if self.entity_description.attrs_fn is None:
            return None
        return self.entity_description.attrs_fn(self.coordinator.data or {})
