"""Tests for the command dispatch and error handling."""

from src.core import ShellCore


def make_core() -> ShellCore:
    """Return a fresh core instance for each test."""
    return ShellCore()


def test_ls_stub_without_args():
    """The ls stub prints its name and that there are no args."""
    result = make_core().execute("ls")
    assert result.text == "ls: no args"
    assert result.is_error is False


def test_ls_stub_with_args():
    """The ls stub prints its name and all arguments."""
    result = make_core().execute("ls -la /home/user")
    assert result.text == "ls: args: -la, /home/user"
    assert result.is_error is False


def test_cd_stub_with_args():
    """The cd stub prints its name and all arguments."""
    result = make_core().execute("cd /var/log")
    assert result.text == "cd: args: /var/log"
    assert result.is_error is False


def test_unknown_command_reports_error():
    """An unknown command produces the 'command not found' error."""
    result = make_core().execute("foobar")
    assert result.text == "sh: foobar: command not found"
    assert result.is_error is True


def test_empty_line_is_ignored():
    """An empty line produces no output and no error."""
    result = make_core().execute("")
    assert result.text == ""
    assert result.is_error is False


def test_exit_without_args_finishes_session():
    """A plain exit clears the running flag and prints nothing."""
    core = make_core()
    result = core.execute("exit")
    assert result.text == ""
    assert result.is_error is False
    assert core.running is False


def test_exit_with_args_reports_error():
    """exit with arguments is a wrong-argument error, not an exit."""
    core = make_core()
    result = core.execute("exit 1")
    assert result.text == "exit: too many arguments"
    assert result.is_error is True
    assert core.running is True
