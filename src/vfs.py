"""In-memory virtual file system (stage 3).

The VFS is loaded from a directory on disk at startup and keeps
all its data in memory: nothing on disk is ever modified
(stage 3 requirement). The source directory is only read.
"""

from __future__ import annotations

from pathlib import Path

#: The root path of the virtual file system.
ROOT_PATH = "/"


def _read_text(path: Path) -> str:
    """Read a file as text, falling back to latin-1.

    Args:
        path: The file on disk.

    Returns:
        The decoded content (UTF-8, or latin-1 for data that is
        not valid UTF-8, so loading never fails).
    """
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


class VfsSystem:
    """A read-only in-memory virtual file system."""

    def __init__(self) -> None:
        """Create an empty VFS with a single root directory."""
        self._dirs: set[str] = {ROOT_PATH}
        self._files: dict[str, str] = {}
        self._current = ROOT_PATH

    @property
    def cwd(self) -> str:
        """The current working directory."""
        return self._current

    @property
    def stats(self) -> tuple[int, int]:
        """The number of files and directories in the VFS."""
        return len(self._files), len(self._dirs)

    @classmethod
    def from_directory(cls, source: Path) -> "VfsSystem":
        """Load a directory tree from disk into memory.

        Args:
            source: The directory on disk that becomes the VFS
                root. It is only read, never modified.

        Returns:
            A VFS with the same tree structure and file contents.
        """
        vfs = cls()
        for entry in sorted(source.rglob("*")):
            rel = entry.relative_to(source).as_posix()
            if entry.is_dir():
                vfs._dirs.add("/" + rel)
            else:
                vfs._files["/" + rel] = _read_text(entry)
        return vfs

    def exists(self, path: str) -> bool:
        """Whether the path exists (a file or a directory)."""
        return path in self._dirs or path in self._files

    def is_dir(self, path: str) -> bool:
        """Whether the path is a directory."""
        return path in self._dirs

    def resolve(self, target: str) -> str:
        """Resolve a path against the current directory.

        Args:
            target: An absolute (starting with ``/``) or relative
                path. An empty target means the current directory.

        Returns:
            The normalized path without ``.`` or ``..`` parts.
        """
        if not target:
            return self._current
        if target.startswith(ROOT_PATH):
            base = target
        elif self._current == ROOT_PATH:
            base = ROOT_PATH + target
        else:
            base = self._current + "/" + target
        parts: list[str] = []
        for part in base.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(part)
        if not parts:
            return ROOT_PATH
        return ROOT_PATH + "/".join(parts)

    def set_current(self, path: str) -> None:
        """Change the current directory to an existing one.

        Args:
            path: A normalized VFS path.

        Raises:
            ValueError: If the path is not an existing directory.
        """
        if not self.is_dir(path):
            raise ValueError(f"not a directory: {path}")
        self._current = path

    def list_dir(self, path: str) -> tuple[list[str], list[str]]:
        """List the direct children of a directory.

        Args:
            path: A normalized VFS directory path.

        Returns:
            Two sorted lists: subdirectory names, then file names.
        """
        prefix = path.rstrip("/") + "/"
        dirs: list[str] = []
        files: list[str] = []
        for entry in self._dirs:
            if entry == path or not entry.startswith(prefix):
                continue
            rest = entry[len(prefix):]
            if "/" not in rest:
                dirs.append(rest)
        for entry in self._files:
            if not entry.startswith(prefix):
                continue
            rest = entry[len(prefix):]
            if "/" not in rest:
                files.append(rest)
        return sorted(dirs), sorted(files)

    def child(self, directory: str, name: str) -> str:
        """The normalized path of a direct child entry.

        Args:
            directory: A normalized VFS directory path.
            name: The child name.

        Returns:
            The normalized child path.
        """
        base = directory.rstrip("/")
        prefix = base + "/" if base else ROOT_PATH
        return prefix + name

    def read_file(self, path: str) -> str | None:
        """Return the content of a file, or None if it is missing.

        Args:
            path: A normalized VFS file path.
        """
        return self._files.get(path)
