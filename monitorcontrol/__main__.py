###############################################################################
# Copyright 2020-present Alex M.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################

from . import get_monitors, PowerMode
from typing import List, Optional
import argparse
import logging
import sys


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
        sys.stdout.write("2.3.0\n")
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
