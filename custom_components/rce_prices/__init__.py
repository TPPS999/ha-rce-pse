from __future__ import annotations

import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_GOODWE_DEVICE_ID,
    CONF_GOODWE_SELL_THRESHOLD,
    CONF_GOODWE_BUY_THRESHOLD,
    CONF_GOODWE_BUY_SWITCH,
    CONF_GOODWE_FLIP_SELL,
    CONF_GOODWE_FLIP_BUY,
    DEFAULT_GOODWE_SELL_THRESHOLD,
    DEFAULT_GOODWE_BUY_THRESHOLD,
    DEFAULT_GOODWE_BUY_SWITCH,
    DEFAULT_GOODWE_FLIP_SELL,
    DEFAULT_GOODWE_FLIP_BUY,
)
from .coordinator import RCEPSEDataUpdateCoordinator
from .price_plan import build_mask

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]

PUSH_GOODWE_SERVICE = "push_goodwe_plan"

PUSH_GOODWE_SCHEMA = vol.Schema({
    vol.Optional("sell_threshold"): vol.Coerce(float),
    vol.Optional("buy_threshold"): vol.Coerce(float),
    vol.Optional("buy_switch"): vol.In([0, 1, 2]),
})

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    _LOGGER.debug("Setting up RCE Prices integration")
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.debug("RCE Prices integration setup completed")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Setting up RCE Prices config entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})

    coordinator = RCEPSEDataUpdateCoordinator(hass, entry)
    _LOGGER.debug("Created data coordinator for RCE Prices")

    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Completed first data refresh for RCE Prices")

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("RCE Prices config entry setup completed successfully")

    async def async_push_goodwe_plan(call: ServiceCall) -> None:
        options = entry.options if entry.options else entry.data

        device_id = str(options.get(CONF_GOODWE_DEVICE_ID, "")).strip()
        if not device_id:
            raise ServiceValidationError(
                "goodwe_device_id not configured - set it in RCE Prices integration options"
            )

        if not coordinator.data or not coordinator.data.get("raw_data"):
            raise ServiceValidationError("RCE Prices coordinator has no data - wait for first refresh")

        now = dt_util.now()
        if now.hour < 14:
            raise ServiceValidationError(
                f"Tomorrow's prices not available yet (current hour: {now.hour}, available after 14:00)"
            )

        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_data = [
            r for r in coordinator.data["raw_data"]
            if r.get("business_date") == tomorrow
        ]

        if len(tomorrow_data) < 96:
            raise ServiceValidationError(
                f"Tomorrow's data incomplete: {len(tomorrow_data)} records available (need 96 - PSE may not have published yet)"
            )

        prices = [float(r["rce_pln"]) for r in tomorrow_data]

        sell_threshold = float(call.data.get(
            "sell_threshold",
            options.get(CONF_GOODWE_SELL_THRESHOLD, DEFAULT_GOODWE_SELL_THRESHOLD)
        ))
        buy_threshold = float(call.data.get(
            "buy_threshold",
            options.get(CONF_GOODWE_BUY_THRESHOLD, DEFAULT_GOODWE_BUY_THRESHOLD)
        ))
        buy_switch = int(call.data.get(
            "buy_switch",
            int(options.get(CONF_GOODWE_BUY_SWITCH, DEFAULT_GOODWE_BUY_SWITCH))
        ))
        flip_sell = bool(options.get(CONF_GOODWE_FLIP_SELL, DEFAULT_GOODWE_FLIP_SELL))
        flip_buy = bool(options.get(CONF_GOODWE_FLIP_BUY, DEFAULT_GOODWE_FLIP_BUY))

        sell_masks = build_mask(prices, sell_threshold, flip_sell, slot_minutes=15)
        buy_masks = build_mask(prices, buy_threshold, flip_buy, slot_minutes=15)

        _LOGGER.debug(
            "Pushing GoodWe plan: device=%s sell_threshold=%.2f buy_threshold=%.2f buy_switch=%d",
            device_id, sell_threshold, buy_threshold, buy_switch
        )

        await hass.services.async_call(
            "goodwe",
            "set_neg_price_plan",
            {
                "device_id": device_id,
                "sell_tomorrow_masks": sell_masks,
                "buy_tomorrow_masks": buy_masks,
                "buy_switch": buy_switch,
            },
            blocking=True,
        )

        _LOGGER.info(
            "GoodWe price plan pushed successfully: sell=%s buy=%s",
            sell_masks, buy_masks
        )

    hass.services.async_register(
        DOMAIN, PUSH_GOODWE_SERVICE, async_push_goodwe_plan, schema=PUSH_GOODWE_SCHEMA
    )
    _LOGGER.debug("Registered service %s.%s", DOMAIN, PUSH_GOODWE_SERVICE)

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    _LOGGER.debug("Options updated for RCE Prices, reloading entry: %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Unloading RCE Prices config entry: %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()
        hass.services.async_remove(DOMAIN, PUSH_GOODWE_SERVICE)
        _LOGGER.debug("RCE Prices config entry unloaded successfully")
    else:
        _LOGGER.warning("Failed to unload RCE Prices config entry: %s", entry.entry_id)

    return unload_ok
