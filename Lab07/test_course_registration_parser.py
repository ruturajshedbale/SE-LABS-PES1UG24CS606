from course_registration_parser import format_course_code, total_credits, parse_student_record
from hypothesis import given, strategies as st


@given(st.text() | st.none())
def test_format_course_code_no_crash(value):
    try:
        result = format_course_code(value)
    except Exception as exc:
        assert False, f"format_course_code crashed on {value!r}: {exc}"
    assert isinstance(result, str)


@given(st.text() | st.none())
def test_total_credits_no_crash(value):
    try:
        result = total_credits(value)
    except Exception as exc:
        assert False, f"total_credits crashed on {value!r}: {exc}"
    assert isinstance(result, int)


@given(st.text() | st.none())
def test_parse_student_record_no_crash(value):
    try:
        result = parse_student_record(value)
    except Exception as exc:
        assert False, f"parse_student_record crashed on {value!r}: {exc}"
    assert isinstance(result, dict)
