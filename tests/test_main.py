"""Tests for the command-line interface of the GUI front-end."""

from src.main import build_arg_parser


def test_no_arguments_means_interactive_mode():
    """Without flags the app runs interactively."""
    args = build_arg_parser().parse_args([])
    assert args.demo is False


def test_demo_flag_replays_demo_script():
    """The --demo flag switches on the automatic demo session."""
    args = build_arg_parser().parse_args(["--demo"])
    assert args.demo is True
