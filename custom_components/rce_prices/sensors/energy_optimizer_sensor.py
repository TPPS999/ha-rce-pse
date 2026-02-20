from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.util import dt as dt_util

from .base import RCEBaseSensor
from ..const import (
    CONF_MAX_GRID_POWER_KW,
    CONF_MAX_CHARGING_POWER_KW,
    CONF_REQUIRED_DAILY_ENERGY_KWH,
    CONF_BATTERY_CAPACITY_KWH,
    CONF_PV_FORECAST_ENTITY,
    CONF_CONSUMPTION_ENTITY,
    CONF_SOC_ENTITY,
    DEFAULT_MAX_GRID_POWER_KW,
    DEFAULT_MAX_CHARGING_POWER_KW,
    DEFAULT_REQUIRED_DAILY_ENERGY_KWH,
    DEFAULT_BATTERY_CAPACITY_KWH,
    PV_START_HOUR,
    PV_END_HOUR,
)
from ..energy_optimizer import calculate_optimal_buy_threshold

if TYPE_CHECKING:
    from ..coordinator import RCEPSEDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class RCEOptimalBuyThresholdSensor(RCEBaseSensor):
    """Sensor exposing the optimal buy price threshold for battery charging."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(coordinator, "optimal_buy_threshold")
        self._config_entry = config_entry
        self._attr_translation_key = None
        self._attr_name = "Optimal Buy Threshold"
        self._attr_native_unit_of_measurement = "PLN/MWh"
        self._attr_icon = "mdi:battery-charging"
        self._last_meta: dict = {}

    def _read_entity_float(self, entity_id: str, fallback: float) -> float:
        if not entity_id:
            return fallback
        state = self.hass.states.get(entity_id)
        if not state or state.state in ("unknown", "unavailable"):
            return fallback
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return fallback

    def _get_price_slots(self) -> list[tuple[datetime, float]]:
        if not self.coordinator.data or not self.coordinator.data.get("raw_data"):
            return []

        now = dt_util.now()
        tomorrow = (now + timedelta(days=1)).date()
        tomorrow_end = datetime.combine(tomorrow, datetime.max.time())
        now_naive = now.replace(tzinfo=None)

        slots: list[tuple[datetime, float]] = []
        for record in self.coordinator.data["raw_data"]:
            try:
                period_end = datetime.strptime(record["dtime"], "%Y-%m-%d %H:%M:%S")
                period_start = period_end - timedelta(minutes=15)
                if period_start < now_naive:
                    continue
                if period_start > tomorrow_end:
                    continue
                slots.append((period_start, float(record["rce_pln"])))
            except (ValueError, KeyError):
                continue
        return slots

    @property
    def native_value(self) -> float | None:
        options = self._config_entry.options if self._config_entry.options else self._config_entry.data

        battery_capacity_kwh = float(options.get(CONF_BATTERY_CAPACITY_KWH, DEFAULT_BATTERY_CAPACITY_KWH))
        max_grid_power_kw = float(options.get(CONF_MAX_GRID_POWER_KW, DEFAULT_MAX_GRID_POWER_KW))
        max_charging_power_kw = float(options.get(CONF_MAX_CHARGING_POWER_KW, DEFAULT_MAX_CHARGING_POWER_KW))
        required_daily_energy_kwh = float(options.get(CONF_REQUIRED_DAILY_ENERGY_KWH, DEFAULT_REQUIRED_DAILY_ENERGY_KWH))

        pv_forecast_entity = str(options.get(CONF_PV_FORECAST_ENTITY, "")).strip()
        consumption_entity = str(options.get(CONF_CONSUMPTION_ENTITY, "")).strip()
        soc_entity = str(options.get(CONF_SOC_ENTITY, "")).strip()

        soc_pct = self._read_entity_float(soc_entity, 0.0)
        battery_energy_kwh = soc_pct / 100.0 * battery_capacity_kwh

        daily_consumption_kwh = self._read_entity_float(consumption_entity, required_daily_energy_kwh)
        pv_forecast_kwh = self._read_entity_float(pv_forecast_entity, 0.0)

        energy_to_buy_kwh = daily_consumption_kwh - pv_forecast_kwh - battery_energy_kwh

        max_energy_before_pv_kwh = battery_capacity_kwh - min(pv_forecast_kwh, battery_capacity_kwh)

        max_per_slot_kwh = min(max_charging_power_kw, max_grid_power_kw) * 0.25

        price_slots = self._get_price_slots()

        threshold, meta = calculate_optimal_buy_threshold(
            price_slots=price_slots,
            energy_to_buy_kwh=energy_to_buy_kwh,
            max_per_slot_kwh=max_per_slot_kwh,
            max_energy_before_pv_kwh=max_energy_before_pv_kwh,
            pv_forecast_kwh=pv_forecast_kwh,
            pv_start_hour=PV_START_HOUR,
            pv_end_hour=PV_END_HOUR,
        )

        self._last_meta = {
            **meta,
            "battery_energy_kwh": round(battery_energy_kwh, 3),
            "pv_forecast_kwh": round(pv_forecast_kwh, 3),
            "daily_consumption_kwh": round(daily_consumption_kwh, 3),
            "soc_pct": round(soc_pct, 1),
            "max_energy_before_pv_kwh": round(max_energy_before_pv_kwh, 3),
            "max_per_slot_kwh": round(max_per_slot_kwh, 4),
        }

        _LOGGER.debug(
            "Optimal buy threshold calculated: %.2f PLN/MWh (status=%s, slots=%d/%d)",
            threshold if threshold is not None else 0.0,
            meta.get("status"),
            meta.get("slots_allocated", 0),
            meta.get("eligible_slots_count", 0),
        )

        return round(threshold, 2) if threshold is not None else None

    @property
    def extra_state_attributes(self) -> dict:
        return self._last_meta
