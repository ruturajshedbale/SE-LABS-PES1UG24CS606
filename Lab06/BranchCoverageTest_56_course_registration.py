import pytest

from course_registration import can_register, late_fee, waitlist_position


@pytest.mark.parametrize(
    ("status", "credits", "course", "prerequisites", "expected"),
    [
        ("regular", 10, 3, True, "registered"),
        ("regular", 22, 3, True, "credit limit exceeded"),
        ("probation", 16, 1, True, "credit limit exceeded"),
        ("honors", 25, 3, True, "registered"),
        ("regular", 10, 3, False, "prerequisites missing"),
    ],
)
def test_all_can_register_branches(status, credits, course, prerequisites, expected):
    assert can_register(status, credits, course, prerequisites) == expected


@pytest.mark.parametrize("status", ["invalid", "", "part_time"])
def test_can_register_unknown_status_branch(status):
    with pytest.raises(ValueError):
        can_register(status, 0, 3, True)


@pytest.mark.parametrize("course", [0, -1])
def test_can_register_invalid_course_branch(course):
    with pytest.raises(ValueError):
        can_register("regular", 0, course, True)


@pytest.mark.parametrize(
    ("enrolled", "capacity", "waitlist", "expected"),
    [
        (39, 40, 0, 0),
        (40, 40, 0, 1),
        (41, 40, 9, 10),
        (41, 40, 10, -1),
    ],
)
def test_all_waitlist_branches(enrolled, capacity, waitlist, expected):
    assert waitlist_position(enrolled, capacity, waitlist) == expected


@pytest.mark.parametrize("capacity", [0, -5])
def test_waitlist_invalid_capacity_branch(capacity):
    with pytest.raises(ValueError):
        waitlist_position(0, capacity, 0)


@pytest.mark.parametrize(
    ("days", "credits", "waiver", "expected"),
    [
        (0, 24, False, 0),
        (-2, 24, False, 0),
        (1, 10, True, 0),
        (7, 10, False, 500),
        (8, 10, False, 600),
        (10, 21, False, 1050),
        (25, 10, False, 2000),
    ],
)
def test_all_late_fee_branches(days, credits, waiver, expected):
    assert late_fee(days, credits, waiver) == expected
