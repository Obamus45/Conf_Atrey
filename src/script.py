"""Startup script loading and execution (stage 2).

A startup script is a plain text file: one emulator command per
line. Empty lines and lines starting with ``#`` are skipped. The
script stops at the first error, as required for stage 2.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .core import ShellCore

#: The prefix of a comment line in a startup script.
COMMENT_PREFIX = "#"


def load_script_lines(path: Path) -> list[tuple[int, str]]:
    """Read a startup script and return its command lines.

    Args:
        path: Path to the script file.

    Returns:
        Pairs of the original file line number and the command
        text; comments and empty lines are skipped.

    Raises:
        OSError: If the file cannot be read.
    """
    raw = path.read_text(encoding="utf-8").splitlines()
    result: list[tuple[int, str]] = []
    for number, line in enumerate(raw, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(COMMENT_PREFIX):
            continue
        result.append((number, stripped))
    return result


@dataclass(frozen=True)
class ScriptStep:
    """The outcome of executing one startup-script line."""

    number: int
    line: str
    output: str
    is_error: bool


@dataclass(frozen=True)
class ScriptReport:
    """The outcome of a full startup-script run."""

    steps: tuple[ScriptStep, ...]
    stopped_on_error: bool


def run_script(
    core: ShellCore,
    entries: list[tuple[int, str]],
    stop_on_error: bool = True,
) -> ScriptReport:
    """Execute the script entries through the core.

    Args:
        core: The command dispatcher.
        entries: Pairs of the line number and the command text.
        stop_on_error: When ``True`` (the startup-script mode)
            execution stops at the first error; the demo mode
            passes ``False`` to show every line including errors.

    Returns:
        The report with all executed steps. Execution also stops
        when the ``exit`` command ends the session.
    """
    steps: list[ScriptStep] = []
    stopped = False
    for number, line in entries:
        result = core.execute(line)
        steps.append(ScriptStep(number, line, result.text, result.is_error))
        if result.is_error and stop_on_error:
            stopped = True
            break
        if not core.running:
            break
    return ScriptReport(tuple(steps), stopped)
