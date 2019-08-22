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

from . import vcp
import sys
from typing import Type, List, Union, Iterable


class Monitor:
    """
    A physical monitor attached to a Virtual Control Panel (VCP).

    Generated with :py:meth:`get_monitors()` or
    :py:meth:`iterate_monitors()`.

    Args:
        vcp: virtual control panel for the monitor
    """

    #: Power modes and their integer values.
    POWER_MODES = {
        "on": 0x01,
        "standby": 0x02,
        "suspend": 0x03,
        "off_soft": 0x04,
        "off_hard": 0x05,
    }

    def __init__(self, vcp: Type[vcp.VCP]):
        self.vcp = vcp
        self.code_maximum = {}

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        """
        Opens the connection to the VCP.

        Raises:
            VCPError: failed to open VCP
        """
        self.vcp.open()

    def close(self):
        """
        Closes the connection to the VCP.

        Raises:
            VCPError: failed to close VCP
        """
        self.vcp.close()

    def _get_code_maximum(self, code: Type[vcp.VCPCode]) -> int:
        """
        Gets the maximum values for a given code, and caches in the
        class dictionary if not already found.

        Args:
            code: feature code definition class

        Returns:
            maximum value for the given code

        Raises:
            TypeError: code is write only
        """
        if not code.readable:
            raise TypeError(f"code is not readable: {code.name}")

        if code.value in self.code_maximum:
            return self.code_maximum[code.value]
        else:
            _, maximum = self.vcp.get_vcp_feature(code.value)
            self.code_maximum[code.value] = maximum
            return maximum

    def _set_vcp_feature(self, code: Type[vcp.VCPCode], value: int):
        """
        Sets the value of a feature on the virtual control panel.

        Args:
            code: feature code definition class
            value: feature value

        Raises:
            TypeError: code is ready only
            ValueError: value is greater than the maximum allowable
            VCPError: failed to get VCP feature
        """
        if code.type == "ro":
            raise TypeError(f"cannot write read-only code: {code.name}")
        elif code.type == "rw":
            maximum = self._get_code_maximum(code)
            if value > maximum:
                raise ValueError(
                    f"value of {value} exceeds code maximum of {maximum}"
                )

        self.vcp.set_vcp_feature(code.value, value)

    def _get_vcp_feature(self, code: Type[vcp.VCPCode]) -> int:
        """
        Gets the value of a feature from the virtual control panel.

        Args:
            code: feature code definition class

        Returns:
            current feature value

        Raises:
            TypeError: code is write only
            VCPError: failed to get VCP feature
        """
        if code.type == "wo":
            raise TypeError(f"cannot read write-only code: {code.name}")

        current, maximum = self.vcp.get_vcp_feature(code.value)
        return current

    @property
    def luminance(self) -> int:
        """
        Gets the monitors back-light luminance.

        Returns:
            current luminance value

        Raises:
            VCPError: failed to get luminance from the VCP
        """
        code = vcp.get_vcp_code_definition("image_luminance")
        return self._get_vcp_feature(code)

    @luminance.setter
    def luminance(self, value: int):
        """
        Sets the monitors back-light luminance.

        Args:
            value: new luminance value (typically 0-100)

        Raises:##### have not implemented or checked
            ValueError: luminance outside of valid range
            VCPError: failed to set luminance in the VCP
        """
        code = vcp.get_vcp_code_definition("image_luminance")
        self._set_vcp_feature(code, value)

    @property
    def contrast(self) -> int:
        """
        Gets the monitors contrast.

        Returns:
            current contrast value

        Raises:
            VCPError: failed to get contrast from the VCP
        """
        code = vcp.get_vcp_code_definition("image_contrast")
        return self._get_vcp_feature(code)

    @contrast.setter
    def contrast(self, value: int):
        """
        Sets the monitors back-light contrast.

        Args:
            value: new contrast value (typically 0-100)

        Raises:
            ValueError: contrast outside of valid range
            VCPError: failed to set contrast in the VCP
        """
        code = vcp.get_vcp_code_definition("image_contrast")
        self._set_vcp_feature(code, value)

    @property
    def power_mode(self) -> int:
        """
        The monitor power mode.

        When used as a getter this returns the integer value of the
        monitor power mode.

        When used as a setter an integer value or a power mode
        string from :py:attr:`Monitor.POWER_MODES` may be used.

        Raises:
            VCPError: failed to get or set the power mode
            ValueError: set power state outside of valid range
            KeyError: set power mode string is invalid
        """
        code = vcp.get_vcp_code_definition("display_power_mode")
        return self._get_vcp_feature(code)

    @power_mode.setter
    def power_mode(self, value: Union[int, str]):
        if isinstance(value, str):
            mode_value = Monitor.POWER_MODES[value]
        elif isinstance(value, int):
            mode_value = value
        else:
            raise TypeError("unsupported mode type: " + repr(type(value)))
        if mode_value not in Monitor.POWER_MODES.values():
            raise ValueError(f"cannot set reserved mode value: {mode_value}")
        code = vcp.get_vcp_code_definition("display_power_mode")
        self._set_vcp_feature(code, mode_value)


def get_vcps() -> List[Type[vcp.VCP]]:
    """
    Discovers virtual control panels.

    This function should not be used directly in most cases, use
    :py:meth:`get_monitors()` or :py:meth:`iterate_monitors()` to
    get monitors with VCPs.

    Returns:
        List of VCPs in a closed state.

    Raises:
        NotImplementedError: not implemented for your operating system
        VCPError: failed to list VCPs
    """
    if sys.platform == "win32" or sys.platform.startswith("linux"):
        return vcp.get_vcps()
    else:
        raise NotImplementedError(f"not implemented for {sys.platform}")


def get_monitors() -> List[Monitor]:
    """
    Creates a list of all monitors.

    Returns:
        List of monitors in a closed state.

    Raises:
        NotImplementedError: not implemented for your operating system
        VCPError: failed to list VCPs

    Example:
        Setting the power mode of all monitors to standby::

            for monitor in get_monitors():
                try:
                    monitor.open()
                    # put monitor in standby mode
                    monitor.power_mode = "standby"
                except VCPError:
                    print("uh-oh")
                    raise
                finally:
                    monitor.close()

        Setting all monitors to the maximum brightness using the
        context manager::

            for monitor in get_monitors():
                with monitor as m:
                    # set back-light luminance to 100%
                    m.luminance = 100
    """
    return [Monitor(v) for v in get_vcps()]


def iterate_monitors() -> Iterable[Monitor]:
    """
    Iterates through all monitors, opening and closing the VCP for
    each monitor.

    Yields:
        Monitor in an open state.

    Raises:
        NotImplementedError: not implemented for this platform
        VCPError: failed to list VCPs

    Example:
        Setting all monitors to the maximum brightness::

            for monitor in iterate_monitors():
                monitor.luminance = 100
    """
    for v in get_vcps():
        monitor = Monitor(v)
        with monitor:
            yield monitor
