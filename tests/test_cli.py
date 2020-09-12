###############################################################################
# Copyright 2019 Alex M.
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

from .test_monitorcontrol import UnitTestVCP
from monitorcontrol import Monitor
from monitorcontrol.__main__ import main
from unittest import mock
import monitorcontrol
import os
import pytest
import sys
import toml

get_monitors_mock = mock.patch.object(
    monitorcontrol.__main__,
    "get_monitors",
    return_value=[Monitor(UnitTestVCP({}))],
)


def test_version():
    toml_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "pyproject.toml"
    )
    with open(toml_path, "r") as f:
        pyproject = toml.load(f)

    toml_version = pyproject["tool"]["poetry"]["version"]

    with mock.patch.object(sys.stdout, "write") as stdout_mock:
        main(["--version"])
        stdout_mock.assert_called_once_with(f"{toml_version}\n")


def test_get_luminance():
    with get_monitors_mock, mock.patch.object(
        Monitor, "get_luminance"
    ) as api_mock:
        main(["--get-luminance"])
        api_mock.assert_called_once()


@pytest.mark.parametrize("value", [0, 100])
def test_set_luminance(value: int):
    with get_monitors_mock, mock.patch.object(
        Monitor, "set_luminance"
    ) as api_mock:
        main(["--set-luminance", str(value)])
        api_mock.assert_called_once_with(value)


def test_get_power():
    with get_monitors_mock, mock.patch.object(
        Monitor, "get_power_mode"
    ) as api_mock:
        main(["--get-power"])
        api_mock.assert_called_once()


@pytest.mark.parametrize("value", ["on", "suspend"])
def test_set_power(value: int):
    with get_monitors_mock, mock.patch.object(
        Monitor, "set_power_mode"
    ) as api_mock:
        main(["--set-power", str(value)])
        api_mock.assert_called_once_with(value)
