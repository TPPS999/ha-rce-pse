from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_PRICE_SLOT_SENSORS,
    DEFAULT_PRICE_SLOT_SENSORS,
    PRICE_SLOT_SENSORS_HOURLY,
    PRICE_SLOT_SENSORS_QUARTER,
)
from .sensors import (
    RCETodayHourPriceSensor,
    RCETomorrowHourPriceSensor,
    RCETodayQuarterPriceSensor,
    RCETomorrowQuarterPriceSensor,
    RCEOptimalBuyThresholdSensor,
    RCETodayMainSensor,
    RCETodayKwhPriceSensor,
    RCENextHourPriceSensor,
    RCENext2HoursPriceSensor,
    RCENext3HoursPriceSensor,
    RCEPreviousHourPriceSensor,
    RCETodayAvgPriceSensor,
    RCETodayMaxPriceSensor,
    RCETodayMinPriceSensor,
    RCETodayMaxPriceHourStartSensor,
    RCETodayMaxPriceHourEndSensor,
    RCETodayMinPriceHourStartSensor,
    RCETodayMinPriceHourEndSensor,
    RCETodayMaxPriceHourStartTimestampSensor,
    RCETodayMaxPriceHourEndTimestampSensor,
    RCETodayMinPriceHourStartTimestampSensor,
    RCETodayMinPriceHourEndTimestampSensor,
    RCETodayMinPriceRangeSensor,
    RCETodayMaxPriceRangeSensor,
    RCETodayMedianPriceSensor,
    RCETodayCurrentVsAverageSensor,
    RCETodayMorningBestPriceSensor,
    RCETodayMorningSecondBestPriceSensor,
    RCETodayMorningBestPriceStartTimestampSensor,
    RCETodayMorningSecondBestPriceStartTimestampSensor,
    RCETodayEveningBestPriceSensor,
    RCETodayEveningSecondBestPriceSensor,
    RCETodayEveningBestPriceStartTimestampSensor,
    RCETodayEveningSecondBestPriceStartTimestampSensor,
    RCETomorrowMainSensor,
    RCETomorrowAvgPriceSensor,
    RCETomorrowMaxPriceSensor,
    RCETomorrowMinPriceSensor,
    RCETomorrowMaxPriceHourStartSensor,
    RCETomorrowMaxPriceHourEndSensor,
    RCETomorrowMinPriceHourStartSensor,
    RCETomorrowMinPriceHourEndSensor,
    RCETomorrowMaxPriceHourStartTimestampSensor,
    RCETomorrowMaxPriceHourEndTimestampSensor,
    RCETomorrowMinPriceHourStartTimestampSensor,
    RCETomorrowMinPriceHourEndTimestampSensor,
    RCETomorrowMinPriceRangeSensor,
    RCETomorrowMaxPriceRangeSensor,
    RCETomorrowMedianPriceSensor,
    RCETomorrowTodayAvgComparisonSensor,
)
from .sensors.custom_windows import (
    RCETodayCheapestWindowStartSensor,
    RCETodayCheapestWindowEndSensor,
    RCETodayCheapestWindowRangeSensor,
    RCETodayExpensiveWindowStartSensor,
    RCETodayExpensiveWindowEndSensor,
    RCETodayExpensiveWindowRangeSensor,
    RCETomorrowCheapestWindowStartSensor,
    RCETomorrowCheapestWindowEndSensor,
    RCETomorrowCheapestWindowRangeSensor,
    RCETomorrowExpensiveWindowStartSensor,
    RCETomorrowExpensiveWindowEndSensor,
    RCETomorrowExpensiveWindowRangeSensor,
    RCETodayCheapestWindowStartTimestampSensor,
    RCETodayCheapestWindowEndTimestampSensor,
    RCETodayExpensiveWindowStartTimestampSensor,
    RCETodayExpensiveWindowEndTimestampSensor,
    RCETomorrowCheapestWindowStartTimestampSensor,
    RCETomorrowCheapestWindowEndTimestampSensor,
    RCETomorrowExpensiveWindowStartTimestampSensor,
    RCETomorrowExpensiveWindowEndTimestampSensor,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Setting up RCE Prices sensors for config entry: %s", config_entry.entry_id)
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    sensors = [
        RCETodayMainSensor(coordinator),
        RCETodayKwhPriceSensor(coordinator),
        RCENextHourPriceSensor(coordinator),
        RCENext2HoursPriceSensor(coordinator),
        RCENext3HoursPriceSensor(coordinator),
        RCEPreviousHourPriceSensor(coordinator),
        RCETodayAvgPriceSensor(coordinator),
        RCETodayMaxPriceSensor(coordinator),
        RCETodayMinPriceSensor(coordinator),
        RCETodayMaxPriceHourStartSensor(coordinator),
        RCETodayMaxPriceHourEndSensor(coordinator),
        RCETodayMinPriceHourStartSensor(coordinator),
        RCETodayMinPriceHourEndSensor(coordinator),
        RCETodayMaxPriceHourStartTimestampSensor(coordinator),
        RCETodayMaxPriceHourEndTimestampSensor(coordinator),
        RCETodayMinPriceHourStartTimestampSensor(coordinator),
        RCETodayMinPriceHourEndTimestampSensor(coordinator),
        RCETodayMinPriceRangeSensor(coordinator),
        RCETodayMaxPriceRangeSensor(coordinator),
        RCETodayMedianPriceSensor(coordinator),
        RCETodayCurrentVsAverageSensor(coordinator),
        RCETodayMorningBestPriceSensor(coordinator),
        RCETodayMorningSecondBestPriceSensor(coordinator),
        RCETodayMorningBestPriceStartTimestampSensor(coordinator),
        RCETodayMorningSecondBestPriceStartTimestampSensor(coordinator),
        RCETodayEveningBestPriceSensor(coordinator),
        RCETodayEveningSecondBestPriceSensor(coordinator),
        RCETodayEveningBestPriceStartTimestampSensor(coordinator),
        RCETodayEveningSecondBestPriceStartTimestampSensor(coordinator),
        RCETomorrowMainSensor(coordinator),
        RCETomorrowAvgPriceSensor(coordinator),
        RCETomorrowMaxPriceSensor(coordinator),
        RCETomorrowMinPriceSensor(coordinator),
        RCETomorrowMaxPriceHourStartSensor(coordinator),
        RCETomorrowMaxPriceHourEndSensor(coordinator),
        RCETomorrowMinPriceHourStartSensor(coordinator),
        RCETomorrowMinPriceHourEndSensor(coordinator),
        RCETomorrowMaxPriceHourStartTimestampSensor(coordinator),
        RCETomorrowMaxPriceHourEndTimestampSensor(coordinator),
        RCETomorrowMinPriceHourStartTimestampSensor(coordinator),
        RCETomorrowMinPriceHourEndTimestampSensor(coordinator),
        RCETomorrowMinPriceRangeSensor(coordinator),
        RCETomorrowMaxPriceRangeSensor(coordinator),
        RCETomorrowMedianPriceSensor(coordinator),
        RCETomorrowTodayAvgComparisonSensor(coordinator),
        RCETodayCheapestWindowStartSensor(coordinator, config_entry),
        RCETodayCheapestWindowEndSensor(coordinator, config_entry),
        RCETodayCheapestWindowRangeSensor(coordinator, config_entry),
        RCETodayExpensiveWindowStartSensor(coordinator, config_entry),
        RCETodayExpensiveWindowEndSensor(coordinator, config_entry),
        RCETodayExpensiveWindowRangeSensor(coordinator, config_entry),
        RCETomorrowCheapestWindowStartSensor(coordinator, config_entry),
        RCETomorrowCheapestWindowEndSensor(coordinator, config_entry),
        RCETomorrowCheapestWindowRangeSensor(coordinator, config_entry),
        RCETomorrowExpensiveWindowStartSensor(coordinator, config_entry),
        RCETomorrowExpensiveWindowEndSensor(coordinator, config_entry),
        RCETomorrowExpensiveWindowRangeSensor(coordinator, config_entry),
        RCETodayCheapestWindowStartTimestampSensor(coordinator, config_entry),
        RCETodayCheapestWindowEndTimestampSensor(coordinator, config_entry),
        RCETodayExpensiveWindowStartTimestampSensor(coordinator, config_entry),
        RCETodayExpensiveWindowEndTimestampSensor(coordinator, config_entry),
        RCETomorrowCheapestWindowStartTimestampSensor(coordinator, config_entry),
        RCETomorrowCheapestWindowEndTimestampSensor(coordinator, config_entry),
        RCETomorrowExpensiveWindowStartTimestampSensor(coordinator, config_entry),
        RCETomorrowExpensiveWindowEndTimestampSensor(coordinator, config_entry),
    ]

    sensors.append(RCEOptimalBuyThresholdSensor(coordinator, config_entry))

    options = config_entry.options if config_entry.options else config_entry.data
    slot_mode = options.get(CONF_PRICE_SLOT_SENSORS, DEFAULT_PRICE_SLOT_SENSORS)

    if slot_mode == PRICE_SLOT_SENSORS_HOURLY:
        _LOGGER.debug("Price slot sensors mode: hourly - adding 48 sensors (24 today + 24 tomorrow)")
        for hour in range(24):
            sensors.append(RCETodayHourPriceSensor(coordinator, hour))
            sensors.append(RCETomorrowHourPriceSensor(coordinator, hour))
    elif slot_mode == PRICE_SLOT_SENSORS_QUARTER:
        _LOGGER.debug("Price slot sensors mode: quarter_hourly - adding 192 sensors (96 today + 96 tomorrow)")
        for hour in range(24):
            for minute in (0, 15, 30, 45):
                sensors.append(RCETodayQuarterPriceSensor(coordinator, hour, minute))
                sensors.append(RCETomorrowQuarterPriceSensor(coordinator, hour, minute))
    else:
        _LOGGER.debug("Price slot sensors mode: none - skipping slot sensors")

    _LOGGER.debug("Adding %d RCE Prices sensors to Home Assistant", len(sensors))
    async_add_entities(sensors)
    _LOGGER.debug("RCE Prices sensors setup completed successfully") 