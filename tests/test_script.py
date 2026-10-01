"""Tests for the startup script engine (stage 2)."""

import pytest

from src.core import ShellCore
from src.script import load_script_lines, run_script


def make_core() -> ShellCore:
    """Return a fresh core instance for each test."""
    return ShellCore()


def test_load_skips_comments_and_blank_lines(tmp_path):
    """Comments (#) and empty lines are skipped, numbers kept."""
    path = tmp_path / "s.txt"
    path.write_text(
        "# comment\n\nls\n   \ncd ..\n", encoding="utf-8"
    )
    expected = [(3, "ls"), (5, "cd ..")]
    assert load_script_lines(path) == expected


def test_load_missing_file_raises(tmp_path):
    """A missing script file raises OSError."""
    with pytest.raises(OSError):
        load_script_lines(tmp_path / "no_such.txt")


def test_runs_to_the_end():
    """Without errors all lines are executed."""
    entries = [(1, "ls"), (2, "cd ..")]
    report = run_script(make_core(), entries)
    assert report.stopped_on_error is False
    executed = [step.line for step in report.steps]
    assert executed == ["ls", "cd .."]
    assert report.steps[0].output == ""


def test_stops_on_the_first_error():
    """The line after the first error is not executed."""
    entries = [(1, "ls"), (2, "bad_command"), (3, "cd ..")]
    report = run_script(make_core(), entries)
    assert report.stopped_on_error is True
    executed = [step.line for step in report.steps]
    assert executed == ["ls", "bad_command"]
    assert "cd .." not in executed
    assert report.steps[1].is_error is True
    assert report.steps[1].output == (
        "sh: bad_command: command not found"
    )


def test_demo_mode_continues_after_error():
    """With stop_on_error=False every line is executed."""
    entries = [(1, "ls"), (2, "bad_command"), (3, "cd ..")]
    report = run_script(make_core(), entries, stop_on_error=False)
    assert report.stopped_on_error is False
    executed = [step.line for step in report.steps]
    assert executed == ["ls", "bad_command", "cd .."]


def test_exit_finishes_the_script():
    """exit ends the script without being an error."""
    report = run_script(make_core(), [(1, "exit"), (2, "ls")])
    assert report.stopped_on_error is False
    executed = [step.line for step in report.steps]
    assert executed == ["exit"]


def test_exit_with_args_is_an_error_and_stops():
    """exit with arguments is an error and stops the script."""
    report = run_script(make_core(), [(1, "exit 1"), (2, "ls")])
    assert report.stopped_on_error is True
    executed = [step.line for step in report.steps]
    assert executed == ["exit 1"]


def test_line_numbers_are_kept():
    """The original file line number survives in the step."""
    entry = (7, "bad_command")
    report = run_script(make_core(), [entry])
    step = report.steps[0]
    assert step.number == entry[0]
    assert step.line == entry[1]
