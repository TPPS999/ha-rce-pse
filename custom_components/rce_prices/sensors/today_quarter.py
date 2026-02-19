from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from .base import RCEBaseSensor

if TYPE_CHECKING:
    from ..coordinator import RCEPSEDataUpdateCoordinator


class RCETodayQuarterPriceSensor(RCEBaseSensor):
    """Sensor exposing the RCE price for a specific 15-minute slot of today."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator, hour: int, minute: int) -> None:
        super().__init__(coordinator, f"today_price_{hour:02d}{minute:02d}")
        self._hour = hour
        self._minute = minute
        self._attr_translation_key = None
        self._attr_name = f"Today {hour:02d}:{minute:02d}"
        self._attr_native_unit_of_measurement = "PLN/MWh"
        self._attr_icon = "mdi:clock-time-eight-outline"

    @property
    def native_value(self) -> float | None:
        today_data = self.get_today_data()
        if not today_data:
            return None

        for record in today_data:
            try:
                period_end = datetime.strptime(record["dtime"], "%Y-%m-%d %H:%M:%S")
                period_start = period_end - timedelta(minutes=15)
                if period_start.hour == self._hour and period_start.minute == self._minute:
                    return round(float(record["rce_pln"]), 2)
            except (ValueError, KeyError):
                continue

        return None
