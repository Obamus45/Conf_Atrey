"""Tests for the command-line configuration (stage 2)."""

import pytest

from src.config import ConfigError, build_config, debug_banner


def test_defaults():
    """Without parameters the default VFS is used, no script."""
    config = build_config([])
    assert config.vfs_path.name == "vfs"
    assert config.script_path is None
    assert config.demo is False


def test_demo_sets_the_standard_script():
    """The --demo flag selects the standard demo script."""
    config = build_config(["--demo"])
    assert config.demo is True
    assert config.script_path is not None
    assert config.script_path.name == "demo_script.txt"


def test_explicit_vfs_directory(tmp_path):
    """An existing directory is accepted as the VFS path."""
    vfs = tmp_path / "myvfs"
    vfs.mkdir()
    config = build_config(["--vfs", str(vfs)])
    assert config.vfs_path == vfs


def test_missing_vfs_raises(tmp_path):
    """A non-existing VFS path is a configuration error."""
    with pytest.raises(ConfigError):
        build_config(["--vfs", str(tmp_path / "no_such_dir")])


def test_vfs_as_file_raises(tmp_path):
    """A file instead of a VFS directory is a configuration error."""
    file = tmp_path / "file.txt"
    file.write_text("x", encoding="utf-8")
    with pytest.raises(ConfigError):
        build_config(["--vfs", str(file)])


def test_explicit_script_file(tmp_path):
    """An existing file is accepted as the startup script."""
    script = tmp_path / "s.txt"
    script.write_text("ls\n", encoding="utf-8")
    config = build_config(["--script", str(script)])
    assert config.script_path == script


def test_missing_script_raises(tmp_path):
    """A non-existing startup script is a configuration error."""
    with pytest.raises(ConfigError):
        build_config(["--script", str(tmp_path / "no_such.txt")])


def test_script_as_directory_raises(tmp_path):
    """A directory instead of a script file is a configuration error."""
    with pytest.raises(ConfigError):
        build_config(["--script", str(tmp_path)])


def test_all_parameters_together(tmp_path):
    """All parameters can be combined in one invocation."""
    vfs = tmp_path / "v"
    vfs.mkdir()
    script = tmp_path / "s.txt"
    script.write_text("ls\n", encoding="utf-8")
    config = build_config(
        ["--vfs", str(vfs), "--script", str(script), "--demo"]
    )
    assert config.vfs_path == vfs
    assert config.script_path == script
    assert config.demo is True


def test_debug_banner_lists_all_parameters(tmp_path):
    """The banner contains every configured parameter."""
    vfs = tmp_path / "v"
    vfs.mkdir()
    script = tmp_path / "s.txt"
    script.write_text("ls\n", encoding="utf-8")
    config = build_config(["--vfs", str(vfs), "--script", str(script)])
    lines = debug_banner(config)
    assert f"[debug] vfs: {vfs}" in lines
    assert f"[debug] script: {script}" in lines
    assert "[debug] demo: no" in lines
