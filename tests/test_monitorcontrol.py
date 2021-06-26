from monitorcontrol import vcp
from monitorcontrol.monitorcontrol import (
    InputSource,
    InputSourceValueError,
    get_monitors,
    get_vcps,
    Monitor,
)
from types import TracebackType
from typing import Iterable, List, Optional, Tuple, Type, Union
import pytest
from unittest import mock


# set to true to run the unit test on your monitors
USE_ATTACHED_MONITORS = False


class UnitTestVCP(vcp.VCP):
    def __init__(self, vcp_dict: dict):
        self.vcp = vcp_dict

    def set_vcp_feature(self, code: int, value: int):
        self.vcp[code]["current"] = value

    def get_vcp_feature(self, code: int) -> Tuple[int, int]:
        return self.vcp[code]["current"], self.vcp[code]["maximum"]

    def get_vcp_capabilities(self):
        # example string from Acer VG271U
        # does not necessarily align with other test code.
        # Reported capabilities could be different.
        return (
            "(prot(monitor)type(LCD)model(ACER VG271U)cmds(01 02 03 07 0C"
            " E3 F3)vcp(04 10 12 14(05 06 08 0B) 16 18 1A 59 5A 5B 5C 5D"
            " 5E 60(0F 11 12)62 9B 9C 9D 9E 9F A0 D6 E0(00 04 05 06) E1(00"
            " 01 02)E2(00 01 02 03 05 06 07 0B 10 11 12)E3 E4 E5 E7(00 01"
            " 02) E8(00 01 02 03 04)) mswhql(1)asset_eep(40)mccs_ver(2.2))"
        )

    def __enter__(self):
        pass

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        pass


def test_context_manager_assert():
    m = Monitor(None)
    with pytest.raises(AssertionError):
        m.get_power_mode()


def test_get_vcps():
    get_vcps()


def test_get_monitors():
    get_monitors()


def get_test_vcps() -> List[Type[vcp.VCP]]:
    if USE_ATTACHED_MONITORS:
        return get_vcps()
    else:
        unit_test_vcp_dict = {
            0x10: {"current": 50, "maximum": 100},
            0xD6: {"current": 1, "maximum": 5},
            0x12: {"current": 50, "maximum": 100},
            0x60: {"current": "HDMI1", "maximum": 3},
        }
        return [UnitTestVCP(unit_test_vcp_dict)]


@pytest.fixture(scope="module", params=get_test_vcps())
def monitor(request) -> Iterable[Monitor]:
    monitor = Monitor(request.param)
    with monitor:
        yield monitor


def test_get_code_maximum_type_error(monitor: Monitor):
    code = vcp.VCPCode("image_factory_default")
    with pytest.raises(TypeError):
        monitor._get_code_maximum(code)


def test_set_vcp_feature_type_error(monitor: Monitor):
    code = vcp.VCPCode("active_control")
    with pytest.raises(TypeError):
        monitor._set_vcp_feature(code, 1)


def test_get_vcp_feature_type_error(monitor: Monitor):
    code = vcp.VCPCode("image_factory_default")
    with pytest.raises(TypeError):
        monitor._get_vcp_feature(code)


@pytest.mark.parametrize(
    "luminance, expected", [(100, 100), (0, 0), (50, 50), (101, ValueError)]
)
def test_luminance(
    monitor: Monitor, luminance: int, expected: Union[int, Type[Exception]]
):
    original = monitor.get_luminance()
    try:
        if isinstance(expected, int):
            monitor.set_luminance(luminance)
            assert monitor.get_luminance() == expected
        elif isinstance(expected, type(Exception)):
            with pytest.raises(expected):
                monitor.set_luminance(luminance)
    finally:
        monitor.set_luminance(original)


@pytest.mark.skipif(
    USE_ATTACHED_MONITORS, reason="not going to change your contrast"
)
def test_contrast(monitor: Monitor):
    contrast = monitor.get_contrast()
    contrast += 1
    monitor.set_contrast(contrast)
    assert monitor.get_contrast() == contrast


@pytest.mark.skipif(
    USE_ATTACHED_MONITORS, reason="not going to turn off your monitors"
)
@pytest.mark.parametrize(
    "mode, expected",
    [
        # always recoverable for real monitors
        ("on", 0x01),
        (0x01, 0x01),
        ("INVALID", AttributeError),
        (["on"], TypeError),
        (0x00, ValueError),
        (0x06, ValueError),
        # sometimes recoverable for real monitors
        ("standby", 0x02),
        ("suspend", 0x03),
        ("off_soft", 0x04),
        # rarely recoverable for real monitors
        ("off_hard", 0x05),
    ],
)
def test_power_mode(
    monitor: Monitor,
    mode: Union[str, int],
    expected: Union[int, Type[Exception]],
):
    if isinstance(expected, (int, str)):
        monitor.set_power_mode(mode)
        power_mode = monitor.get_power_mode().value
        if expected != 0x01:
            # Acer XF270HU empirical testing: monitor reports zero when in any
            # power mode that is not on
            assert power_mode == expected or power_mode == 0x00
        else:
            assert monitor.get_power_mode().value == expected
    elif isinstance(expected, type(Exception)):
        with pytest.raises(expected):
            monitor.set_power_mode(mode)


# ASUS VG27A when set to a mode that doesnt exist returnd analog1 (0x1)
@pytest.mark.skipif(
    USE_ATTACHED_MONITORS, reason="Real monitors dont support all input types"
)
@pytest.mark.parametrize(
    "mode, expected",
    [
        (InputSource.ANALOG1, 0x01),
        (InputSource.ANALOG2, 0x02),
        (InputSource.DVI1, 0x03),
        (InputSource.DVI2, 0x04),
        (InputSource.COMPOSITE1, 0x05),
        (InputSource.COMPOSITE2, 0x06),
        (InputSource.SVIDEO1, 0x07),
        (InputSource.SVIDEO2, 0x08),
        (InputSource.TUNER1, 0x09),
        (InputSource.TUNER2, 0x0A),
        (InputSource.TUNER3, 0x0B),
        (InputSource.CMPONENT1, 0x0C),
        (InputSource.CMPONENT2, 0x0D),
        (InputSource.CMPONENT3, 0x0E),
        (InputSource.DP1, 0x0F),
        (InputSource.DP2, 0x10),
        (InputSource.HDMI1, 0x11),
        (InputSource.HDMI2, 0x12),
    ],
)
def test_input_source(
    monitor: Monitor,
    mode: Union[str, int],
    expected: Tuple[InputSource, int],
):
    monitor.set_input_source(mode)
    read_source = monitor.get_input_source()
    assert read_source == mode


@pytest.mark.skipif(USE_ATTACHED_MONITORS, reason="This is mocked")
def test_get_input_source_type_c(monitor: Monitor):
    type_c_input = 27
    with mock.patch.object(
        monitor, "_get_vcp_feature", return_value=type_c_input
    ):
        try:
            monitor.get_input_source()
            assert 0, "Did not raise InputSourceValueError"
        except InputSourceValueError as e:
            assert e.value == type_c_input


@pytest.mark.skipif(
    USE_ATTACHED_MONITORS, reason="No value in testing this with real monitors"
)
def test_input_source_issue_59(monitor: Monitor):
    """
    Some monitors seem to duplicate the low byte (input source)
    to the high byte (reserved).
    See https://github.com/newAM/monitorcontrol/issues/59
    """
    with mock.patch.object(monitor, "_get_vcp_feature", return_value=0x1010):
        input_source = monitor.get_input_source()
        assert input_source == InputSource.DP2


def test_get_vcp_capabilities(monitor: Monitor):
    monitors_dict = monitor.get_vcp_capabilities()
    model = monitors_dict["model"]
    inputs = monitors_dict["inputs"]
    print(inputs)
    if model != "ACER VG271U":
        raise AssertionError("Could not parse model")
    if set(inputs) != {"DP1", "HDMI1", "HDMI2"}:
        raise AssertionError("Could not parse input sources")
