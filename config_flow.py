"""Config flow for Cambridge Audio Infrared integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import infrared
from homeassistant.helpers import selector

from .const import (
    CONF_INFRARED_ENTITY_ID,
    CONF_MODEL,
    DOMAIN,
    SUPPORTED_MODELS,
)


class CambridgeAudioIRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cambridge Audio Infrared."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step: choose model + IR emitter."""
        errors: dict[str, str] = {}

        # Collect all available IR emitters already configured in HA
        emitters = infrared.async_get_emitters(self.hass)

        if not emitters:
            return self.async_abort(reason="no_emitters")

        emitter_options = [
            selector.SelectOptionDict(value=e.entity_id, label=e.name)
            for e in emitters
        ]

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_MODEL]}_{user_input[CONF_INFRARED_ENTITY_ID]}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Cambridge Audio {user_input[CONF_MODEL]}",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_MODEL): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=SUPPORTED_MODELS,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                vol.Required(CONF_INFRARED_ENTITY_ID): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=emitter_options,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
