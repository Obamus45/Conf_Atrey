"""Tests for the command dispatch and VFS commands (stage 4)."""

from datetime import datetime
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
    (tmp_path / "home" / "user" / ".bashrc").write_text(
        "bashrc\n", encoding="utf-8"
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


def test_ls_hides_dot_files_by_default(tmp_path):
    """Dot files are not listed without the -a option."""
    core = make_vfs(tmp_path)
    result = core.execute("ls /home/user")
    assert ".bashrc" not in result.text
    assert result.text == "notes.txt"


def test_ls_a_shows_dot_files(tmp_path):
    """The -a option lists dot files first (ASCII order)."""
    core = make_vfs(tmp_path)
    result = core.execute("ls -a /home/user")
    assert result.is_error is False
    assert result.text == ".bashrc notes.txt"


def test_ls_l_long_format(tmp_path):
    """The -l option lists permissions and file sizes."""
    core = make_vfs(tmp_path)
    result = core.execute("ls -l /etc")
    assert result.is_error is False
    assert "-rw-r--r--" in result.text
    assert "hostname" in result.text
    result = core.execute("ls -l")
    assert "drwxr-xr-x" in result.text
    assert "etc/" not in result.text
    assert "etc" in result.text


def test_ls_la_combined_options(tmp_path):
    """-a and -l work together."""
    core = make_vfs(tmp_path)
    result = core.execute("ls -la /home/user")
    assert result.is_error is False
    assert ".bashrc" in result.text
    assert "-rw-r--r--" in result.text


def test_ls_invalid_option(tmp_path):
    """An unknown option letter is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("ls -x")
    assert result.is_error is True
    assert result.text == "ls: invalid option -- 'x'"


def test_cd_dash_switches_previous(tmp_path):
    """cd - returns to the previous directory and prints it."""
    core = make_vfs(tmp_path)
    core.execute("cd /home/user")
    result = core.execute("cd -")
    assert result.is_error is False
    assert result.text == "/"
    core.execute("cd -")
    assert core.execute("pwd").text == "/home/user"


def test_cd_dash_without_history_is_an_error(tmp_path):
    """cd - without a previous directory is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("cd -")
    assert result.is_error is True
    assert result.text == "cd: no previous directory"


def test_cal_via_core(tmp_path):
    """cal is registered in the command dispatcher."""
    core = make_vfs(tmp_path)
    result = core.execute("cal 1 2024")
    assert result.is_error is False
    assert "January 2024" in result.text


def test_date_via_core(tmp_path):
    """date is registered in the command dispatcher."""
    core = make_vfs(tmp_path)
    result = core.execute("date +%Y")
    assert result.is_error is False
    assert result.text == str(datetime.now().year)


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


# --- Stage 5: touch, chmod, vfs-load ------------------------------------

def test_touch_creates_empty_file(tmp_path):
    """touch creates an empty file in the current directory."""
    core = make_vfs(tmp_path)
    core.execute("cd /home/user")
    result = core.execute("touch notes2.txt")
    assert result.is_error is False
    assert result.text == ""
    assert "notes2.txt" in core.execute("ls").text
    assert core.execute("cat notes2.txt").text == ""


def test_touch_existing_file_and_dir_is_ok(tmp_path):
    """touch on existing files and directories is not an error."""
    core = make_vfs(tmp_path)
    assert core.execute("touch notes.txt").is_error is False
    assert core.execute("touch /home/user").is_error is False


def test_touch_missing_parent_is_an_error(tmp_path):
    """touch below a missing directory is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("touch /no_such_dir/file")
    assert result.is_error is True
    assert result.text == "touch: /no_such_dir/file: no such file or directory"


def test_touch_missing_operand_is_an_error(tmp_path):
    """touch without arguments is a missing-operand error."""
    core = make_vfs(tmp_path)
    result = core.execute("touch")
    assert result.is_error is True
    assert result.text == "touch: missing file operand"


def test_chmod_add_and_remove_exec_bit(tmp_path):
    """chmod +x/-x change the permission string shown by ls -l."""
    core = make_vfs(tmp_path)
    core.execute("cd /home/user")
    core.execute("touch script.sh")
    assert "-rw-r--r--" in core.execute("ls -l").text
    core.execute("chmod +x script.sh")
    long = core.execute("ls -l").text
    assert "-rwxr--r--" in long
    core.execute("chmod -x script.sh")
    lines = core.execute("ls -l").text.splitlines()
    script_line = [l for l in lines if "script.sh" in l]
    assert len(script_line) == 1
    assert script_line[0].startswith("-rw-r--r--")


def test_chmod_invalid_mode_is_an_error(tmp_path):
    """chmod with an unsupported mode is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("chmod 7z notes.txt")
    assert result.is_error is True
    assert result.text == "chmod: invalid mode: '7z'"


def test_chmod_missing_operands_are_errors(tmp_path):
    """chmod without a mode or without files is an error."""
    core = make_vfs(tmp_path)
    assert core.execute("chmod").is_error is True
    result = core.execute("chmod +x")
    assert result.is_error is True
    assert result.text == "chmod: missing operand"


def test_chmod_missing_file_is_an_error(tmp_path):
    """chmod on a missing path is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("chmod +x no_such_file")
    assert result.is_error is True
    assert result.text == "chmod: no_such_file: no such file or directory"


def test_vfs_load_replaces_the_vfs(tmp_path):
    """vfs-load replaces the in-memory VFS with another directory."""
    core = make_vfs(tmp_path)
    source = Path(__file__).resolve().parent.parent / "vfs_multi"
    result = core.execute(f"vfs-load {source}")
    assert result.is_error is False
    assert "vfs loaded: 4 files, 2 dirs" in result.text
    assert core.execute("pwd").text == "/"
    assert "alpha.txt" in core.execute("ls").text
    assert core.execute("cat alpha.txt").text.startswith("файл alpha")


def test_vfs_load_errors(tmp_path):
    """vfs-load with a bad path or bad arguments is an error."""
    core = make_vfs(tmp_path)
    result = core.execute("vfs-load /no_such_dir_xyz")
    assert result.is_error is True
    assert "no such file or directory" in result.text
    repo = Path(__file__).resolve().parent.parent
    source = repo / "vfs_minimal" / "hello.txt"
    result = core.execute(f"vfs-load {source}")
    assert result.is_error is True
    assert "not a directory" in result.text
    assert core.execute("vfs-load").is_error is True
    assert core.execute("vfs-load a b").is_error is True
    assert "alpha.txt" not in core.execute("ls").text
