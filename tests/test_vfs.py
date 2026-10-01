"""Tests for the in-memory virtual file system (stage 3)."""

from pathlib import Path

import pytest

from src.vfs import VfsSystem


def build_tree(base: Path) -> None:
    """Create a small directory tree under ``base``."""
    (base / "etc").mkdir()
    (base / "home" / "user").mkdir(parents=True)
    (base / "empty").mkdir()
    (base / "etc" / "hostname").write_text(
        "emulator\n", encoding="utf-8"
    )
    (base / "home" / "user" / "notes.txt").write_text(
        "notes\n", encoding="utf-8"
    )


def test_from_directory_loads_the_tree(tmp_path):
    """The disk tree (files and directories) ends up in memory."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    assert vfs.is_dir("/etc")
    assert vfs.is_dir("/home/user")
    assert vfs.exists("/home/user/notes.txt")
    assert vfs.is_dir("/empty")
    expected = (2, 5)  # two files, five directories (incl. /)
    assert vfs.stats == expected


def test_resolve_absolute_path(tmp_path):
    """An absolute path is normalized without changing its meaning."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    assert vfs.resolve("/etc/hostname") == "/etc/hostname"
    assert vfs.resolve("/") == "/"


def test_resolve_relative_path_from_cwd(tmp_path):
    """A relative path is resolved against the current directory."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    vfs.set_current("/home")
    assert vfs.resolve("user") == "/home/user"
    assert vfs.resolve("user/notes.txt") == "/home/user/notes.txt"
    assert vfs.resolve("") == "/home"


def test_resolve_dot_and_dot_dot(tmp_path):
    """'.' stays in place and '..' goes to the parent directory."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    vfs.set_current("/home/user")
    assert vfs.resolve(".") == "/home/user"
    assert vfs.resolve("..") == "/home"
    assert vfs.resolve("notes.txt/..") == "/home/user"


def test_dot_dot_at_root_stays_at_root(tmp_path):
    """Going above the root keeps the root (like a real shell)."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    assert vfs.resolve("../..") == "/"
    vfs.set_current("/etc")
    assert vfs.resolve("../../x") == "/x"


def test_list_dir_returns_direct_children(tmp_path):
    """Nested entries are not listed in the parent directory."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    dirs, files = vfs.list_dir("/")
    assert dirs == ["empty", "etc", "home"]
    assert files == []


def test_list_dir_mixed_children(tmp_path):
    """A directory with only files lists exactly those files."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    dirs, files = vfs.list_dir("/etc")
    assert dirs == []
    assert files == ["hostname"]


def test_list_empty_directory(tmp_path):
    """An empty directory yields two empty lists."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    dirs, files = vfs.list_dir("/empty")
    assert dirs == []
    assert files == []


def test_read_file_content(tmp_path):
    """read_file returns the exact content, None when missing."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    assert vfs.read_file("/etc/hostname") == "emulator\n"
    assert vfs.read_file("/no_such.txt") is None


def test_vfs_is_independent_from_disk(tmp_path):
    """Modifying or deleting the source does not change the VFS."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    (tmp_path / "etc" / "hostname").write_text(
        "changed\n", encoding="utf-8"
    )
    (tmp_path / "empty").rmdir()
    assert vfs.read_file("/etc/hostname") == "emulator\n"
    assert vfs.is_dir("/empty")


def test_set_current_rejects_non_directory(tmp_path):
    """set_current refuses files and non-existing paths."""
    build_tree(tmp_path)
    vfs = VfsSystem.from_directory(tmp_path)
    with pytest.raises(ValueError):
        vfs.set_current("/etc/hostname")
    with pytest.raises(ValueError):
        vfs.set_current("/no_such_dir")


def test_crlf_source_is_normalized_to_lf(tmp_path):
    """Windows CRLF endings are normalized to LF on loading."""
    source = tmp_path / "crlf.txt"
    source.write_bytes("one\r\ntwo\r\n".encode("utf-8"))
    vfs = VfsSystem.from_directory(tmp_path)
    assert vfs.read_file("/crlf.txt") == "one\ntwo\n"
