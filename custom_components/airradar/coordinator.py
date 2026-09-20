"""Data coordinator for AirRadar."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
import logging
import math
from typing import Any
from urllib.parse import quote

from aiohttp import ClientError, ClientSession

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ADSB_URL,
    ADSBDB_URL,
    CONF_ALTITUDE_M,
    CONF_DISTANCE_KM,
    CONF_NOTIFICATIONS,
    CONF_NOTIFY_SERVICE,
    CONF_POLL_INTERVAL,
    DEFAULT_ALTITUDE_M,
    DEFAULT_DISTANCE_KM,
    DEFAULT_NOTIFICATIONS,
    DEFAULT_NOTIFY_SERVICE,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    HYSTERESIS_KM,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


def _setting(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Read an option, falling back to initial config-entry data."""
    return entry.options.get(key, entry.data.get(key, default))


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in kilometres."""
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _altitude_m(aircraft: dict[str, Any]) -> float | None:
    """Return aircraft altitude in metres."""
    raw = aircraft.get("alt_baro")
    if raw == "ground":
        return None
    if raw in (None, ""):
        raw = aircraft.get("alt_geom")
    try:
        feet = float(raw)
    except (TypeError, ValueError):
        return None
    return feet * 0.3048


def _callsign(aircraft: dict[str, Any]) -> str:
    """Return a normalized callsign."""
    return str(aircraft.get("flight") or "").strip()


def _aircraft_id(aircraft: dict[str, Any]) -> str:
    """Return a stable identifier for the current aircraft."""
    return str(aircraft.get("hex") or _callsign(aircraft) or "").strip()


class AirRadarCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll ADS-B data and detect aircraft passages."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize AirRadar."""
        self.entry = entry
        self.session: ClientSession = async_get_clientsession(hass)
        self._active_ids: set[str] = set()
        self._initialized = False
        self._passage_listeners: set[Callable[[dict[str, Any]], None]] = set()
        self._enrichment_cache: dict[str, tuple[datetime, dict[str, str]]] = {}
        self.last_passage: dict[str, Any] | None = None
        self.last_error: str | None = None

        super().__init__(
            hass,
            logger=_LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=int(
                    _setting(entry, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
                )
            ),
        )

    @property
    def distance_limit_km(self) -> float:
        """Configured alert distance."""
        return float(_setting(self.entry, CONF_DISTANCE_KM, DEFAULT_DISTANCE_KM))

    @property
    def altitude_limit_m(self) -> int:
        """Configured alert altitude."""
        return int(_setting(self.entry, CONF_ALTITUDE_M, DEFAULT_ALTITUDE_M))

    @property
    def notifications_enabled(self) -> bool:
        """Whether direct phone notifications are enabled."""
        return bool(_setting(self.entry, CONF_NOTIFICATIONS, DEFAULT_NOTIFICATIONS))

    @property
    def notify_service(self) -> str:
        """Configured Home Assistant notify action."""
        return str(
            _setting(self.entry, CONF_NOTIFY_SERVICE, DEFAULT_NOTIFY_SERVICE)
        ).strip()

    @callback
    def async_add_passage_listener(
        self, listener: Callable[[dict[str, Any]], None]
    ) -> Callable[[], None]:
        """Subscribe to passage events."""
        self._passage_listeners.add(listener)

        @callback
        def _remove() -> None:
            self._passage_listeners.discard(listener)

        return _remove

    @callback
    def _emit_passage(self, passage: dict[str, Any]) -> None:
        """Emit a passage to event entities."""
        for listener in tuple(self._passage_listeners):
            listener(passage)

    async def _async_get_json(
        self, url: str, timeout: int = 10
    ) -> tuple[int, dict[str, Any], dict[str, str]]:
        """Fetch JSON and return status, content and headers."""
        try:
            async with asyncio.timeout(timeout):
                async with self.session.get(
                    url,
                    headers={"Accept": "application/json", "User-Agent": USER_AGENT},
                ) as response:
                    headers = dict(response.headers)
                    if response.status == 204:
                        return response.status, {}, headers
                    try:
                        content = await response.json(content_type=None)
                    except Exception as err:
                        raise UpdateFailed("Réponse JSON invalide") from err
                    if not isinstance(content, dict):
                        content = {}
                    return response.status, content, headers
        except TimeoutError as err:
            raise UpdateFailed("Délai dépassé lors de l'appel API") from err
        except ClientError as err:
            raise UpdateFailed(f"Erreur réseau: {err}") from err

    async def _async_fetch_aircraft(self) -> list[dict[str, Any]]:
        """Fetch aircraft around Home Assistant's home coordinates."""
        lat = float(self.hass.config.latitude)
        lon = float(self.hass.config.longitude)

        radius_km = self.distance_limit_km + HYSTERESIS_KM + 2.0
        radius_nm = max(1.0, min(250.0, radius_km / 1.852))

        url = ADSB_URL.format(
            lat=f"{lat:.6f}",
            lon=f"{lon:.6f}",
            radius_nm=f"{radius_nm:.1f}",
        )
        status, content, headers = await self._async_get_json(url)

        if status == 429:
            retry_after = 60.0
            try:
                retry_after = max(10.0, min(900.0, float(headers.get("Retry-After", 60))))
            except (TypeError, ValueError):
                pass
            raise UpdateFailed(
                "Limite de requêtes ADS-B atteinte",
                retry_after=retry_after,
            )

        if status != 200:
            raise UpdateFailed(f"ADSB.lol a répondu HTTP {status}")

        aircraft = content.get("ac", [])
        if not isinstance(aircraft, list):
            return []
        return [item for item in aircraft if isinstance(item, dict)]

    async def _async_enrich_callsign(self, callsign: str) -> dict[str, str]:
        """Get airline and route from ADSBDB, with a six-hour cache."""
        callsign = callsign.strip().upper()
        if not callsign:
            return {}

        now = datetime.now(timezone.utc)
        cached = self._enrichment_cache.get(callsign)
        if cached and now - cached[0] < timedelta(hours=6):
            return cached[1]

        url = ADSBDB_URL.format(callsign=quote(callsign, safe=""))

        try:
            status, content, _ = await self._async_get_json(url, timeout=8)
        except UpdateFailed:
            return {}

        result: dict[str, str] = {}
        if status == 200:
            route = content.get("response", {}).get("flightroute", {})
            if isinstance(route, dict):
                airline = route.get("airline") or {}
                origin = route.get("origin") or {}
                destination = route.get("destination") or {}

                if isinstance(airline, dict):
                    result["company"] = str(airline.get("name") or "").strip()

                if isinstance(origin, dict) and isinstance(destination, dict):
                    origin_code = str(
                        origin.get("iata_code") or origin.get("icao_code") or ""
                    ).strip()
                    destination_code = str(
                        destination.get("iata_code")
                        or destination.get("icao_code")
                        or ""
                    ).strip()
                    if origin_code and destination_code:
                        result["route"] = f"{origin_code} → {destination_code}"

        self._enrichment_cache[callsign] = (now, result)
        return result

    def _normalize_aircraft(
        self, aircraft: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Normalize ADS-B aircraft data."""
        try:
            lat = float(aircraft.get("lat"))
            lon = float(aircraft.get("lon"))
        except (TypeError, ValueError):
            return None

        altitude = _altitude_m(aircraft)
        aircraft_id = _aircraft_id(aircraft)
        if not aircraft_id:
            return None

        try:
            speed = float(aircraft.get("gs") or 0) * 1.852
        except (TypeError, ValueError):
            speed = 0.0

        try:
            heading = float(aircraft.get("track") or 0)
        except (TypeError, ValueError):
            heading = 0.0

        distance = _distance_km(
            float(self.hass.config.latitude),
            float(self.hass.config.longitude),
            lat,
            lon,
        )

        return {
            "id": aircraft_id,
            "hex": str(aircraft.get("hex") or "").strip(),
            "callsign": _callsign(aircraft) or aircraft_id,
            "company": str(aircraft.get("ownOp") or "").strip(),
            "route": "",
            "registration": str(aircraft.get("r") or "").strip(),
            "type": str(aircraft.get("t") or "").strip(),
            "model": str(aircraft.get("desc") or "").strip(),
            "distance_km": round(distance, 2),
            "altitude_m": round(altitude) if altitude is not None else None,
            "speed_kmh": round(speed),
            "heading_deg": round(heading),
            "lat": lat,
            "lon": lon,
            "on_ground": altitude is None,
        }

    async def _async_notify(self, passage: dict[str, Any]) -> None:
        """Send the direct Home Assistant phone notification."""
        if not self.notifications_enabled:
            return

        action = self.notify_service
        if not action:
            return

        if "." not in action:
            _LOGGER.warning("Action de notification invalide: %s", action)
            return

        domain, service = action.split(".", 1)
        if domain != "notify":
            _LOGGER.warning("L'action de notification doit commencer par notify.")
            return

        if not self.hass.services.has_service(domain, service):
            _LOGGER.warning("Action de notification introuvable: %s", action)
            return

        first_line = passage["callsign"]
        if passage.get("company"):
            first_line += f" — {passage['company']}"

        details: list[str] = []
        if passage.get("route"):
            details.append(passage["route"])
        details.append(f"{passage['distance_km']:.2f} km")
        if passage.get("altitude_m") is not None:
            details.append(f"{int(passage['altitude_m'])} m")
        details.append(f"{int(passage.get('speed_kmh') or 0)} km/h")

        message = f"{first_line}\n" + " · ".join(details)

        await self.hass.services.async_call(
            domain,
            service,
            {
                "title": "✈️ Avion proche de la maison",
                "message": message,
            },
            blocking=False,
        )

    async def _async_process_passage(self, plane: dict[str, Any]) -> None:
        """Enrich, store, emit and optionally notify one new passage."""
        enrichment = await self._async_enrich_callsign(plane["callsign"])

        passage = dict(plane)
        if enrichment.get("company"):
            passage["company"] = enrichment["company"]
        if enrichment.get("route"):
            passage["route"] = enrichment["route"]

        passage["detected_at"] = datetime.now(timezone.utc).isoformat()
        self.last_passage = passage

        self._emit_passage(passage)
        await self._async_notify(passage)

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll ADS-B and update all AirRadar entities."""
        raw_aircraft = await self._async_fetch_aircraft()

        planes: list[dict[str, Any]] = []
        for raw in raw_aircraft:
            plane = self._normalize_aircraft(raw)
            if plane is not None:
                planes.append(plane)

        planes.sort(key=lambda item: item["distance_km"])

        nearest: dict[str, Any] | None = planes[0] if planes else None
        if nearest and nearest.get("callsign"):
            enrichment = await self._async_enrich_callsign(nearest["callsign"])
            if enrichment.get("company"):
                nearest["company"] = enrichment["company"]
            if enrichment.get("route"):
                nearest["route"] = enrichment["route"]

        max_distance = self.distance_limit_km
        max_altitude = self.altitude_limit_m

        nearby_ids: set[str] = set()
        eligible: list[dict[str, Any]] = []

        for plane in planes:
            distance = float(plane["distance_km"])
            altitude = plane.get("altitude_m")

            if distance <= max_distance + HYSTERESIS_KM:
                nearby_ids.add(plane["id"])

            if (
                not plane["on_ground"]
                and altitude is not None
                and distance <= max_distance
                and float(altitude) <= max_altitude
            ):
                eligible.append(plane)

        if not self._initialized:
            self._active_ids = {plane["id"] for plane in eligible}
            self._initialized = True
        else:
            self._active_ids.intersection_update(nearby_ids)

            for plane in eligible:
                if plane["id"] in self._active_ids:
                    continue
                self._active_ids.add(plane["id"])
                await self._async_process_passage(plane)

        self.last_error = None
        return {
            "nearest": nearest,
            "aircraft_count": len(planes),
            "eligible": eligible,
            "alert_active": bool(eligible),
            "last_passage": self.last_passage,
            "distance_limit_km": max_distance,
            "altitude_limit_m": max_altitude,
        }
