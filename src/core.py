"""Core logic of the shell emulator (headless).

The module parses input lines and dispatches them to command
handlers. The graphical front-end (``src.main``) reuses this
module, so the behaviour can be unit-tested without a display.

Stage 1 (variant 26) provides:

* a simple whitespace parser (command + arguments);
* stub commands ``ls`` and ``cd`` that echo their name and args;
* the ``exit`` command;
* error messages for unknown commands and wrong arguments.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Text templates of the stub commands.
STUB_WITH_ARGS = "{name}: args: {args}"
STUB_NO_ARGS = "{name}: no args"

#: Error templates (UNIX-style messages, intentionally in English).
UNKNOWN_COMMAND = "sh: {name}: command not found"
EXIT_USAGE = "exit: too many arguments"


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


def _stub(name: str, args: list[str]) -> CommandResult:
    """Echo a stub command's name and its arguments.

    Args:
        name: The command name (``ls`` or ``cd``).
        args: The arguments that follow the command.

    Returns:
        A result with the text the stub prints to the user.
    """
    if not args:
        return CommandResult(STUB_NO_ARGS.format(name=name), False)
    text = STUB_WITH_ARGS.format(name=name, args=", ".join(args))
    return CommandResult(text, False)


class ShellCore:
    """Dispatches input lines to command handlers.

    The core keeps the minimal state needed for stage 1: the flag
    that tells the front-end whether the session is still running.
    """

    def __init__(self) -> None:
        """Create the core and register the stub commands."""
        self._running = True
        self._handlers = {
            "ls": _stub,
            "cd": _stub,
        }

    @property
    def running(self) -> bool:
        """Whether the session should keep running."""
        return self._running

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
        return handler(command, args)

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
