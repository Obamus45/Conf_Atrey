"""Core logic of the shell emulator.

The module parses input lines and dispatches them to command
handlers. Stage 3 replaces the stage 1 stubs with real commands
backed by the in-memory VFS: ``ls``, ``cd``, ``pwd`` and ``cat``.
The graphical front-end (``src.main``) reuses this module, so the
behaviour can be unit-tested without a display.
"""

from __future__ import annotations

from dataclasses import dataclass

from .vfs import ROOT_PATH, VfsSystem

#: Error templates (UNIX-style messages, intentionally in English).
UNKNOWN_COMMAND = "sh: {name}: command not found"
EXIT_USAGE = "exit: too many arguments"
LS_USAGE = "ls: too many arguments"
CD_USAGE = "cd: too many arguments"
PWD_USAGE = "pwd: too many arguments"
CAT_USAGE = "cat: missing file operand"


@dataclass(frozen=True)
class CommandResult:
    """The outcome of executing one input line."""

    text: str
    is_error: bool


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
        self._vfs = vfs if vfs is not None else VfsSystem()
        self._handlers = {
            "ls": self._ls,
            "cd": self._cd,
            "pwd": self._pwd,
            "cat": self._cat,
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

    def _ls(self, args: list[str]) -> CommandResult:
        """List a VFS directory (the current one by default).

        Args:
            args: The command arguments (at most one path).

        Returns:
            The directory entries in one line (directories marked
            with a trailing slash), or an error message.
        """
        if len(args) > 1:
            return CommandResult(LS_USAGE, True)
        if args:
            target = self._vfs.resolve(args[0])
            name = args[0]
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
        entries = [d + "/" for d in dirs] + files
        return CommandResult(" ".join(entries), False)

    def _cd(self, args: list[str]) -> CommandResult:
        """Change the current VFS directory.

        Without arguments the core returns to the VFS root.

        Args:
            args: The command arguments (at most one path).

        Returns:
            An empty result on success, or an error message.
        """
        if len(args) > 1:
            return CommandResult(CD_USAGE, True)
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
        self._vfs.set_current(target)
        return CommandResult("", False)

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
