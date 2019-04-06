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

import pytest
from unittest.mock import patch
from typing import Tuple, Union, Type, List, Iterable
from .. import ddcci
from ..monitor_control import Monitor, get_vcps, get_monitors, iterate_monitors

# set to true to run the unit test on your monitors
USE_ATTACHED_MONITORS = False


class UnitTestVCP(ddcci.VCP):

    def __init__(self, vcp_dict):
        self.vcp = vcp_dict

    def open(self):
        pass

    def close(self):
        pass

    def set_vcp_feature(self, code: int, value: int):
        self.vcp[code]["current"] = value

    def get_vcp_feature(self, code: int) -> Tuple[int, int]:
        return self.vcp[code]["current"], self.vcp[code]["maximum"]


def test_get_vcps():
    get_vcps()

    with patch("sys.platform", "darwin"):
        with pytest.raises(NotImplementedError):
            get_vcps()


def test_get_monitors():
    get_monitors()


def test_iterate_monitors():
    iterate_monitors()


def get_test_vcps() -> List[Type[ddcci.VCP]]:
    if USE_ATTACHED_MONITORS:
        return get_vcps()
    else:
        unit_test_vcp_dict = {
            0x10: {
                "current": 50,
                "maximum": 100,
            },
            0xD6: {
                "current": 1,
                "maximum": 5,
            },
        }
        return [UnitTestVCP(unit_test_vcp_dict)]


@pytest.fixture(scope="module", params=get_test_vcps())
def monitor(request) -> Iterable[Monitor]:
    monitor = Monitor(request.param)
    monitor.open()
    yield monitor
    monitor.close()


def test_get_code_maximum_type_error(monitor: Monitor):
    code = ddcci.get_vcp_code_definition("image_factory_default")
    with pytest.raises(TypeError):
        monitor._get_code_maximum(code)


def test_set_vcp_feature_type_error(monitor: Monitor):
    code = ddcci.get_vcp_code_definition("active_control")
    with pytest.raises(TypeError):
        monitor._set_vcp_feature(code, 1)


def test_get_vcp_feature_type_error(monitor: Monitor):
    code = ddcci.get_vcp_code_definition("image_factory_default")
    with pytest.raises(TypeError):
        monitor._get_vcp_feature(code)


@pytest.mark.parametrize(
    "luminance, expected",
    [(100, 100), (0, 0), (50, 50), (101, ValueError)]
)
def test_luminance(
        monitor: Monitor,
        luminance: int,
        expected: Union[int, Type[Exception]]):
    original = monitor.luminance
    try:
        if isinstance(expected, int):
            monitor.luminance = luminance
            assert monitor.luminance == expected
        elif isinstance(expected, type(Exception)):
            with pytest.raises(expected):
                monitor.luminance = luminance
    finally:
        monitor.luminance = original


@pytest.mark.skipif(
    USE_ATTACHED_MONITORS,
    reason="not going to turn off your monitors"
)
@pytest.mark.parametrize(
    "mode, expected",
    [
        # always recoverable for real monitors
        ("on", 0x01),
        (0x01, 0x01),
        ("INVALID", KeyError),
        (["on"], TypeError),
        (0x00, ValueError),
        (0x06, ValueError),

        # sometimes recoverable for real monitors
        ("standby", 0x02),
        ("suspend", 0x03),
        ("off_soft", 0x04),

        # rarely recoverable for real monitors
        ("off_hard", 0x05),
    ]
)
def test_get_power_mode(
        monitor: Monitor,
        mode: Union[str, int],
        expected: Union[int, Type[Exception]]):
    if isinstance(expected, (int, str)):
        monitor.power_mode = mode
        power_mode = monitor.power_mode
        if expected != 0x01:
            # Acer XF270HU empirical testing: monitor reports zero when in any
            # power mode that is not on
            assert power_mode == expected or power_mode == 0x00
        else:
            assert monitor.power_mode == expected
    elif isinstance(expected, type(Exception)):
        with pytest.raises(expected):
            monitor.power_mode = mode


def test_context_manager(monitor: Monitor):
    monitor.close()
    with monitor:
        pass
