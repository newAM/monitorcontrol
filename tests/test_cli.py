from .test_monitorcontrol import UnitTestVCP
from monitorcontrol import Monitor
from monitorcontrol.__main__ import main
from unittest import mock
import sys
import monitorcontrol
import pytest

get_monitors_mock = mock.patch.object(
    monitorcontrol.__main__,
    "get_monitors",
    return_value=[Monitor(UnitTestVCP({}))],
)


def test_version():
    with mock.patch.object(sys.stdout, "write") as stdout_mock:
        main(["--version"])
        stdout_mock.assert_called_once()


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
