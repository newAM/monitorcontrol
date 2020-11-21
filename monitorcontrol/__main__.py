from . import get_monitors, PowerMode
from typing import List, Optional
import argparse
import logging
import sys

if sys.version_info >= (3, 8):
    import importlib.metadata

    version = importlib.metadata.version("monitorcontrol")
else:
    import importlib_metadata

    version = importlib_metadata.version("monitorcontrol")


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
    return parser


def count_to_level(count: int) -> int:
    """ Number of -v to a logging level. """
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

    if args.version:
        sys.stdout.write(version + "\n")
        return
    elif args.get_luminance:
        for monitor in get_monitors():
            with monitor:
                luminance = monitor.get_luminance()
            sys.stdout.write(str(luminance) + "\n")
            return
    elif args.get_power_mode:
        for monitor in get_monitors():
            with monitor:
                power = monitor.get_power_mode()
            sys.stdout.write(str(power) + "\n")
            return
    elif args.set_luminance is not None:
        for monitor in get_monitors():
            with monitor:
                monitor.set_luminance(args.set_luminance)
        return
    elif args.set_power_mode is not None:
        for monitor in get_monitors():
            with monitor:
                monitor.set_power_mode(args.set_power_mode)
        return
