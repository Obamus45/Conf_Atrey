"""Graphical front-end of the shell emulator (stage 1).

The window title is built from real data of the operating system
that runs the emulator, for example::

    Эмулятор - [user@hostname]

Run the application with ``python -m src.main``. The ``--demo``
flag replays the session from ``demo/demo_script.txt``
automatically, which is convenient for a screen recording.
"""

from __future__ import annotations

import argparse
import getpass
import socket
from pathlib import Path

import tkinter as tk

from .core import ShellCore

#: Window and terminal appearance (constants only).
TITLE_TEMPLATE = "Эмулятор - [{user}@{host}]"
PROMPT_TEMPLATE = "{user}@{host}:~$ "
FONT_FAMILY = "Courier New"
FONT_SIZE = 11
TEXT_WIDTH = 78
TEXT_HEIGHT = 24
BG_COLOR = "#101418"
FG_COLOR = "#d8dee6"
PROMPT_COLOR = "#4ec9b0"
ERROR_COLOR = "#f48771"
DIM_COLOR = "#7d8590"

#: Timings of the automatic demo session, in milliseconds.
DEMO_DELAY_MS = 600
CLOSE_DELAY_MS = 1200

#: Where the demo script lives (next to ``src/`` in the repo).
REPO_ROOT = Path(__file__).resolve().parent.parent
DEMO_SCRIPT = REPO_ROOT / "demo" / "demo_script.txt"

#: Fallback session used when the demo script file is missing.
DEFAULT_DEMO = [
    "ls",
    "ls -la /home/user",
    "cd /var/log",
    "foobar",
    "exit 1",
    "exit",
]


class ShellApp:
    """A Tkinter window that hosts the emulator REPL."""

    def __init__(self, root: tk.Tk, core: ShellCore) -> None:
        """Build the window with the real OS data in its title.

        Args:
            root: The main Tk root window.
            core: The headless command dispatcher.
        """
        self._root = root
        self._core = core
        user = getpass.getuser()
        host = socket.gethostname()
        title = TITLE_TEMPLATE.format(user=user, host=host)
        root.title(title)
        self._prompt = PROMPT_TEMPLATE.format(user=user, host=host)
        self._build_ui()
        self._append(self._prompt, "prompt")

    def _build_ui(self) -> None:
        """Create the terminal area and the input entry."""
        self._build_terminal()
        self._build_input()

    def _build_terminal(self) -> None:
        """Create the read-only terminal text area with tags."""
        font = (FONT_FAMILY, FONT_SIZE)
        self._text = tk.Text(
            self._root,
            wrap="none",
            width=TEXT_WIDTH,
            height=TEXT_HEIGHT,
            font=font,
            background=BG_COLOR,
            foreground=FG_COLOR,
            insertbackground=FG_COLOR,
            relief="flat",
            state="disabled",
        )
        self._text.pack(fill="both", expand=True)
        self._text.tag_config("prompt", foreground=PROMPT_COLOR)
        self._text.tag_config("error", foreground=ERROR_COLOR)
        self._text.tag_config("dim", foreground=DIM_COLOR)

    def _build_input(self) -> None:
        """Create the input line that captures the Enter key."""
        font = (FONT_FAMILY, FONT_SIZE)
        self._entry = tk.Entry(
            self._root,
            font=font,
            background=BG_COLOR,
            foreground=FG_COLOR,
            insertbackground=FG_COLOR,
            relief="flat",
        )
        self._entry.pack(fill="x")
        self._entry.bind("<Return>", self._on_return)
        self._entry.focus_set()

    def _append(self, content: str, tag: str | None = None) -> None:
        """Append text to the terminal area and scroll to it.

        Args:
            content: The text to display.
            tag: An optional name of a text tag to apply.
        """
        self._text.configure(state="normal")
        if tag is None:
            self._text.insert("end", content)
        else:
            self._text.insert("end", content, tag)
        self._text.configure(state="disabled")
        self._text.see("end")

    def _on_return(self, _event: object | None) -> None:
        """Process the line typed in the input entry.

        Args:
            _event: The Tk event (or ``None`` in demo mode); the
                value is not used.
        """
        line = self._entry.get()
        self._entry.delete("0", "end")
        self._append(line + "\n")
        self._run_line(line)

    def _run_line(self, line: str) -> None:
        """Execute one line, show the output and the new prompt.

        Args:
            line: The raw line to execute.
        """
        result = self._core.execute(line)
        if result.text:
            tag = "error" if result.is_error else None
            self._append(result.text + "\n", tag)
        if not self._core.running:
            self._close()
            return
        self._append(self._prompt, "prompt")

    def _close(self) -> None:
        """Show the farewell line and close the window."""
        self._append("session ended\n", "dim")
        self._root.after(CLOSE_DELAY_MS, self._root.destroy)

    def run_demo(self) -> None:
        """Replay the demo session automatically.

        Every demo line is scheduled with a short delay so the
        session looks like real interactive typing on the screen.
        """
        self._append("auto demo: replaying demo script\n", "dim")
        delay = 0
        for line in _load_demo_lines():
            self._root.after(delay, self._type_demo_line, line)
            delay += DEMO_DELAY_MS

    def _type_demo_line(self, line: str) -> None:
        """Simulate the user typing one demo line.

        Args:
            line: The line to type into the input entry.
        """
        self._entry.insert("end", line)
        self._on_return(None)


def _load_demo_lines() -> list[str]:
    """Read the demo script, skipping blanks and ``#`` comments.

    Returns:
        The list of lines to replay in the demo session.
    """
    if not DEMO_SCRIPT.is_file():
        return list(DEFAULT_DEMO)
    lines = DEMO_SCRIPT.read_text(encoding="utf-8").splitlines()
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            result.append(stripped)
    return result


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser.

    Returns:
        The parser with the ``--demo`` flag.
    """
    parser = argparse.ArgumentParser(
        prog="shell-emulator",
        description="Эмулятор языка оболочки ОС (вариант 26, этап 1).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="автоматически воспроизвести демо-сессию "
        "из demo/demo_script.txt",
    )
    return parser


def main() -> None:
    """Application entry point: parse args and open the window."""
    args = build_arg_parser().parse_args()
    core = ShellCore()
    root = tk.Tk()
    app = ShellApp(root, core)
    if args.demo:
        app.run_demo()
    root.mainloop()


if __name__ == "__main__":
    main()
