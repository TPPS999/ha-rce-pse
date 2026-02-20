from __future__ import annotations

from datetime import datetime


def calculate_optimal_buy_threshold(
    price_slots: list[tuple[datetime, float]],
    energy_to_buy_kwh: float,
    max_per_slot_kwh: float,
    max_energy_before_pv_kwh: float,
    pv_forecast_kwh: float,
    pv_start_hour: int = 7,
    pv_end_hour: int = 19,
) -> tuple[float | None, dict]:
    """Calculate the marginal buy price threshold for battery charging.

    Uses a greedy algorithm to find the cheapest slots that satisfy energy demand.
    Skips PV hours (pv_start_hour..pv_end_hour on tomorrow) when PV is expected.
    Caps pre-PV energy to leave room for PV absorption.

    Args:
        price_slots: List of (slot_start_datetime, price_PLN_per_MWh) for future slots.
                     Must be naive datetimes (no timezone). Slots are 15-min each.
        energy_to_buy_kwh: Net energy needed from grid (already accounting for SoC and PV).
        max_per_slot_kwh: Max energy chargeable per 15-min slot (kWh).
        max_energy_before_pv_kwh: Max energy allowed to charge before PV starts.
        pv_forecast_kwh: Expected PV production tomorrow (kWh).
        pv_start_hour: Hour when PV starts producing (default 7).
        pv_end_hour: Hour when PV stops producing (default 19).

    Returns:
        Tuple of (threshold_price_or_None, metadata_dict).
        threshold_price is None when no purchase is needed or data is insufficient.
    """
    if energy_to_buy_kwh <= 0:
        return None, {
            "status": "no_purchase_needed",
            "energy_to_buy_kwh": energy_to_buy_kwh,
            "eligible_slots_count": 0,
            "slots_allocated": 0,
            "threshold_price": None,
        }

    if not price_slots:
        return None, {
            "status": "insufficient_data",
            "energy_to_buy_kwh": energy_to_buy_kwh,
            "eligible_slots_count": 0,
            "slots_allocated": 0,
            "threshold_price": None,
        }

    tomorrow = (min(s[0] for s in price_slots).date())
    # Determine tomorrow: the date after the earliest slot's date
    dates = sorted({s[0].date() for s in price_slots})
    tomorrow_date = dates[-1] if len(dates) >= 2 else None

    pre_pv_slots: list[tuple[datetime, float]] = []
    post_pv_slots: list[tuple[datetime, float]] = []

    for slot_start, price in price_slots:
        is_tomorrow = (tomorrow_date is not None and slot_start.date() == tomorrow_date)

        if is_tomorrow and pv_forecast_kwh > 0 and pv_start_hour <= slot_start.hour < pv_end_hour:
            # PV production window - skip
            continue
        elif is_tomorrow and slot_start.hour >= pv_end_hour:
            post_pv_slots.append((slot_start, price))
        else:
            pre_pv_slots.append((slot_start, price))

    eligible_slots = sorted(pre_pv_slots + post_pv_slots, key=lambda x: x[1])

    if not eligible_slots:
        return None, {
            "status": "window_too_small",
            "energy_to_buy_kwh": energy_to_buy_kwh,
            "eligible_slots_count": 0,
            "slots_allocated": 0,
            "threshold_price": None,
        }

    pre_pv_set = {s[0] for s in pre_pv_slots}
    remaining = energy_to_buy_kwh
    cumulative_pre_pv = 0.0
    slots_allocated = 0
    last_price = None

    for slot_start, price in eligible_slots:
        if remaining <= 0:
            break

        is_pre_pv = slot_start in pre_pv_set
        if is_pre_pv and cumulative_pre_pv >= max_energy_before_pv_kwh:
            continue

        available_pre_pv_capacity = (max_energy_before_pv_kwh - cumulative_pre_pv) if is_pre_pv else float("inf")
        can_buy = min(max_per_slot_kwh, remaining, available_pre_pv_capacity)

        if can_buy <= 0:
            continue

        remaining -= can_buy
        if is_pre_pv:
            cumulative_pre_pv += can_buy
        slots_allocated += 1
        last_price = price

    threshold = last_price

    return threshold, {
        "status": "ok",
        "energy_to_buy_kwh": round(energy_to_buy_kwh, 3),
        "eligible_slots_count": len(eligible_slots),
        "slots_allocated": slots_allocated,
        "threshold_price": threshold,
        "energy_remaining_kwh": round(max(0.0, remaining), 3),
    }
