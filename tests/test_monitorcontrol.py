from monitorcontrol import vcp
from monitorcontrol.monitorcontrol import (
    get_monitors,
    get_vcps,
    Monitor,
)
from types import TracebackType
from typing import Iterable, List, Optional, Tuple, Type, Union
import pytest


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
        ("ANALOG1", 0x01),
        ("ANALOG2", 0x02),
        ("DVI1", 0x03),
        ("DVI2", 0x04),
        ("COMPOSITE1", 0x05),
        ("COMPOSITE2", 0x06),
        ("SVIDEO1", 0x07),
        ("SVIDEO2", 0x08),
        ("TUNER1", 0x09),
        ("TUNER2", 0x0A),
        ("TUNER3", 0x0B),
        ("CMPONENT1", 0x0C),
        ("CMPONENT2", 0x0D),
        ("CMPONENT3", 0x0E),
        ("DP1", 0x0F),
        ("DP2", 0x10),
        ("HDMI1", 0x11),
        ("HDMI2", 0x12),
    ],
)
def test_input_source(
    monitor: Monitor,
    mode: Union[str, int],
    expected: Union[int, Type[Exception]],
):
    if isinstance(expected, (int, str)):
        monitor.set_input_source(mode)
        read_source = monitor.get_input_source()
        assert read_source == mode
