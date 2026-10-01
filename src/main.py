"""Graphical front-end of the shell emulator.

The window title is built from real data of the operating system
that runs the emulator, for example::

    Эмулятор - [user@hostname]

Stage 2 adds the command-line configuration: ``--vfs PATH`` (the
physical VFS directory) and ``--script PATH`` (the startup
script). All parameters are printed as a ``[debug]`` banner on
startup, in the console and in the terminal window.

Run the application with ``python -m src.main``.
"""

from __future__ import annotations

import getpass
import socket
import sys
from pathlib import Path

import tkinter as tk

from .config import ConfigError, EmulatorConfig, build_config
from .config import debug_banner
from .core import ShellCore
from .script import ScriptReport, ScriptStep
from .script import load_script_lines, run_script

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

#: Timings of the automatic script replay, in milliseconds.
STEP_DELAY_MS = 600
CLOSE_DELAY_MS = 1200


class ShellApp:
    """A Tkinter window that hosts the emulator REPL."""

    def __init__(
        self, root: tk.Tk, core: ShellCore, config: EmulatorConfig
    ) -> None:
        """Build the window with the real OS data in its title.

        Args:
            root: The main Tk root window.
            core: The headless command dispatcher.
            config: The resolved command-line configuration.
        """
        self._root = root
        self._core = core
        user = getpass.getuser()
        host = socket.gethostname()
        title = TITLE_TEMPLATE.format(user=user, host=host)
        root.title(title)
        self._prompt = PROMPT_TEMPLATE.format(user=user, host=host)
        self._build_ui()
        for line in debug_banner(config):
            self._append(line + "\n", "dim")
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
            _event: The Tk event (not used).
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

    def run_startup_script(
        self, path: Path, stop_on_error: bool = True
    ) -> None:
        """Load and replay the startup script, imitating a dialogue.

        Both the input lines and their output are displayed with
        short delays, like a real interactive session. In the
        startup-script mode the script stops at the first error
        (stage 2 requirement); the demo mode keeps going to show
        every line.

        Args:
            path: Path to the startup script file.
            stop_on_error: Whether the first error stops the run.
        """
        try:
            entries = load_script_lines(path)
        except OSError as err:
            self._append(f"error: cannot read script: {err}\n", "error")
            return
        mode = "startup script" if stop_on_error else "demo session"
        self._append(f"{mode}: {path}\n", "dim")
        report = run_script(self._core, entries, stop_on_error)
        delay = 0
        count = len(report.steps)
        for index, step in enumerate(report.steps):
            self._root.after(delay, self._show_step, step)
            delay += STEP_DELAY_MS
            if index < count - 1:
                self._root.after(
                    delay, self._append, self._prompt, "prompt"
                )
                delay += STEP_DELAY_MS
        self._root.after(delay, self._finish_script, report)

    def _show_step(self, step: ScriptStep) -> None:
        """Render one replayed step: the input echo and its output.

        Args:
            step: The replayed script step to render.
        """
        self._append(step.line + "\n")
        if step.output:
            tag = "error" if step.is_error else None
            self._append(step.output + "\n", tag)

    def _finish_script(self, report: ScriptReport) -> None:
        """Show the script outcome and return to the prompt.

        Args:
            report: The report of the finished script run.
        """
        if not self._core.running:
            self._close()
            return
        if report.stopped_on_error:
            last = report.steps[-1]
            text = f"script stopped at line {last.number} (error)\n"
        else:
            count = len(report.steps)
            text = f"script finished: {count} command(s)\n"
        self._append(text, "dim")
        self._append(self._prompt, "prompt")


def main(argv: list[str] | None = None) -> int:
    """Application entry point.

    Args:
        argv: The command-line arguments (defaults to
            ``sys.argv[1:]``).

    Returns:
        The process exit code: 0 on success, 1 on a configuration
        error.
    """
    args = sys.argv[1:] if argv is None else argv
    try:
        config = build_config(args)
    except ConfigError as err:
        if sys.stderr is not None:
            print(f"error: {err}", file=sys.stderr)
        return 1
    if sys.stdout is not None:
        for line in debug_banner(config):
            print(line)
    root = tk.Tk()
    core = ShellCore()
    app = ShellApp(root, core, config)
    if config.script_path is not None:
        app.run_startup_script(
            config.script_path, stop_on_error=not config.demo
        )
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
