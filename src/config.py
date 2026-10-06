"""Command-line configuration and the startup debug banner (stage 2)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_VFS = REPO_ROOT / "vfs"

DEMO_SCRIPT = REPO_ROOT / "demo" / "demo_script.txt"


class ConfigError(ValueError):
    """Raised when a command-line parameter is invalid."""


@dataclass(frozen=True)
class EmulatorConfig:
    """All resolved parameters of the emulator."""

    vfs_path: Path
    script_path: Path | None
    demo: bool


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser.

    Returns:
        The parser with the ``--vfs``, ``--script`` and ``--demo``
        options.
    """
    parser = argparse.ArgumentParser(
        prog="shell-emulator",
        description="Эмулятор языка оболочки ОС (вариант 26).",
    )
    parser.add_argument(
        "--vfs",
        metavar="PATH",
        help="путь к физической директории VFS "
        "(по умолчанию: vfs/ в корне репозитория)",
    )
    parser.add_argument(
        "--script",
        metavar="PATH",
        help="путь к стартовому скрипту команд эмулятора "
        "(комментарии начинаются с #)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="выполнить стандартный стартовый скрипт "
        "demo/demo_script.txt",
    )
    return parser


def _validate_vfs(value: str | None) -> Path:
    """Resolve and validate the ``--vfs`` parameter.

    Args:
        value: The raw value of ``--vfs`` (or ``None``).

    Returns:
        The validated path to the VFS directory.

    Raises:
        ConfigError: If the path is missing or not a directory.
    """
    path = Path(value) if value is not None else DEFAULT_VFS
    if not path.exists():
        raise ConfigError(f"VFS path does not exist: {path}")
    if not path.is_dir():
        raise ConfigError(f"VFS path is not a directory: {path}")
    return path


def _validate_script(value: str | None) -> Path | None:
    """Resolve and validate the ``--script`` parameter.

    Args:
        value: The raw value of ``--script`` (or ``None``).

    Returns:
        The validated path to the script file, or ``None`` when the
        parameter is not given.

    Raises:
        ConfigError: If the path is missing or not a file.
    """
    if value is None:
        return None
    path = Path(value)
    if not path.exists():
        raise ConfigError(f"startup script not found: {path}")
    if not path.is_file():
        raise ConfigError(f"startup script is not a file: {path}")
    return path


def build_config(argv: list[str]) -> EmulatorConfig:
    """Parse and validate the command-line arguments.

    Args:
        argv: The arguments without the program name.

    Returns:
        The resolved configuration.

    Raises:
        ConfigError: If any parameter is invalid.
    """
    args = build_arg_parser().parse_args(argv)
    vfs_path = _validate_vfs(args.vfs)
    script_path = _validate_script(args.script)
    if args.demo and script_path is None:
        script_path = DEMO_SCRIPT
    return EmulatorConfig(vfs_path, script_path, args.demo)


def debug_banner(config: EmulatorConfig) -> list[str]:
    """Build the startup debug lines with all the parameters.

    The banner is printed to the console and shown in the terminal
    window right after the emulator starts (stage 2 requirement).

    Args:
        config: The resolved configuration.

    Returns:
        The list of ``[debug]`` lines.
    """
    script = config.script_path
    script_text = str(script) if script is not None else "not set"
    demo_text = "yes" if config.demo else "no"
    return [
        f"[debug] vfs: {config.vfs_path}",
        f"[debug] script: {script_text}",
        f"[debug] demo: {demo_text}",
    ]
