"""Fare helpers. Invalid inputs return None; valid results are finite."""

import math


def _nonnegative_number(text):
    try:
        value = float(text)
    except (ValueError, OverflowError):
        return None
    return value if math.isfinite(value) and value >= 0 else None


def parse_trip(text):
    """Parse a nonempty cab label and a finite, nonnegative distance."""
    if not isinstance(text, str) or text.count(':') != 1:
        return None
    cab, distance = text.split(':')
    cab = cab.strip().title()
    km = _nonnegative_number(distance)
    if not cab or km is None:
        return None
    return cab, km

def fare_average(fares_csv):
    """Return the arithmetic mean of finite nonnegative decimal fares."""
    if not isinstance(fares_csv, str):
        return None
    values = [_nonnegative_number(r) for r in fares_csv.split(',')]
    if any(value is None for value in values):
        return None
    # Scale before summing so large finite fares do not overflow the sum.
    largest = max(values)
    if largest == 0:
        return 0.0
    return largest * (math.fsum(value / largest for value in values) / len(values))

def payable_fare(text):
    """Apply 18% tax, subtract a nonnegative promo, and floor at zero."""
    if not isinstance(text, str) or text.count('|') != 1:
        return None
    fare_text, promo_text = text.split('|')
    fare = _nonnegative_number(fare_text)
    promo = _nonnegative_number(promo_text)
    if fare is None or promo is None:
        return None
    total = fare * 1.18 - promo
    if not math.isfinite(total):
        return None
    return max(total, 0.0)

def main():
    tasks = [
        (parse_trip, "Enter cab:distance in km (e.g. sedan:12): ", "Cab and Distance"),
        (fare_average, "Enter fares as CSV (e.g. 120,95,210): ", "Average Fare"),
        (payable_fare, "Enter fare|promo (e.g. 250|30): ", "Payable Fare"),
    ]
    for function, prompt, label in tasks:
        print(f"==== Running {function.__name__} ====")
        try:
            result = function(input(prompt))
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return
        if result is None:
            print("Invalid input: check the format and use finite, nonnegative numbers.")
        else:
            print(f"{label}:", result)
        print()

if __name__ == "__main__":
    main()
