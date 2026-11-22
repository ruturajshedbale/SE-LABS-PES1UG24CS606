import pytest

from course_registration import can_register, late_fee, waitlist_position


@pytest.mark.parametrize(
    ("student_status", "current_credits", "course_credits", "prerequisites_met", "expected"),
    [
        ("regular", 20, 4, True, "registered"),
        ("regular", 20, 5, True, "credit limit exceeded"),
        ("probation", 13, 4, True, "credit limit exceeded"),
        ("honors", 24, 4, True, "registered"),
        ("regular", 20, 4, False, "prerequisites missing"),
    ],
)
def test_can_register_paths(student_status, current_credits, course_credits, prerequisites_met, expected):
    assert can_register(student_status, current_credits, course_credits, prerequisites_met) == expected


def test_can_register_rejects_unknown_status():
    with pytest.raises(ValueError, match="unknown status"):
        can_register("invalid", 0, 3, True)


def test_can_register_rejects_invalid_course_credits():
    with pytest.raises(ValueError, match="invalid course credits"):
        can_register("regular", 0, 0, True)


@pytest.mark.parametrize(
    ("enrolled", "capacity", "waitlist_length", "expected"),
    [
        (30, 40, 0, 0),
        (40, 40, 0, 1),
        (50, 40, 9, 10),
        (50, 40, 10, -1),
    ],
)
def test_waitlist_position_paths(enrolled, capacity, waitlist_length, expected):
    assert waitlist_position(enrolled, capacity, waitlist_length) == expected


def test_waitlist_position_rejects_invalid_capacity():
    with pytest.raises(ValueError, match="invalid capacity"):
        waitlist_position(0, 0, 0)


@pytest.mark.parametrize(
    ("days_late", "credits", "has_waiver", "expected"),
    [
        (0, 24, False, 0),
        (3, 10, True, 0),
        (7, 10, False, 500),
        (8, 10, False, 600),
        (20, 24, False, 2000),
        (7, 24, False, 750),
        (30, 10, False, 2000),
    ],
)
def test_late_fee_paths(days_late, credits, has_waiver, expected):
    assert late_fee(days_late, credits, has_waiver) == expected
