"""Tests for the command dispatch and VFS commands (stage 3)."""

from pathlib import Path

from src.core import ShellCore
from src.vfs import VfsSystem


def make_vfs(tmp_path: Path) -> ShellCore:
    """Build a small VFS on disk and a core that loads it."""
    (tmp_path / "etc").mkdir()
    (tmp_path / "home" / "user").mkdir(parents=True)
    (tmp_path / "tmp").mkdir()
    (tmp_path / "etc" / "hostname").write_text(
        "emulator\n", encoding="utf-8"
    )
    (tmp_path / "home" / "user" / "notes.txt").write_text(
        "notes here\n", encoding="utf-8"
    )
    (tmp_path / "tmp" / "scratch.txt").write_text(
        "scratch\n", encoding="utf-8"
    )
    vfs = VfsSystem.from_directory(tmp_path)
    return ShellCore(vfs)


def test_ls_lists_current_directory(tmp_path):
    """ls without arguments lists the current VFS directory."""
    core = make_vfs(tmp_path)
    result = core.execute("ls")
    assert result.is_error is False
    assert result.text == "etc/ home/ tmp/"


def test_ls_lists_another_directory(tmp_path):
    """ls with a path lists that directory."""
    core = make_vfs(tmp_path)
    result = core.execute("ls /home/user")
    assert result.is_error is False
    assert result.text == "notes.txt"


def test_ls_missing_directory_is_an_error(tmp_path):
    """ls on a non-existing path reports 'no such file'."""
    core = make_vfs(tmp_path)
    result = core.execute("ls /no_such_dir")
    assert result.is_error is True
    assert result.text == "ls: /no_such_dir: no such file or directory"


def test_ls_on_a_file_is_an_error(tmp_path):
    """ls on a file reports 'not a directory'."""
    core = make_vfs(tmp_path)
    result = core.execute("ls /etc/hostname")
    assert result.is_error is True
    assert result.text == "ls: /etc/hostname: not a directory"


def test_ls_too_many_arguments(tmp_path):
    """ls with more than one path is a wrong-argument error."""
    core = make_vfs(tmp_path)
    result = core.execute("ls /etc /tmp")
    assert result.is_error is True
    assert result.text == "ls: too many arguments"


def test_cd_absolute_and_pwd(tmp_path):
    """cd with an absolute path changes the VFS directory."""
    core = make_vfs(tmp_path)
    assert core.execute("cd /home/user").is_error is False
    assert core.execute("pwd").text == "/home/user"


def test_cd_relative_and_dot_dot(tmp_path):
    """cd supports relative paths and the '..' parent."""
    core = make_vfs(tmp_path)
    core.execute("cd /home/user")
    core.execute("cd ..")
    assert core.execute("pwd").text == "/home"
    core.execute("cd user")
    assert core.execute("pwd").text == "/home/user"


def test_cd_without_args_returns_to_root(tmp_path):
    """cd without arguments returns to the VFS root."""
    core = make_vfs(tmp_path)
    core.execute("cd /home/user")
    core.execute("cd")
    assert core.execute("pwd").text == "/"


def test_cd_missing_path_is_an_error(tmp_path):
    """cd to a non-existing path is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("cd /no_such_dir")
    assert result.is_error is True
    assert "no such file or directory" in result.text


def test_cd_to_a_file_is_an_error(tmp_path):
    """cd to a file is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("cd /etc/hostname")
    assert result.is_error is True
    assert "not a directory" in result.text


def test_cd_too_many_arguments(tmp_path):
    """cd with more than one path is a wrong-argument error."""
    core = make_vfs(tmp_path)
    result = core.execute("cd /etc /tmp")
    assert result.is_error is True
    assert result.text == "cd: too many arguments"


def test_pwd_at_root(tmp_path):
    """pwd shows the VFS root at session start."""
    core = make_vfs(tmp_path)
    result = core.execute("pwd")
    assert result.is_error is False
    assert result.text == "/"


def test_cat_prints_file_content(tmp_path):
    """cat prints the content of a VFS file."""
    core = make_vfs(tmp_path)
    core.execute("cd /home/user")
    result = core.execute("cat notes.txt")
    assert result.is_error is False
    assert result.text == "notes here\n"


def test_cat_multiple_files(tmp_path):
    """cat concatenates the content of several files."""
    core = make_vfs(tmp_path)
    result = core.execute("cat /etc/hostname /tmp/scratch.txt")
    assert result.text == "emulator\nscratch\n"


def test_cat_missing_file_is_an_error(tmp_path):
    """cat on a non-existing file is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("cat /no_such.txt")
    assert result.is_error is True
    assert "no such file or directory" in result.text


def test_cat_on_a_directory_is_an_error(tmp_path):
    """cat on a directory is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("cat /etc")
    assert result.is_error is True
    assert "is a directory" in result.text


def test_cat_without_args_is_an_error(tmp_path):
    """cat without a file operand is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("cat")
    assert result.is_error is True
    assert result.text == "cat: missing file operand"


def test_vfs_content_is_in_memory(tmp_path):
    """Changes on disk do not affect the already loaded VFS."""
    core = make_vfs(tmp_path)
    (tmp_path / "etc" / "hostname").write_text(
        "changed on disk\n", encoding="utf-8"
    )
    result = core.execute("cat /etc/hostname")
    assert result.text == "emulator\n"


def test_unknown_command_reports_error():
    """An unknown command produces the 'command not found' error."""
    result = ShellCore().execute("foobar")
    assert result.text == "sh: foobar: command not found"
    assert result.is_error is True


def test_empty_line_is_ignored():
    """An empty line produces no output and no error."""
    result = ShellCore().execute("")
    assert result.text == ""
    assert result.is_error is False


def test_exit_without_args_finishes_session():
    """A plain exit clears the running flag and prints nothing."""
    core = ShellCore()
    result = core.execute("exit")
    assert result.text == ""
    assert result.is_error is False
    assert core.running is False


def test_exit_with_args_reports_error():
    """exit with arguments is a wrong-argument error, not an exit."""
    core = ShellCore()
    result = core.execute("exit 1")
    assert result.text == "exit: too many arguments"
    assert result.is_error is True
    assert core.running is True
