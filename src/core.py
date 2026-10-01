"""Core logic of the shell emulator.

The module parses input lines and dispatches them to command
handlers. Stage 3 replaces the stage 1 stubs with real commands
backed by the in-memory VFS: ``ls``, ``cd``, ``pwd`` and ``cat``.
Stage 4 deepens ``ls``/``cd`` and adds ``cal`` and ``date``.
The graphical front-end (``src.main``) reuses this module, so
the behaviour can be unit-tested without a display.
"""

from __future__ import annotations

from . import commands
from .result import CommandResult
from .vfs import ROOT_PATH, VfsSystem

#: Error templates (UNIX-style messages, intentionally in English).
UNKNOWN_COMMAND = "sh: {name}: command not found"
EXIT_USAGE = "exit: too many arguments"
LS_USAGE = "ls: too many arguments"
CD_USAGE = "cd: too many arguments"
PWD_USAGE = "pwd: too many arguments"
CAT_USAGE = "cat: missing file operand"
CD_NO_PREVIOUS = "cd: no previous directory"

#: Valid ls option letters.
LS_FLAGS = "al"

#: The prefix of a hidden (dot) entry.
DOT = "."

#: Permission strings of the ls -l mode (static on this stage).
DIR_PERMS = "drwxr-xr-x"
FILE_PERMS = "-rw-r--r--"

#: The cd argument that switches to the previous directory.
CD_PREV = "-"


def _parse_ls_args(
    args: list[str],
) -> tuple[set[str], list[str], str | None]:
    """Split ls arguments into flags, paths and an error.

    Args:
        args: The raw ls arguments.

    Returns:
        The found flags, the paths and an error message when an
        unknown option letter is met (otherwise None).
    """
    flags: set[str] = set()
    paths: list[str] = []
    error: str | None = None
    for arg in args:
        if arg.startswith("-"):
            for letter in arg[1:]:
                if letter not in LS_FLAGS:
                    error = f"ls: invalid option -- '{letter}'"
                    break
            if error is not None:
                break
            flags.update(arg[1:])
        else:
            paths.append(arg)
    return flags, paths, error


def _visible(
    dirs: list[str], files: list[str], show_hidden: bool
) -> tuple[list[str], list[str]]:
    """Filter dot entries unless hidden files are requested.

    Args:
        dirs: The subdirectory names.
        files: The file names.
        show_hidden: Whether dot entries are included.

    Returns:
        The (possibly filtered) directory and file names.
    """
    if show_hidden:
        return dirs, files
    visible_dirs = [d for d in dirs if not d.startswith(DOT)]
    visible_files = [f for f in files if not f.startswith(DOT)]
    return visible_dirs, visible_files


def _short_list(dirs: list[str], files: list[str]) -> str:
    """Build the plain ls listing line.

    Args:
        dirs: The subdirectory names.
        files: The file names.

    Returns:
        The entries in one line; directories get a trailing '/'.
    """
    dir_set = set(dirs)
    entries = [
        entry + "/" if entry in dir_set else entry
        for entry in sorted(dirs + files)
    ]
    return " ".join(entries)


def parse_line(line: str) -> tuple[str, list[str]]:
    """Split an input line into a command and its arguments.

    The parser is intentionally simple: tokens are separated by
    whitespace (spaces and tabs), as required for stage 1.

    Args:
        line: The raw line entered by the user.

    Returns:
        A ``(command, arguments)`` tuple. An empty line yields an
        empty command and an empty argument list.
    """
    tokens = line.split()
    if not tokens:
        return "", []
    return tokens[0], tokens[1:]


class ShellCore:
    """Dispatches input lines to VFS-backed command handlers."""

    def __init__(self, vfs: VfsSystem | None = None) -> None:
        """Create the core and register the commands.

        Args:
            vfs: The in-memory file system. An empty VFS is
                created when none is given.
        """
        self._running = True
        self._prev_cwd: str | None = None
        self._vfs = vfs if vfs is not None else VfsSystem()
        self._handlers = {
            "ls": self._ls,
            "cd": self._cd,
            "pwd": self._pwd,
            "cat": self._cat,
            "cal": self._cal,
            "date": self._date,
        }

    @property
    def running(self) -> bool:
        """Whether the session should keep running."""
        return self._running

    @property
    def cwd(self) -> str:
        """The current VFS directory (shown in the prompt)."""
        return self._vfs.cwd

    @property
    def vfs_stats(self) -> tuple[int, int]:
        """The VFS size: the file count and the directory count."""
        return self._vfs.stats

    def execute(self, line: str) -> CommandResult:
        """Execute one input line.

        Args:
            line: The raw line entered by the user.

        Returns:
            The result to show in the terminal area. An empty text
            means "nothing to print".
        """
        command, args = parse_line(line)
        if not command:
            return CommandResult("", False)
        if command == "exit":
            return self._exit(args)
        handler = self._handlers.get(command)
        if handler is None:
            return self._unknown(command)
        return handler(args)

    def _unknown(self, name: str) -> CommandResult:
        """Build the error result for an unknown command.

        Args:
            name: The command that was not found.

        Returns:
            The error result to show in the terminal area.
        """
        return CommandResult(UNKNOWN_COMMAND.format(name=name), True)

    def _exit(self, args: list[str]) -> CommandResult:
        """Handle the ``exit`` command.

        Args:
            args: The arguments after ``exit`` (must be empty).

        Returns:
            An error result when arguments are given; otherwise an
            empty result, and the running flag is cleared.
        """
        if args:
            return CommandResult(EXIT_USAGE, True)
        self._running = False
        return CommandResult("", False)

    def _cal(self, args: list[str]) -> CommandResult:
        """Handle the ``cal`` command (calendar, stage 4).

        Args:
            args: An optional month and an optional year.

        Returns:
            The calendar text, or an error message.
        """
        return commands.cal(args)

    def _date(self, args: list[str]) -> CommandResult:
        """Handle the ``date`` command (stage 4).

        Args:
            args: Optionally a single ``+FORMAT`` string.

        Returns:
            The formatted date text, or an error message.
        """
        return commands.date(args)

    def _ls(self, args: list[str]) -> CommandResult:
        """List a VFS directory, supporting -a and -l options.

        Args:
            args: Options (-a, -l, combinable) and at most one
                path.

        Returns:
            The listing text, or an error message.
        """
        flags, paths, error = _parse_ls_args(args)
        if error is not None:
            return CommandResult(error, True)
        if len(paths) > 1:
            return CommandResult(LS_USAGE, True)
        if paths:
            target = self._vfs.resolve(paths[0])
            name = paths[0]
        else:
            target = self._vfs.cwd
            name = target
        if not self._vfs.exists(target):
            return CommandResult(
                f"ls: {name}: no such file or directory", True
            )
        if not self._vfs.is_dir(target):
            return CommandResult(
                f"ls: {name}: not a directory", True
            )
        dirs, files = self._vfs.list_dir(target)
        dirs, files = _visible(dirs, files, "a" in flags)
        if "l" in flags:
            return CommandResult(
                self._long_list(target, dirs, files), False
            )
        return CommandResult(_short_list(dirs, files), False)

    def _long_list(
        self, target: str, dirs: list[str], files: list[str]
    ) -> str:
        """Build the ls -l lines for the given entries.

        Args:
            target: The listed VFS directory.
            dirs: The subdirectory names (already filtered).
            files: The file names (already filtered).

        Returns:
            The long-format listing joined by newlines.
        """
        lines: list[str] = []
        for name in sorted(dirs + files):
            child = self._vfs.child(target, name)
            if self._vfs.is_dir(child):
                perm, size = DIR_PERMS, "-"
            else:
                perm = FILE_PERMS
                content = self._vfs.read_file(child) or ""
                size = len(content.encode("utf-8"))
            lines.append(f"{perm}  {size:>4}  {name}")
        return "\n".join(lines)

    def _cd(self, args: list[str]) -> CommandResult:
        """Change the current VFS directory (``cd -`` goes back).

        Without arguments the core returns to the VFS root.

        Args:
            args: The command arguments (at most one path).

        Returns:
            An empty result on success, the new path for
            ``cd -``, or an error message.
        """
        if len(args) > 1:
            return CommandResult(CD_USAGE, True)
        if args and args[0] == CD_PREV:
            return self._cd_previous()
        if args:
            target = self._vfs.resolve(args[0])
        else:
            target = ROOT_PATH
        if not self._vfs.exists(target):
            return CommandResult(
                f"cd: {target}: no such file or directory", True
            )
        if not self._vfs.is_dir(target):
            return CommandResult(
                f"cd: {target}: not a directory", True
            )
        self._remember_and_move(target)
        return CommandResult("", False)

    def _cd_previous(self) -> CommandResult:
        """Switch to the previous directory (the ``cd -`` mode).

        Returns:
            The new current path, or an error when there is no
            previous directory yet.
        """
        if self._prev_cwd is None:
            return CommandResult(CD_NO_PREVIOUS, True)
        previous = self._prev_cwd
        self._prev_cwd = self._vfs.cwd
        self._vfs.set_current(previous)
        return CommandResult(self._vfs.cwd, False)

    def _remember_and_move(self, target: str) -> None:
        """Move the VFS cursor, remembering the previous one.

        Args:
            target: The validated destination VFS path.
        """
        if target != self._vfs.cwd:
            self._prev_cwd = self._vfs.cwd
        self._vfs.set_current(target)

    def _pwd(self, args: list[str]) -> CommandResult:
        """Print the current VFS directory.

        Args:
            args: The command arguments (must be empty).

        Returns:
            The current VFS path, or an error message.
        """
        if args:
            return CommandResult(PWD_USAGE, True)
        return CommandResult(self._vfs.cwd, False)

    def _cat(self, args: list[str]) -> CommandResult:
        """Print the content of one or more VFS files.

        Args:
            args: The file paths (at least one).

        Returns:
            The concatenated file contents, or an error message.
        """
        if not args:
            return CommandResult(CAT_USAGE, True)
        chunks: list[str] = []
        for arg in args:
            target = self._vfs.resolve(arg)
            if not self._vfs.exists(target):
                return CommandResult(
                    f"cat: {arg}: no such file or directory", True
                )
            if self._vfs.is_dir(target):
                return CommandResult(
                    f"cat: {arg}: is a directory", True
                )
            chunks.append(self._vfs.read_file(target) or "")
        return CommandResult("".join(chunks), False)
