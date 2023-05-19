import os
import sys
import pathlib

PACKAGE_PARENT=pathlib.Path(__file__).parent
SCRIPT_DIR=PACKAGE_PARENT
sys.path.append(str(SCRIPT_DIR))

from monitorcontrol import get_monitors, PowerMode, InputSource
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
    group.add_argument(
        "--get-monitors-fast",
        action="store_true",
        help="Get the monitors and query only display controller id and firmware version",
    )
    group = parser.add_argument_group("Optional monitor select")
    group.add_argument(
        "--monitor",
        type=int,
        default=None,
        help="Select monitor for command. "
        "Default: getters use monitor 1. Setters use all monitors.",
    )
    group.add_argument(
        "--display-controller-id",
        default=None,
        help="Filter monitor(s) by display controller id for command. "
    )
    group.add_argument(
        "--firmware-version",
        default=None,
        help="Filter monitor(s) by firmware version for command. "
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

def monitor_match(monitor_obj, exp_disp_ctrl, exp_firmware):
    with monitor_obj:
        disp_ctrl = monitor_obj.get_display_controller_id()
        firmware = monitor_obj.get_firmware_ver()
        eq = exp_disp_ctrl == f'{disp_ctrl:x}'
        rv = False
        if exp_disp_ctrl == f'{disp_ctrl:x}':
            rv = exp_firmware == f'{firmware:x}' if exp_firmware is not None else True
        sys.stdout.write(f"{'including' if rv else 'excluding'} monitor display_controller: {disp_ctrl:x} firmware: {firmware:x}\n")
        return rv

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
                if args.display_controller_id is not None and not monitor_match(monitor_obj, args.display_controller_id, args.firmware_version): continue
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
    elif args.get_monitors_fast:
        for monitor_index, monitor_obj in enumerate(get_monitors(), 0):
            with monitor_obj:
                disp_ctrl = monitor_obj.get_display_controller_id()
                firmware = monitor_obj.get_firmware_ver()
                sys.stdout.write(f"Monitor {monitor_index + 1}: display_controller: {disp_ctrl:x} firmware: {firmware:x}\n")
        return
    else:
        raise AssertionError("Internal error, please report this bug")


if __name__ == "__main__":
    main()