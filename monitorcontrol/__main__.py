from . import get_monitors, PowerMode, InputSource
from typing import List, Optional
import argparse
import importlib.metadata
import logging
import sys

version = importlib.metadata.version("monitorcontrol")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="monitorcontrol",
        description="Monitor controls using MCCS over DDC-CI.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase logging verbosity.",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--set-luminance", type=int, help="Set the lumianance of all monitors."
    )
    group.add_argument(
        "--get-luminance",
        action="store_true",
        help="Get the lumianance of the first monitor.",
    )
    group.add_argument(
        "--get-power-mode",
        action="store_true",
        help="Get the power mode of the first monitor.",
    )
    group.add_argument(
        "--set-power-mode",
        choices=[mode.name for mode in PowerMode],
        help="Set the power mode of all monitors.",
    )
    group.add_argument(
        "--version", action="store_true", help="Show the version and exit."
    )
    group.add_argument(
        "--get-input-source",
        action="store_true",
        help="Get the input source of each monitor.",
    )
    group.add_argument(
        "--set-input-source",
        choices=[mode.name for mode in InputSource],
        help="Set the input source of all monitors.",
    )
    group.add_argument(
        "--get-monitors",
        action="store_true",
        help="Get the monitors.",
    )
    group = parser.add_argument_group("Optional monitor select")
    group.add_argument(
        "--monitor",
        type=int,
        default=None,
        help="Select monitor for command. "
        "Default: getters use monitor 1. Setters use all monitors.",
    )
    return parser


def count_to_level(count: int) -> int:
    """Number of -v to a logging level."""
    if count == 1:
        return logging.ERROR
    elif count == 2:
        return logging.WARNING
    elif count == 3:
        return logging.INFO
    elif count >= 4:
        return logging.DEBUG

    return logging.CRITICAL


def main(argv: Optional[List[str]] = None):
    parser = get_parser()
    args = parser.parse_args(argv)

    logging_level = count_to_level(args.verbose)
    root_logger = logging.getLogger()
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(logging_level)
    formatter = logging.Formatter("{levelname} {name} {message}", style="{")
    handler.setFormatter(formatter)
    root_logger.setLevel(logging_level)
    root_logger.addHandler(handler)

    monitor_index = 0
    if args.monitor is not None:
        monitor_index = args.monitor - 1

    if args.version:
        sys.stdout.write(version + "\n")
        return
    elif args.get_luminance:
        monitor_obj = get_monitors()[monitor_index]
        with monitor_obj:
            luminance = monitor_obj.get_luminance()
        sys.stdout.write(str(luminance) + "\n")
        return
    elif args.get_power_mode:
        monitor_obj = get_monitors()[monitor_index]
        with monitor_obj:
            power = monitor_obj.get_power_mode()
        sys.stdout.write(str(power.name) + "\n")
        return
    elif args.set_luminance is not None:
        if args.monitor is None:
            for monitor_obj in get_monitors():
                with monitor_obj:
                    monitor_obj.set_luminance(args.set_luminance)
        else:
            monitor_obj = get_monitors()[monitor_index]
            with monitor_obj:
                monitor_obj.set_luminance(args.set_luminance)
        return
    elif args.set_power_mode is not None:
        if args.monitor is None:
            for monitor_obj in get_monitors():
                with monitor_obj:
                    monitor_obj.set_power_mode(args.set_power_mode)
        else:
            monitor_obj = get_monitors()[monitor_index]
            with monitor_obj:
                monitor_obj.set_power_mode(args.set_power_mode)
        return
    elif args.get_input_source:
        monitor_obj = get_monitors()[monitor_index]
        with monitor_obj:
            input_source = monitor_obj.get_input_source()
        sys.stdout.write(str(input_source) + "\n")
        return
    elif args.set_input_source is not None:
        if args.monitor is None:
            for monitor_obj in get_monitors():
                with monitor_obj:
                    monitor_obj.set_input_source(args.set_input_source)
        else:
            monitor_obj = get_monitors()[monitor_index]
            with monitor_obj:
                monitor_obj.set_input_source(args.set_input_source)
        return
    elif args.get_monitors:
        for monitor_index, monitor_obj in enumerate(get_monitors(), 0):
            with monitor_obj:
                monitors_dict = monitor_obj.get_vcp_capabilities()
                current_input = monitor_obj.get_input_source()
            model = monitors_dict["model"]
            inputs = monitors_dict["inputs"]
            sys.stdout.write(f"Monitor {monitor_index + 1}: {model}" + "\n")
            sys.stdout.write("Available Inputs:\n")
            for i in inputs:
                sys.stdout.write(f"\t{i}")
                if i == current_input:
                    sys.stdout.write("*\n")
                else:
                    sys.stdout.write("\n")

        return
    else:
        raise AssertionError("Internal error, please report this bug")
