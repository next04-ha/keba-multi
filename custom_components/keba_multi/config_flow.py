import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import callback

from .const import CONF_RFID, CONF_HOST, CONF_FS_INTERVAL, DEFAULT_FS_INTERVAL

_LOGGER = logging.getLogger(__name__)

class KebaMultiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        _LOGGER.debug("Starting config flow for KEBA multi (user input: %s)", user_input)

        errors = {}

        # Step 1: Handle the user input
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            _LOGGER.debug("Attempting to configure KEBA at %s", host)

            # Ensure unique ID per host (so you can add more than one)
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            # Step 2: Create the configuration entry for the KEBA charging station
            return self.async_create_entry(
                title=f"KEBA {host}",
                data={
                    CONF_HOST: host,
                    CONF_RFID: user_input.get(CONF_RFID, "00845500"),
                    CONF_FS_INTERVAL: int(user_input.get(CONF_FS_INTERVAL, DEFAULT_FS_INTERVAL)),
                },
            )

        # Step 3: Display the user input form
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_RFID, default="00845500"): str,
                vol.Optional(CONF_FS_INTERVAL, default=DEFAULT_FS_INTERVAL): vol.Coerce(int),
            }
        )

        _LOGGER.debug("Displaying configuration form for user input")
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        # Ensure the handler is valid
        _LOGGER.debug("Returning options flow for KEBA")
        return KebaMultiOptionsFlow(config_entry)


class KebaMultiOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        # Log to verify when this is being called
        _LOGGER.debug("Initializing options flow for KEBA multi (entry: %s)", config_entry)
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            _LOGGER.debug("Updating options for KEBA at %s", self._config_entry.data.get(CONF_HOST))
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_FS_INTERVAL,
                        default=self._config_entry.data.get(CONF_FS_INTERVAL, DEFAULT_FS_INTERVAL),
                    ): vol.Coerce(int)
                }
            ),
        )

