"""Tests for the input line parser (stage 1 requirement 3)."""

from src.core import parse_line


def test_simple_command_without_args():
    """A single token becomes the command with no arguments."""
    assert parse_line("ls") == ("ls", [])


def test_command_with_one_argument():
    """The first token is the command, the rest are arguments."""
    assert parse_line("cd /home") == ("cd", ["/home"])


def test_command_with_several_arguments():
    """All tokens after the first one become arguments."""
    result = parse_line("ls -la /home user")
    assert result == ("ls", ["-la", "/home", "user"])


def test_multiple_spaces_between_tokens():
    """Extra spaces do not create empty tokens."""
    assert parse_line("ls    -la   .") == ("ls", ["-la", "."])


def test_tabs_are_separators_too():
    """Tab characters separate tokens the same way spaces do."""
    assert parse_line("ls\t-l") == ("ls", ["-l"])


def test_empty_line_has_no_command():
    """An empty line yields an empty command and no arguments."""
    assert parse_line("") == ("", [])


def test_whitespace_only_line_has_no_command():
    """A line with only spaces yields no command."""
    assert parse_line("   ") == ("", [])
