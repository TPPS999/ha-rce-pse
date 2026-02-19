from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from .base import RCEBaseSensor

if TYPE_CHECKING:
    from ..coordinator import RCEPSEDataUpdateCoordinator


class RCETomorrowHourPriceSensor(RCEBaseSensor):
    """Sensor exposing the average RCE price for a specific hour of tomorrow."""

    def __init__(self, coordinator: RCEPSEDataUpdateCoordinator, hour: int) -> None:
        super().__init__(coordinator, f"tomorrow_price_h{hour:02d}")
        self._hour = hour
        self._attr_translation_key = None
        self._attr_name = f"Tomorrow H{hour:02d}"
        self._attr_native_unit_of_measurement = "PLN/MWh"
        self._attr_icon = "mdi:clock-time-eight-outline"

    @property
    def available(self) -> bool:
        return super().available and self.is_tomorrow_data_available()

    @property
    def native_value(self) -> float | None:
        tomorrow_data = self.get_tomorrow_data()
        if not tomorrow_data:
            return None

        prices = []
        for record in tomorrow_data:
            try:
                period_end = datetime.strptime(record["dtime"], "%Y-%m-%d %H:%M:%S")
                period_start = period_end - timedelta(minutes=15)
                if period_start.hour == self._hour:
                    prices.append(float(record["rce_pln"]))
            except (ValueError, KeyError):
                continue

        if not prices:
            return None

        return round(sum(prices) / len(prices), 2)
