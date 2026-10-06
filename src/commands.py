"""Calendar and date commands (stage 4).

These commands do not touch the VFS: they work with the current
date and time of the operating system, like their UNIX
counterparts ``cal`` and ``date``.
"""

from __future__ import annotations

import calendar as py_calendar
from datetime import datetime

from .result import CommandResult

MIN_MONTH = 1
MAX_MONTH = 12
MIN_YEAR = 1
MAX_YEAR = 9999

TABLE_WIDTH = 20
WEEKDAY_HEADER = "Su Mo Tu We Th Fr Sa"

MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

MAX_CAL_ARGS = 2

CAL_USAGE = "cal: too many arguments"
DATE_USAGE = "date: too many arguments"
DEFAULT_DATE_FORMAT = "%a %b %d %H:%M:%S %Y"


class CalendarError(ValueError):
    """Raised when a cal argument is not a valid month or year."""


def cal(args: list[str]) -> CommandResult:
    """Print a month calendar (the current month by default).

    Args:
        args: An optional month (1-12) and an optional year.

    Returns:
        The calendar text, or an error message.
    """
    now = datetime.now()
    if len(args) > MAX_CAL_ARGS:
        return CommandResult(CAL_USAGE, True)
    try:
        if not args:
            month, year = now.month, now.year
        elif len(args) == 1:
            month = _parse_month(args[0])
            year = now.year
        else:
            month = _parse_month(args[0])
            year = _parse_year(args[1])
    except CalendarError as err:
        return CommandResult(str(err), True)
    return CommandResult(_month_text(month, year), False)


def date(args: list[str]) -> CommandResult:
    """Print the current date and time (UNIX ``date`` style).

    Args:
        args: Optionally a single ``+FORMAT`` strftime string.

    Returns:
        The formatted date text, or an error message.
    """
    if len(args) > 1:
        return CommandResult(DATE_USAGE, True)
    if not args:
        return CommandResult(
            datetime.now().strftime(DEFAULT_DATE_FORMAT), False
        )
    text = args[0]
    if not text.startswith("+"):
        return CommandResult(f"date: invalid format: {text}", True)
    return CommandResult(datetime.now().strftime(text[1:]), False)


def _parse_month(text: str) -> int:
    """Parse and validate the month argument of cal.

    Args:
        text: The raw argument.

    Returns:
        The month number (1-12).

    Raises:
        CalendarError: When the value is not a valid month.
    """
    value = _parse_int(text, "month")
    if not MIN_MONTH <= value <= MAX_MONTH:
        raise CalendarError(f"cal: invalid month: {value}")
    return value


def _parse_year(text: str) -> int:
    """Parse and validate the year argument of cal.

    Args:
        text: The raw argument.

    Returns:
        The year (1-9999).

    Raises:
        CalendarError: When the value is not a valid year.
    """
    value = _parse_int(text, "year")
    if not MIN_YEAR <= value <= MAX_YEAR:
        raise CalendarError(f"cal: invalid year: {value}")
    return value


def _parse_int(text: str, role: str) -> int:
    """Convert a cal argument to an integer.

    Args:
        text: The raw argument.
        role: The argument role for the error message
            (``month`` or ``year``).

    Raises:
        CalendarError: When the argument is not an integer.
    """
    try:
        return int(text)
    except ValueError:
        raise CalendarError(
            f"cal: invalid {role}: {text}"
        ) from None


def _month_text(month: int, year: int) -> str:
    """Build the calendar text of a month.

    Args:
        month: The month number (1-12).
        year: The year.

    Returns:
        The calendar lines joined by newlines.
    """
    title = f"{MONTH_NAMES[month - 1]} {year}"
    lines = [title.center(TABLE_WIDTH)]
    lines.append(WEEKDAY_HEADER)
    for week in py_calendar.monthcalendar(year, month):
        sunday_first = [week[-1]] + week[:-1]
        lines.append(_week_line(sunday_first))
    return "\n".join(lines)


def _week_line(days: list[int]) -> str:
    """Format one calendar week row.

    Args:
        days: Seven day numbers, Sunday first; 0 means empty.

    Returns:
        The row text with 2-character day columns.
    """
    cells = []
    for day in days:
        cells.append(f"{day:>2}" if day else "  ")
    return " ".join(cells)
