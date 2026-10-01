"""In-memory virtual file system (stages 3 and 5).

The VFS is loaded from a directory on disk at startup and keeps
all its data in memory: nothing on disk is ever modified
(stage 3 requirement). The source directory is only read.
Stage 5 adds in-memory modifications: ``touch`` and ``chmod``
change the stored tree and permission strings, and ``vfs-load``
replaces the tree with another one loaded from disk.
"""

from __future__ import annotations

from pathlib import Path

#: The root path of the virtual file system.
ROOT_PATH = "/"

#: Default permission strings of the VFS entries.
DEFAULT_DIR_PERMS = "drwxr-xr-x"
DEFAULT_FILE_PERMS = "-rw-r--r--"

#: The position of the owner execute bit in a permission string.
EXEC_BIT = 3


def _read_text(path: Path) -> str:
    """Read a file as text, falling back to latin-1.

    Args:
        path: The file on disk.

    Returns:
        The decoded content (UTF-8, or latin-1 for data that is
        not valid UTF-8, so loading never fails). Line endings
        are normalized to LF, so the VFS content does not depend
        on the operating system that created the source
        directory (Windows text files use CRLF).
    """
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    return text.replace("\r\n", "\n")


class VfsSystem:
    """An in-memory virtual file system (modifiable in stage 5)."""

    def __init__(self) -> None:
        """Create an empty VFS with a single root directory."""
        self._dirs: set[str] = {ROOT_PATH}
        self._files: dict[str, str] = {}
        self._perms: dict[str, str] = {ROOT_PATH: DEFAULT_DIR_PERMS}
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
                vfs._perms["/" + rel] = DEFAULT_DIR_PERMS
            else:
                vfs._files["/" + rel] = _read_text(entry)
                vfs._perms["/" + rel] = DEFAULT_FILE_PERMS
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

    def parent(self, path: str) -> str:
        """The parent directory of a normalized VFS path.

        Args:
            path: A normalized VFS path (file or directory).

        Returns:
            The parent directory; the root for first-level paths.
        """
        base = path.rstrip("/")
        index = base.rfind("/")
        if index <= 0:
            return ROOT_PATH
        return base[:index]

    def perm(self, path: str) -> str | None:
        """The permission string of an entry, or None if missing.

        Args:
            path: A normalized VFS path.
        """
        return self._perms.get(path)

    def create_file(self, path: str) -> None:
        """Create an empty file (the parent must exist).

        Args:
            path: A normalized VFS path that does not exist yet.
        """
        self._files[path] = ""
        self._perms[path] = DEFAULT_FILE_PERMS

    def toggle_exec(self, path: str, enable: bool) -> None:
        """Set or clear the owner execute bit of an entry.

        Args:
            path: A normalized VFS path of an existing entry.
            enable: Whether the execute bit must be set.
        """
        perm = list(self._perms[path])
        perm[EXEC_BIT] = "x" if enable else "-"
        self._perms[path] = "".join(perm)
