"""The shared result type of the shell command layer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    """The outcome of executing one input line."""

    text: str
    is_error: bool
