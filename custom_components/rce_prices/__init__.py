from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .coordinator import RCEPSEDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]

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
        _LOGGER.debug("RCE Prices config entry unloaded successfully")
    else:
        _LOGGER.warning("Failed to unload RCE Prices config entry: %s", entry.entry_id)
    
    return unload_ok 