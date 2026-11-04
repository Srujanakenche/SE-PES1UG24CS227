"""Decision and boundary tests, with expected values derived by hand."""
import pytest
from ride_share_fare import extra_distance_fare, seats_and_bags_ok, pickup_status


@pytest.mark.parametrize("cab,distance,message", [
    ("bus", 10, "unknown cab type"), ("mini", -1, "invalid distance"),
])
def test_invalid_inputs(cab, distance, message):
    with pytest.raises(ValueError, match=f"^{message}$"):
        extra_distance_fare(cab, distance, "city", False)


@pytest.mark.parametrize("cab,distance,zone,subscriber,expected", [
    ("mini", 0, "city", False, 0),
    ("mini", 5, "city", False, 0),
    ("sedan", 8, "city", False, 0),
    ("suv", 12, "city", False, 0),
    ("mini", 8, "city", True, 0),
    ("mini", 9, "city", True, 12),
    ("sedan", 12, "city", True, 12),
    ("suv", 13, "city", True, 12),
    ("mini", 6, "outstation", False, 18),
    ("mini", 25, "city", False, 240),
    ("mini", 26, "city", False, 420),
    ("mini", 25, "outstation", False, 360),
    ("mini", 26, "outstation", False, 630),
    ("mini", 5.5, "city", False, 6),
])
def test_fare_branches(cab, distance, zone, subscriber, expected):
    assert extra_distance_fare(cab, distance, zone, subscriber) == expected


@pytest.mark.parametrize("passengers,bags,wheelchair,expected", [
    (2, 3, True, True), (3, 0, True, False),
    (5, 0, False, False), (4, 2, False, True), (4, 3, False, False),
])
def test_capacity_branches(passengers, bags, wheelchair, expected):
    assert seats_and_bags_ok(passengers, bags, wheelchair) is expected


@pytest.mark.parametrize("scheduled,airport,cutoff", [
    (False, False, 5), (False, True, 15),
    (True, False, 10), (True, True, 20),
])
@pytest.mark.parametrize("offset,expected", [
    (0, "on_time"), (-1, "delayed"), (-15, "delayed"), (-16, "missed"),
])
def test_pickup_boundaries(scheduled, airport, cutoff, offset, expected):
    assert pickup_status(cutoff + offset, scheduled, airport) == expected
