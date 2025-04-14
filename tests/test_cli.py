from .test_monitorcontrol import UnitTestVCP
from monitorcontrol import Monitor
import monitorcontrol.__main__
from monitorcontrol.__main__ import main, count_to_level

from unittest import mock
import monitorcontrol
import pytest

get_monitors_mock = mock.patch.object(
    monitorcontrol.__main__,
    "get_monitors",
    return_value=[Monitor(UnitTestVCP({}))],
)


def test_version():
    with mock.patch("builtins.print") as stdout_mock:
        main(["--version"])
        stdout_mock.assert_called_once()


def test_get_luminance():
    with get_monitors_mock, mock.patch.object(Monitor, "get_luminance") as api_mock:
        main(["--get-luminance"])
        api_mock.assert_called_once()


@pytest.mark.parametrize("value", [0, 100])
def test_set_luminance(value: int):
    with get_monitors_mock, mock.patch.object(Monitor, "set_luminance") as api_mock:
        main(["--set-luminance", str(value)])
        api_mock.assert_called_once_with(value)


def test_get_volume():
    with get_monitors_mock, mock.patch.object(Monitor, "get_volume") as api_mock:
        main(["--get-volume"])
        api_mock.assert_called_once()


@pytest.mark.parametrize("value", [0, 100])
def test_set_volume(value: int):
    with get_monitors_mock, mock.patch.object(Monitor, "set_volume") as api_mock:
        main(["--set-volume", str(value)])
        api_mock.assert_called_once_with(value)


def test_get_power():
    with get_monitors_mock, mock.patch.object(Monitor, "get_power_mode") as api_mock:
        main(["--get-power"])
        api_mock.assert_called_once()


@pytest.mark.parametrize("value", ["on", "suspend"])
def test_set_power(value: int):
    with get_monitors_mock, mock.patch.object(Monitor, "set_power_mode") as api_mock:
        main(["--set-power", str(value)])
        api_mock.assert_called_once_with(value)


def test_get_audio_mute():
    with (
        get_monitors_mock,
        mock.patch.object(Monitor, "get_audio_mute_mode") as api_mock,
    ):
        main(["--get-audio-mute"])
        api_mock.assert_called_once()


@pytest.mark.parametrize("value", ["on", "off"])
def test_set_audio_mute(value: int):
    with (
        get_monitors_mock,
        mock.patch.object(Monitor, "set_audio_mute_mode") as api_mock,
    ):
        main(["--set-audio-mute", str(value)])
        api_mock.assert_called_once_with(value)


def test_get_input_source():
    with get_monitors_mock, mock.patch.object(Monitor, "get_input_source") as api_mock:
        main(["--get-input-source"])
        api_mock.assert_called_once()


@pytest.mark.parametrize("value", ["DP1", "HDMI1", "27"])
def test_set_input_source(value: str):
    with get_monitors_mock, mock.patch.object(Monitor, "set_input_source") as api_mock:
        main(["--set-input-source", str(value)])
        api_mock.assert_called_once_with(value)


def test_get_monitors():
    with (
        get_monitors_mock,
        mock.patch.object(Monitor, "get_input_source") as input_source_api_mock,
        mock.patch.object(Monitor, "get_vcp_capabilities") as vcp_capabilities_api_mock,
    ):
        main(["--get-monitors"])
        input_source_api_mock.assert_called()
        vcp_capabilities_api_mock.assert_called()


def test_count_to_level_cli():
    for num_v in range(1, 10):
        main(["--version", "-" + "v" * num_v])


def test_count_to_level():
    for num_v in range(10):
        assert isinstance(count_to_level(num_v), int)
