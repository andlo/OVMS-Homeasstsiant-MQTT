import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


@callback
def configured_instances(hass):
    return [entry.title for entry in hass.config_entries.async_entries(DOMAIN)]


class OVMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="OVMS", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("broker"): str,
                    vol.Required("port", default=1883): int,
                    vol.Optional("username"): str,
                    vol.Optional("password"): str,
                }
            ),
            errors=errors,
        )
