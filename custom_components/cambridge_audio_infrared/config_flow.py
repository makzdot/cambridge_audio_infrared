"""Config flow for Cambridge Audio Infrared integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import infrared
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_CXN_SYSTEM_CODE,
    CONF_INFRARED_ENTITY_ID,
    CONF_INFRARED_RECEIVER_ENTITY_ID,
    CONF_MODEL,
    CXN_SYSTEM_CODE_DEFAULT,
    CXN_SYSTEM_CODES,
    DOMAIN,
    MODEL_CXN100,
    SUPPORTED_MODELS,
)


def _entity_options(hass, entity_ids: list[str]) -> list[selector.SelectOptionDict]:
    """Build select options from entity_id strings with friendly-name labels."""
    options = []
    for entity_id in entity_ids:
        state = hass.states.get(entity_id)
        label = state.name if state else entity_id
        options.append(selector.SelectOptionDict(value=entity_id, label=label))
    return options


class CambridgeAudioIRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Cambridge Audio Infrared."""

    VERSION = 1

    # Carries step_user input forward to async_step_cxn for the CXN flow.
    # Annotation-only: set per-instance in async_step_user before use.
    _pending: dict[str, Any]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: choose model + IR emitter."""
        errors: dict[str, str] = {}

        # Collect available IR emitters and receivers already configured in HA
        emitters = infrared.async_get_emitters(self.hass)
        receivers = infrared.async_get_receivers(self.hass)

        if not emitters:
            return self.async_abort(reason="no_emitters")

        emitter_options = _entity_options(self.hass, emitters)
        receiver_options = _entity_options(self.hass, receivers)

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_MODEL]}_{user_input[CONF_INFRARED_ENTITY_ID]}"
            )
            self._abort_if_unique_id_configured()

            # The CXN exposes a switchable base system code; collect it next.
            if user_input[CONF_MODEL] == MODEL_CXN100:
                self._pending = user_input
                return await self.async_step_cxn()

            return self.async_create_entry(
                title=f"Cambridge Audio {user_input[CONF_MODEL]}",
                data=user_input,
            )

        schema_fields: dict = {
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
        # Receiver is optional: it enables remote-press events but is not
        # needed to control the amplifier.
        if receiver_options:
            schema_fields[vol.Optional(CONF_INFRARED_RECEIVER_ENTITY_ID)] = (
                selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=receiver_options,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                )
            )
        schema = vol.Schema(schema_fields)

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_cxn(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose the CXN's base RC-5 system code (24 or 28)."""
        if user_input is not None:
            data = {
                **self._pending,
                CONF_CXN_SYSTEM_CODE: int(user_input[CONF_CXN_SYSTEM_CODE]),
            }
            return self.async_create_entry(
                title=f"Cambridge Audio {data[CONF_MODEL]}",
                data=data,
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_CXN_SYSTEM_CODE, default=str(CXN_SYSTEM_CODE_DEFAULT)
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[str(code) for code in CXN_SYSTEM_CODES],
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="cxn", data_schema=schema)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the emitter, attach/change a receiver, or the CXN system code."""
        entry = self._get_reconfigure_entry()
        model = entry.data[CONF_MODEL]

        emitters = infrared.async_get_emitters(self.hass)
        receivers = infrared.async_get_receivers(self.hass)
        if not emitters:
            return self.async_abort(reason="no_emitters")

        if user_input is not None:
            # Build the data explicitly so deselecting the receiver removes it.
            data: dict[str, Any] = {
                CONF_MODEL: model,
                CONF_INFRARED_ENTITY_ID: user_input[CONF_INFRARED_ENTITY_ID],
            }
            if user_input.get(CONF_INFRARED_RECEIVER_ENTITY_ID):
                data[CONF_INFRARED_RECEIVER_ENTITY_ID] = user_input[
                    CONF_INFRARED_RECEIVER_ENTITY_ID
                ]
            if model == MODEL_CXN100:
                data[CONF_CXN_SYSTEM_CODE] = int(user_input[CONF_CXN_SYSTEM_CODE])
            return self.async_update_reload_and_abort(entry, data=data)

        emitter_options = _entity_options(self.hass, emitters)
        receiver_options = _entity_options(self.hass, receivers)

        fields: dict = {
            vol.Required(
                CONF_INFRARED_ENTITY_ID,
                default=entry.data.get(CONF_INFRARED_ENTITY_ID),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=emitter_options,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        }
        if receiver_options:
            current_receiver = entry.data.get(CONF_INFRARED_RECEIVER_ENTITY_ID)
            receiver_key = (
                vol.Optional(CONF_INFRARED_RECEIVER_ENTITY_ID, default=current_receiver)
                if current_receiver
                else vol.Optional(CONF_INFRARED_RECEIVER_ENTITY_ID)
            )
            fields[receiver_key] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=receiver_options,
                    mode=selector.SelectSelectorMode.LIST,
                )
            )
        if model == MODEL_CXN100:
            fields[
                vol.Required(
                    CONF_CXN_SYSTEM_CODE,
                    default=str(
                        entry.data.get(CONF_CXN_SYSTEM_CODE, CXN_SYSTEM_CODE_DEFAULT)
                    ),
                )
            ] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(code) for code in CXN_SYSTEM_CODES],
                    mode=selector.SelectSelectorMode.LIST,
                )
            )

        return self.async_show_form(
            step_id="reconfigure", data_schema=vol.Schema(fields)
        )
