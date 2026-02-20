from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final[str] = "rce_prices"
SENSOR_PREFIX: Final[str] = "RCE Prices"
MANUFACTURER: Final[str] = "plebann"
PSE_API_URL: Final[str] = "https://api.raporty.pse.pl/api/rce-pln"
API_UPDATE_INTERVAL: Final[timedelta] = timedelta(minutes=30)
API_SELECT: Final[str] = "dtime,period,rce_pln,business_date,publication_ts"
API_FIRST: Final[int] = 200

TAX_RATE: Final[float] = 0.23

CONF_CHEAPEST_TIME_WINDOW_START: Final[str] = "cheapest_time_window_start"
CONF_CHEAPEST_TIME_WINDOW_END: Final[str] = "cheapest_time_window_end"
CONF_CHEAPEST_WINDOW_DURATION_HOURS: Final[str] = "cheapest_window_duration_hours"

CONF_EXPENSIVE_TIME_WINDOW_START: Final[str] = "expensive_time_window_start"
CONF_EXPENSIVE_TIME_WINDOW_END: Final[str] = "expensive_time_window_end"
CONF_EXPENSIVE_WINDOW_DURATION_HOURS: Final[str] = "expensive_window_duration_hours"

CONF_WINDOW_DURATION_HOURS: Final[str] = "window_duration_hours"
CONF_USE_HOURLY_PRICES: Final[str] = "use_hourly_prices"
CONF_PRICE_SLOT_SENSORS: Final[str] = "price_slot_sensors"

PRICE_SLOT_SENSORS_NONE: Final[str] = "none"
PRICE_SLOT_SENSORS_HOURLY: Final[str] = "hourly"
PRICE_SLOT_SENSORS_QUARTER: Final[str] = "quarter_hourly"

DEFAULT_TIME_WINDOW_START: Final[int] = 0
DEFAULT_TIME_WINDOW_END: Final[int] = 24
DEFAULT_WINDOW_DURATION_HOURS: Final[int] = 2
DEFAULT_USE_HOURLY_PRICES: Final[bool] = False
DEFAULT_PRICE_SLOT_SENSORS: Final[str] = PRICE_SLOT_SENSORS_NONE

MORNING_BEST_WINDOW_START_HOUR: Final[int] = 7
MORNING_BEST_WINDOW_END_HOUR: Final[int] = 9
EVENING_BEST_WINDOW_START_HOUR: Final[int] = 17
EVENING_BEST_WINDOW_END_HOUR: Final[int] = 21
BEST_WINDOW_DURATION_HOURS: Final[int] = 1

CONF_GOODWE_DEVICE_ID: Final[str] = "goodwe_device_id"
CONF_GOODWE_SELL_THRESHOLD: Final[str] = "goodwe_sell_threshold"
CONF_GOODWE_BUY_THRESHOLD: Final[str] = "goodwe_buy_threshold"
CONF_GOODWE_BUY_SWITCH: Final[str] = "goodwe_buy_switch"
CONF_GOODWE_FLIP_SELL: Final[str] = "goodwe_flip_sell"
CONF_GOODWE_FLIP_BUY: Final[str] = "goodwe_flip_buy"

DEFAULT_GOODWE_SELL_THRESHOLD: Final[float] = 0.0
DEFAULT_GOODWE_BUY_THRESHOLD: Final[float] = 0.0
DEFAULT_GOODWE_BUY_SWITCH: Final[str] = "1"
DEFAULT_GOODWE_FLIP_SELL: Final[bool] = False
DEFAULT_GOODWE_FLIP_BUY: Final[bool] = False

CONF_MAX_GRID_POWER_KW: Final[str] = "max_grid_power_kw"
CONF_MAX_CHARGING_POWER_KW: Final[str] = "max_charging_power_kw"
CONF_REQUIRED_DAILY_ENERGY_KWH: Final[str] = "required_daily_energy_kwh"
CONF_BATTERY_CAPACITY_KWH: Final[str] = "battery_capacity_kwh"
CONF_PV_FORECAST_ENTITY: Final[str] = "pv_forecast_entity"
CONF_CONSUMPTION_ENTITY: Final[str] = "consumption_entity"
CONF_SOC_ENTITY: Final[str] = "soc_entity"

DEFAULT_MAX_GRID_POWER_KW: Final[float] = 11.0
DEFAULT_MAX_CHARGING_POWER_KW: Final[float] = 5.0
DEFAULT_REQUIRED_DAILY_ENERGY_KWH: Final[float] = 10.0
DEFAULT_BATTERY_CAPACITY_KWH: Final[float] = 10.0
PV_START_HOUR: Final[int] = 7
PV_END_HOUR: Final[int] = 19