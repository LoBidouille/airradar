"""Config flow for AirRadar."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlowWithReload
from homeassistant.core import callback

from .const import (
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
    MAX_ALTITUDE_M,
    MAX_DISTANCE_KM,
    MAX_POLL_INTERVAL,
    MIN_ALTITUDE_M,
    MIN_DISTANCE_KM,
    MIN_POLL_INTERVAL,
)


def _schema(values: dict[str, Any] | None = None) -> vol.Schema:
    """Build the configuration schema."""
    values = values or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_DISTANCE_KM,
                default=values.get(CONF_DISTANCE_KM, DEFAULT_DISTANCE_KM),
            ): vol.All(vol.Coerce(float), vol.Range(min=MIN_DISTANCE_KM, max=MAX_DISTANCE_KM)),
            vol.Required(
                CONF_ALTITUDE_M,
                default=values.get(CONF_ALTITUDE_M, DEFAULT_ALTITUDE_M),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_ALTITUDE_M, max=MAX_ALTITUDE_M)),
            vol.Required(
                CONF_POLL_INTERVAL,
                default=values.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL)),
            vol.Required(
                CONF_NOTIFICATIONS,
                default=values.get(CONF_NOTIFICATIONS, DEFAULT_NOTIFICATIONS),
            ): bool,
            vol.Optional(
                CONF_NOTIFY_SERVICE,
                default=values.get(CONF_NOTIFY_SERVICE, DEFAULT_NOTIFY_SERVICE),
            ): str,
        }
    )


class AirRadarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an AirRadar config flow."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            notify_service = user_input.get(CONF_NOTIFY_SERVICE, "").strip()
            user_input[CONF_NOTIFY_SERVICE] = notify_service

            if notify_service and (
                "." not in notify_service
                or not notify_service.startswith("notify.")
            ):
                errors[CONF_NOTIFY_SERVICE] = "invalid_notify_service"

            if not errors:
                await self.async_set_unique_id("airradar_home")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="AirRadar", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AirRadarOptionsFlow:
        """Return the options flow."""
        return AirRadarOptionsFlow()


class AirRadarOptionsFlow(OptionsFlowWithReload):
    """Handle AirRadar options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage AirRadar options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            notify_service = user_input.get(CONF_NOTIFY_SERVICE, "").strip()
            user_input[CONF_NOTIFY_SERVICE] = notify_service

            if notify_service and (
                "." not in notify_service
                or not notify_service.startswith("notify.")
            ):
                errors[CONF_NOTIFY_SERVICE] = "invalid_notify_service"

            if not errors:
                return self.async_create_entry(data=user_input)

        current = {
            **self.config_entry.data,
            **self.config_entry.options,
        }
        if user_input is not None:
            current.update(user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
            errors=errors,
        )
