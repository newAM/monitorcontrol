###############################################################################
# Copyright 2019-present Alex M.
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
from types import TracebackType
from typing import List, Optional, Type, Union
import enum
import sys


@enum.unique
class PowerMode(enum.Enum):
    """ Monitor power modes. """

    on = 0x01
    standby = 0x02
    suspend = 0x03
    off_soft = 0x04
    off_hard = 0x05


class Monitor:
    """
    A physical monitor attached to a Virtual Control Panel (VCP).

    Typically you do not use this class directly and instead use
    :py:meth:`get_monitors` to get a list of initialized monitors.

    Args:
        vcp: Virtual control panel for the monitor.
    """

    def __init__(self, vcp: vcp.VCP):
        self.vcp = vcp
        self.code_maximum = {}

    def __enter__(self):
        self.vcp.__enter__()
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        return self.vcp.__exit__(
            exception_type, exception_value, exception_traceback
        )

    def _get_code_maximum(self, code: Type[vcp.VCPCode]) -> int:
        """
        Gets the maximum values for a given code, and caches in the
        class dictionary if not already found.

        Args:
            code: Feature code definition class.

        Returns:
            Maximum value for the given code.

        Raises:
            TypeError: Code is write only.
        """
        if not code.readable:
            raise TypeError(f"code is not readable: {code.name}")

        if code.value in self.code_maximum:
            return self.code_maximum[code.value]
        else:
            _, maximum = self.vcp.get_vcp_feature(code.value)
            self.code_maximum[code.value] = maximum
            return maximum

    def _set_vcp_feature(self, code: vcp.VCPCode, value: int):
        """
        Sets the value of a feature on the virtual control panel.

        Args:
            code: Feature code.
            value: Feature value.

        Raises:
            TypeError: Code is ready only.
            ValueError: Value is greater than the maximum allowable.
            VCPError: Failed to get VCP feature.
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

    def _get_vcp_feature(self, code: vcp.VCPCode) -> int:
        """
        Gets the value of a feature from the virtual control panel.

        Args:
            code: Feature code.

        Returns:
            Current feature value.

        Raises:
            TypeError: Code is write only.
            VCPError: Failed to get VCP feature.
        """
        if code.type == "wo":
            raise TypeError(f"cannot read write-only code: {code.name}")

        current, maximum = self.vcp.get_vcp_feature(code.value)
        return current

    def get_luminance(self) -> int:
        """
        Gets the monitors back-light luminance.

        Returns:
            Current luminance value.

        Raises:
            VCPError: Failed to get luminance from the VCP.
        """
        code = vcp.VCPCode("image_luminance")
        return self._get_vcp_feature(code)

    def set_luminance(self, value: int):
        """
        Sets the monitors back-light luminance.

        Args:
            value: New luminance value (typically 0-100).

        Raises:
            ValueError: Luminance outside of valid range.
            VCPError: Failed to set luminance in the VCP.
        """
        code = vcp.VCPCode("image_luminance")
        self._set_vcp_feature(code, value)

    def get_contrast(self) -> int:
        """
        Gets the monitors contrast.

        Returns:
            Current contrast value.

        Raises:
            VCPError: Failed to get contrast from the VCP.
        """
        code = vcp.VCPCode("image_contrast")
        return self._get_vcp_feature(code)

    def set_contrast(self, value: int):
        """
        Sets the monitors back-light contrast.

        Args:
            value: New contrast value (typically 0-100).

        Raises:
            ValueError: Contrast outside of valid range.
            VCPError: Failed to set contrast in the VCP.
        """
        code = vcp.VCPCode("image_contrast")
        self._set_vcp_feature(code, value)

    def get_power_mode(self) -> PowerMode:
        """
        Get the monitor power mode.

        Returns:
            Value from the :py:class:`PowerMode` enumeration.

        Raises:
            VCPError: Failed to get the power mode.
            ValueError: Set power state outside of valid range.
            KeyError: Set power mode string is invalid.
        """
        code = vcp.VCPCode("display_power_mode")
        value = self._get_vcp_feature(code)
        return PowerMode(value)

    def set_power_mode(self, value: Union[int, str, PowerMode]):
        """
        Set the monitor power mode.

        Args:
            value:
                An integer power mode,
                or a string represeting the power mode,
                or a value from :py:class:`PowerMode`.

        Raises:
            VCPError: Failed to get or set the power mode
            ValueError: Power state outside of valid range.
            AttributeError: Power mode string is invalid.
        """
        if isinstance(value, str):
            mode_value = getattr(PowerMode, value).value
        elif isinstance(value, int):
            mode_value = PowerMode(value).value
        else:
            raise TypeError("unsupported mode type: " + repr(type(value)))

        code = vcp.VCPCode("display_power_mode")
        self._set_vcp_feature(code, mode_value)


def get_vcps() -> List[Type[vcp.VCP]]:
    """
    Discovers virtual control panels.

    This function should not be used directly in most cases, use
    :py:func:`get_monitors` get monitors with VCPs.

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
        VCPError: Failed to list VCPs.

    Example:
        Setting the power mode of all monitors to standby::

            for monitor in get_monitors():
                with monitor:
                    monitor.set_power_mode("standby")

        Setting all monitors to the maximum brightness using the
        context manager::

            for monitor in get_monitors():
                with monitor:
                    monitor.set_luminance(100)
    """
    return [Monitor(v) for v in vcp.get_vcps()]
