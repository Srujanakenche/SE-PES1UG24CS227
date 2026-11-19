import math

import pytest
from hypothesis import example, given, settings, strategies as st
from ride_share_fare import parse_trip, fare_average, payable_fare

settings.register_profile("lab", max_examples=300, derandomize=True)
settings.load_profile("lab")

unexpected = st.one_of(st.text(), st.none(), st.integers(), st.floats(),
                       st.booleans(), st.binary(), st.lists(st.integers()),
                       st.dictionaries(st.text(), st.integers()))


@given(unexpected)
@example("sedan:nan")
@example("sedan:-1")
def test_parse_trip_no_crash(s):
    result = parse_trip(s)
    if result is not None:
        cab, km = result
        assert isinstance(cab, str) and cab.strip()
        assert math.isfinite(km) and km >= 0


@given(unexpected)
@example("nan,1")
@example("-1,2")
def test_fare_average_no_crash(s):
    result = fare_average(s)
    if result is not None:
        assert math.isfinite(result) and result >= 0


@given(unexpected)
@example("nan|0")
@example("-1|0")
def test_payable_fare_no_crash(s):
    result = payable_fare(s)
    if result is not None:
        assert math.isfinite(result) and result >= 0


@given(st.sampled_from(["mini", "sedan", "suv"]),
       st.integers(min_value=0, max_value=10**9))
def test_valid_trip(cab, km):
    assert parse_trip(f"  {cab.upper()} : {km}  ") == (cab.title(), float(km))


@given(st.lists(st.integers(min_value=0, max_value=10**9), min_size=1,
                max_size=50))
@example([1, 2])
def test_average_matches_arithmetic_mean(values):
    result = fare_average(",".join(map(str, values)))
    assert result == pytest.approx(sum(values) / len(values))
    assert min(values) <= result <= max(values)


@given(st.integers(min_value=0, max_value=10**9),
       st.integers(min_value=0, max_value=10**9))
def test_payable_matches_tax_and_promo(fare, promo):
    assert payable_fare(f"{fare}|{promo}") == pytest.approx(
        max(fare * 1.18 - promo, 0))


@pytest.mark.parametrize("fn,bad", [
    (parse_trip, ["", "sedan", ":2", "sedan:1:2", "sedan:-1",
                  "sedan:nan", "sedan:inf", "sedan:1e9999"]),
    (fare_average, ["", "1,,2", "1,", "one,two", "-1,2", "nan,1", "inf"]),
    (payable_fare, ["", "1", "1|2|3", "-1|0", "1|-2", "nan|0",
                    "inf|0", "1.7e308|0"]),
])
def test_malformed_input_is_rejected(fn, bad):
    for value in bad:
        assert fn(value) is None, repr(value)


@pytest.mark.parametrize("fn", [parse_trip, fare_average, payable_fare])
@pytest.mark.parametrize("value", [None, 1, True, [], {}, b"1"])
def test_non_string_input_is_rejected(fn, value):
    assert fn(value) is None


def test_decimal_fares_and_extreme_finite_values():
    assert fare_average("1.5,2.5") == 2.0
    assert fare_average("1e308,1e308") == 1e308
    assert payable_fare("0|100") == 0.0
