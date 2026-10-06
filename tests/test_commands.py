"""Tests for the cal and date commands (stage 4)."""

import re
from datetime import datetime

from src.commands import MONTH_NAMES, cal, date


def test_cal_current_month_has_header():
    """cal without arguments prints the current month name."""
    result = cal([])
    assert result.is_error is False
    name = MONTH_NAMES[datetime.now().month - 1]
    assert name in result.text.splitlines()[0]
    assert "Su Mo Tu We Th Fr Sa" in result.text


def test_cal_known_month_grid():
    """February 2024 starts on Thursday and has five week rows."""
    result = cal(["2", "2024"])
    lines = result.text.splitlines()
    expected_rows = 7
    assert len(lines) == expected_rows
    assert lines[0].strip() == "February 2024"
    first_week = lines[2]
    assert "  1  2  3" in first_week


def test_cal_single_argument_is_month_of_current_year():
    """cal with one argument prints that month of this year."""
    now = datetime.now()
    result = cal(["1"])
    assert f"January {now.year}" in result.text


def test_cal_invalid_month_name():
    """A non-numeric month is an error."""
    result = cal(["x"])
    assert result.is_error is True
    assert result.text == "cal: invalid month: x"


def test_cal_out_of_range_month():
    """Month numbers outside 1-12 are errors."""
    assert cal(["13"]).text == "cal: invalid month: 13"
    assert cal(["0"]).text == "cal: invalid month: 0"


def test_cal_invalid_year():
    """An invalid year is an error."""
    assert cal(["1", "abc"]).text == "cal: invalid year: abc"
    assert cal(["1", "0"]).text == "cal: invalid year: 0"


def test_cal_too_many_arguments():
    """cal accepts at most a month and a year."""
    result = cal(["1", "2024", "extra"])
    assert result.is_error is True
    assert result.text == "cal: too many arguments"


def test_date_default_format():
    """date without arguments prints a full UNIX-style line."""
    result = date([])
    pattern = (
        r"^[A-Z][a-z]{2} [A-Z][a-z]{2} \d{2} "
        r"\d{2}:\d{2}:\d{2} \d{4}$"
    )
    assert re.match(pattern, result.text)
    assert result.is_error is False


def test_date_custom_format_year():
    """date +%Y prints only the current year."""
    result = date(["+%Y"])
    assert result.text == str(datetime.now().year)


def test_date_custom_format_iso():
    """date +%Y-%m-%d prints an ISO-like date."""
    result = date(["+%Y-%m-%d"])
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", result.text)


def test_date_invalid_format_argument():
    """A non-+ argument is an error."""
    result = date(["hello"])
    assert result.is_error is True
    assert result.text == "date: invalid format: hello"


def test_date_too_many_arguments():
    """date accepts at most one format argument."""
    result = date(["+%Y", "%m"])
    assert result.is_error is True
    assert result.text == "date: too many arguments"
