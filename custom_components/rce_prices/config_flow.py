from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_CHEAPEST_TIME_WINDOW_START,
    CONF_CHEAPEST_TIME_WINDOW_END,
    CONF_CHEAPEST_WINDOW_DURATION_HOURS,
    CONF_EXPENSIVE_TIME_WINDOW_START,
    CONF_EXPENSIVE_TIME_WINDOW_END,
    CONF_EXPENSIVE_WINDOW_DURATION_HOURS,
    CONF_USE_HOURLY_PRICES,
    CONF_PRICE_SLOT_SENSORS,
    PRICE_SLOT_SENSORS_NONE,
    PRICE_SLOT_SENSORS_HOURLY,
    PRICE_SLOT_SENSORS_QUARTER,
    CONF_GOODWE_DEVICE_ID,
    CONF_GOODWE_SELL_THRESHOLD,
    CONF_GOODWE_BUY_THRESHOLD,
    CONF_GOODWE_BUY_SWITCH,
    CONF_GOODWE_FLIP_SELL,
    CONF_GOODWE_FLIP_BUY,
    DEFAULT_TIME_WINDOW_START,
    DEFAULT_TIME_WINDOW_END,
    DEFAULT_WINDOW_DURATION_HOURS,
    DEFAULT_USE_HOURLY_PRICES,
    DEFAULT_PRICE_SLOT_SENSORS,
    DEFAULT_GOODWE_SELL_THRESHOLD,
    DEFAULT_GOODWE_BUY_THRESHOLD,
    DEFAULT_GOODWE_BUY_SWITCH,
    DEFAULT_GOODWE_FLIP_SELL,
    DEFAULT_GOODWE_FLIP_BUY,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_CHEAPEST_TIME_WINDOW_START, default=DEFAULT_TIME_WINDOW_START): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=0,
            max=23,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    ),
    vol.Required(CONF_CHEAPEST_TIME_WINDOW_END, default=DEFAULT_TIME_WINDOW_END): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1,
            max=24,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    ),
    vol.Required(CONF_CHEAPEST_WINDOW_DURATION_HOURS, default=DEFAULT_WINDOW_DURATION_HOURS): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1,
            max=24,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    ),
    vol.Required(CONF_EXPENSIVE_TIME_WINDOW_START, default=DEFAULT_TIME_WINDOW_START): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=0,
            max=23,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    ),
    vol.Required(CONF_EXPENSIVE_TIME_WINDOW_END, default=DEFAULT_TIME_WINDOW_END): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1,
            max=24,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    ),
    vol.Required(CONF_EXPENSIVE_WINDOW_DURATION_HOURS, default=DEFAULT_WINDOW_DURATION_HOURS): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1,
            max=24,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    ),
    vol.Optional(CONF_USE_HOURLY_PRICES, default=DEFAULT_USE_HOURLY_PRICES): selector.BooleanSelector(
        selector.BooleanSelectorConfig()
    ),
    vol.Optional(CONF_PRICE_SLOT_SENSORS, default=DEFAULT_PRICE_SLOT_SENSORS): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
                {"value": PRICE_SLOT_SENSORS_NONE, "label": "None (no slot sensors)"},
                {"value": PRICE_SLOT_SENSORS_HOURLY, "label": "Hourly (h00-h23, 24 per day)"},
                {"value": PRICE_SLOT_SENSORS_QUARTER, "label": "15-minute (0000-2345, 96 per day)"},
            ],
            mode=selector.SelectSelectorMode.LIST,
        )
    ),
    vol.Optional(CONF_GOODWE_DEVICE_ID, default=""): selector.TextSelector(
        selector.TextSelectorConfig()
    ),
    vol.Optional(CONF_GOODWE_SELL_THRESHOLD, default=DEFAULT_GOODWE_SELL_THRESHOLD): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=-500,
            max=5000,
            step=0.01,
            mode=selector.NumberSelectorMode.BOX,
        )
    ),
    vol.Optional(CONF_GOODWE_BUY_THRESHOLD, default=DEFAULT_GOODWE_BUY_THRESHOLD): selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=-500,
            max=5000,
            step=0.01,
            mode=selector.NumberSelectorMode.BOX,
        )
    ),
    vol.Optional(CONF_GOODWE_BUY_SWITCH, default=DEFAULT_GOODWE_BUY_SWITCH): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
                {"value": "0", "label": "0 - Disabled"},
                {"value": "1", "label": "1 - Charge battery only"},
                {"value": "2", "label": "2 - Charge + sell"},
            ],
            mode=selector.SelectSelectorMode.LIST,
        )
    ),
    vol.Optional(CONF_GOODWE_FLIP_SELL, default=DEFAULT_GOODWE_FLIP_SELL): selector.BooleanSelector(
        selector.BooleanSelectorConfig()
    ),
    vol.Optional(CONF_GOODWE_FLIP_BUY, default=DEFAULT_GOODWE_FLIP_BUY): selector.BooleanSelector(
        selector.BooleanSelectorConfig()
    ),
})


class RCEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    MINOR_VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    def async_get_options_flow(config_entry):
        return RCEOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        _LOGGER.debug("Starting RCE Prices config flow")
        
        if self._async_current_entries():
            _LOGGER.debug("RCE Prices integration already configured, aborting")
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            cheapest_start = user_input.get(CONF_CHEAPEST_TIME_WINDOW_START, DEFAULT_TIME_WINDOW_START)
            cheapest_end = user_input.get(CONF_CHEAPEST_TIME_WINDOW_END, DEFAULT_TIME_WINDOW_END)
            expensive_start = user_input.get(CONF_EXPENSIVE_TIME_WINDOW_START, DEFAULT_TIME_WINDOW_START)
            expensive_end = user_input.get(CONF_EXPENSIVE_TIME_WINDOW_END, DEFAULT_TIME_WINDOW_END)
            
            if cheapest_start >= cheapest_end:
                errors["base"] = "invalid_time_window"
            elif expensive_start >= expensive_end:
                errors["base"] = "invalid_time_window"
            else:
                _LOGGER.debug("Creating RCE Prices config entry with options: %s", user_input)
                await self.async_set_unique_id("rce_prices")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="RCE Prices", data=user_input)

        _LOGGER.debug("Showing RCE Prices configuration form")
        return self.async_show_form(
            step_id="user", 
            data_schema=CONFIG_SCHEMA,
            errors=errors
        )


class RCEOptionsFlow(config_entries.OptionsFlow):

    async def async_step_init(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        errors = {}

        if user_input is not None:
            cheapest_start = user_input.get(CONF_CHEAPEST_TIME_WINDOW_START, DEFAULT_TIME_WINDOW_START)
            cheapest_end = user_input.get(CONF_CHEAPEST_TIME_WINDOW_END, DEFAULT_TIME_WINDOW_END)
            expensive_start = user_input.get(CONF_EXPENSIVE_TIME_WINDOW_START, DEFAULT_TIME_WINDOW_START)
            expensive_end = user_input.get(CONF_EXPENSIVE_TIME_WINDOW_END, DEFAULT_TIME_WINDOW_END)
            
            if cheapest_start >= cheapest_end:
                errors["base"] = "invalid_time_window"
            elif expensive_start >= expensive_end:
                errors["base"] = "invalid_time_window"
            else:
                _LOGGER.debug("Updating RCE Prices options: %s", user_input)
                return self.async_create_entry(title="", data=user_input)

        current_data = self.config_entry.options if self.config_entry.options else self.config_entry.data
        options_schema = vol.Schema({
            vol.Required(
                CONF_CHEAPEST_TIME_WINDOW_START, 
                default=current_data.get(CONF_CHEAPEST_TIME_WINDOW_START, DEFAULT_TIME_WINDOW_START)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=23,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_CHEAPEST_TIME_WINDOW_END, 
                default=current_data.get(CONF_CHEAPEST_TIME_WINDOW_END, DEFAULT_TIME_WINDOW_END)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=24,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_CHEAPEST_WINDOW_DURATION_HOURS, 
                default=current_data.get(CONF_CHEAPEST_WINDOW_DURATION_HOURS, DEFAULT_WINDOW_DURATION_HOURS)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=24,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_EXPENSIVE_TIME_WINDOW_START, 
                default=current_data.get(CONF_EXPENSIVE_TIME_WINDOW_START, DEFAULT_TIME_WINDOW_START)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=23,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_EXPENSIVE_TIME_WINDOW_END, 
                default=current_data.get(CONF_EXPENSIVE_TIME_WINDOW_END, DEFAULT_TIME_WINDOW_END)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=24,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_EXPENSIVE_WINDOW_DURATION_HOURS, 
                default=current_data.get(CONF_EXPENSIVE_WINDOW_DURATION_HOURS, DEFAULT_WINDOW_DURATION_HOURS)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=24,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_USE_HOURLY_PRICES,
                default=current_data.get(CONF_USE_HOURLY_PRICES, DEFAULT_USE_HOURLY_PRICES)
            ): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
            vol.Optional(
                CONF_PRICE_SLOT_SENSORS,
                default=current_data.get(CONF_PRICE_SLOT_SENSORS, DEFAULT_PRICE_SLOT_SENSORS)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": PRICE_SLOT_SENSORS_NONE, "label": "None (no slot sensors)"},
                        {"value": PRICE_SLOT_SENSORS_HOURLY, "label": "Hourly (h00-h23, 24 per day)"},
                        {"value": PRICE_SLOT_SENSORS_QUARTER, "label": "15-minute (0000-2345, 96 per day)"},
                    ],
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Optional(
                CONF_GOODWE_DEVICE_ID,
                default=current_data.get(CONF_GOODWE_DEVICE_ID, "")
            ): selector.TextSelector(
                selector.TextSelectorConfig()
            ),
            vol.Optional(
                CONF_GOODWE_SELL_THRESHOLD,
                default=current_data.get(CONF_GOODWE_SELL_THRESHOLD, DEFAULT_GOODWE_SELL_THRESHOLD)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=-500,
                    max=5000,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_GOODWE_BUY_THRESHOLD,
                default=current_data.get(CONF_GOODWE_BUY_THRESHOLD, DEFAULT_GOODWE_BUY_THRESHOLD)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=-500,
                    max=5000,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(
                CONF_GOODWE_BUY_SWITCH,
                default=current_data.get(CONF_GOODWE_BUY_SWITCH, DEFAULT_GOODWE_BUY_SWITCH)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "0", "label": "0 - Disabled"},
                        {"value": "1", "label": "1 - Charge battery only"},
                        {"value": "2", "label": "2 - Charge + sell"},
                    ],
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
            vol.Optional(
                CONF_GOODWE_FLIP_SELL,
                default=current_data.get(CONF_GOODWE_FLIP_SELL, DEFAULT_GOODWE_FLIP_SELL)
            ): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
            vol.Optional(
                CONF_GOODWE_FLIP_BUY,
                default=current_data.get(CONF_GOODWE_FLIP_BUY, DEFAULT_GOODWE_FLIP_BUY)
            ): selector.BooleanSelector(
                selector.BooleanSelectorConfig()
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors
        ) 