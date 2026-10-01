"""Tests for the GUI front-end entry point (stage 2)."""

from src.main import main


def test_bad_vfs_path_returns_error(tmp_path, capsys):
    """An invalid --vfs value exits with code 1 and a message."""
    code = main(["--vfs", str(tmp_path / "no_such_dir")])
    captured = capsys.readouterr()
    assert code == 1
    assert "error:" in captured.err


def test_bad_script_path_returns_error(tmp_path, capsys):
    """An invalid --script value exits with code 1 and a message."""
    code = main(["--script", str(tmp_path / "no_such.txt")])
    captured = capsys.readouterr()
    assert code == 1
    assert "error:" in captured.err
