from __future__ import annotations


def build_mask(prices: list[float], threshold: float, flip: bool, slot_minutes: int = 15) -> list[int]:
    """Build 6 U16 bitmask registers from a list of prices.

    96-bit mask: 6 registers x 16 bits. LSB = earliest time slot within each register.
    Bit=1 means price < threshold (favorable period).

    Register mapping:
      Register 1: Slots 0-15  (00:00-04:00)
      Register 2: Slots 16-31 (04:00-08:00)
      Register 3: Slots 32-47 (08:00-12:00)
      Register 4: Slots 48-63 (12:00-16:00)
      Register 5: Slots 64-79 (16:00-20:00)
      Register 6: Slots 80-95 (20:00-24:00)

    Args:
        prices: Price values per input slot. 96 values for 15-min data, 24 for hourly.
        threshold: Prices strictly below threshold -> bit=1 (favorable period).
        flip: If True, invert all bits (bit=1 for prices >= threshold instead).
        slot_minutes: Granularity of input prices in minutes (15, 30, or 60).

    Returns:
        List of 6 integers (U16, LSB = earliest time slot within each register).
    """
    slots_per_day = 96
    bits_per_input = max(1, slot_minutes // 15)

    expanded: list[float] = []
    for price in prices:
        expanded.extend([float(price)] * bits_per_input)

    if len(expanded) < slots_per_day:
        expanded.extend([0.0] * (slots_per_day - len(expanded)))
    expanded = expanded[:slots_per_day]

    regs = [0] * 6
    for i, price in enumerate(expanded):
        is_set = price < threshold
        if flip:
            is_set = not is_set
        if is_set:
            regs[i // 16] |= 1 << (i % 16)

    return regs
