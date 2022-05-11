from . import vcp
from types import TracebackType
from typing import List, Optional, Type, Union
import enum
import sys


@enum.unique
class PowerMode(enum.Enum):
    """Monitor power modes."""

    #: On.
    on = 0x01
    #: Standby.
    standby = 0x02
    #: Suspend.
    suspend = 0x03
    #: Software power off.
    off_soft = 0x04
    #: Hardware power off.
    off_hard = 0x05


@enum.unique
class InputSource(enum.Enum):
    """Monitor input sources."""

    OFF = 0x00
    ANALOG1 = 0x01
    ANALOG2 = 0x02
    DVI1 = 0x03
    DVI2 = 0x04
    COMPOSITE1 = 0x05
    COMPOSITE2 = 0x06
    SVIDEO1 = 0x07
    SVIDEO2 = 0x08
    TUNER1 = 0x09
    TUNER2 = 0x0A
    TUNER3 = 0x0B
    CMPONENT1 = 0x0C
    CMPONENT2 = 0x0D
    CMPONENT3 = 0x0E
    DP1 = 0x0F
    DP2 = 0x10
    HDMI1 = 0x11
    HDMI2 = 0x12


class InputSourceValueError(ValueError):
    """
    Raised upon an invalid (out of spec) input source value.

    https://github.com/newAM/monitorcontrol/issues/93

    Attributes:
        value (int): The value of the input source that was invalid.
    """

    def __init__(self, message: str, value: int):
        super().__init__(message)
        self.value = value


class Monitor:
    """
    A physical monitor attached to a Virtual Control Panel (VCP).

    Typically you do not use this class directly and instead use
    :py:meth:`get_monitors` to get a list of initialized monitors.

    All class methods must be called from within a context manager unless
    otherwise stated.

    Args:
        vcp: Virtual control panel for the monitor.
    """

    def __init__(self, vcp: vcp.VCP):
        self.vcp = vcp
        self.code_maximum = {}
        self._in_ctx = False

    def __enter__(self):
        self.vcp.__enter__()
        self._in_ctx = True
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        try:
            return self.vcp.__exit__(
                exception_type, exception_value, exception_traceback
            )
        finally:
            self._in_ctx = False

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
        assert (
            self._in_ctx
        ), "This function must be run within the context manager"
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
        assert (
            self._in_ctx
        ), "This function must be run within the context manager"
        if code.type == "ro":
            raise TypeError(f"cannot write read-only code: {code.name}")
        elif code.type == "rw" and code.function == "c":
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
        assert (
            self._in_ctx
        ), "This function must be run within the context manager"
        if code.type == "wo":
            raise TypeError(f"cannot read write-only code: {code.name}")

        current, maximum = self.vcp.get_vcp_feature(code.value)
        return current

    def get_vcp_capabilities(self) -> dict:
        """
        Gets the capabilities of the monitor

        Returns:
            Dictionary of capabilities in the following example format::

                {
                    "prot": "monitor",
                    "type": "LCD",
                    "cmds": {
                            1: [],
                            2: [],
                            96: [15, 17, 18],
                    },
                    "inputs": [
                        InputSource.DP1,
                        InputSource.HDMI1,
                        InputSource.HDMI2
                        # this may return integers for out-of-spec values,
                        # such as USB Type-C monitors
                    ],
                }
        """
        assert (
            self._in_ctx
        ), "This function must be run within the context manager"

        cap_str = self.vcp.get_vcp_capabilities()

        res = _parse_capabilities(cap_str)
        return res

    def get_luminance(self) -> int:
        """
        Gets the monitors back-light luminance.

        Returns:
            Current luminance value.

        Example:
            Basic Usage::

                from monitorcontrol import get_monitors

                for monitor in get_monitors():
                    with monitor:
                        print(monitor.get_luminance())

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

        Example:
            Basic Usage::

                from monitorcontrol import get_monitors

                for monitor in get_monitors():
                    with monitor:
                        monitor.set_luminance(50)

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

        Example:
            Basic Usage::

                from monitorcontrol import get_monitors

                for monitor in get_monitors():
                    with monitor:
                        print(monitor.get_contrast())

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

        Example:
            Basic Usage::

                from monitorcontrol import get_monitors

                for monitor in get_monitors():
                    with monitor:
                        print(monitor.set_contrast(50))

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

        Example:
            Basic Usage::

                from monitorcontrol import get_monitors

                for monitor in get_monitors():
                    with monitor:
                        print(monitor.get_power_mode())

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

        Example:
            Basic Usage::

                from monitorcontrol import get_monitors

                for monitor in get_monitors():
                    with monitor:
                        monitor.set_power_mode("standby")

        Raises:
            VCPError: Failed to get or set the power mode
            ValueError: Power state outside of valid range.
            AttributeError: Power mode string is invalid.
        """
        if isinstance(value, str):
            mode_value = getattr(PowerMode, value).value
        elif isinstance(value, int):
            mode_value = PowerMode(value).value
        elif isinstance(value, PowerMode):
            mode_value = value.value
        else:
            raise TypeError("unsupported mode type: " + repr(type(value)))

        code = vcp.VCPCode("display_power_mode")
        self._set_vcp_feature(code, mode_value)

    def get_input_source(self) -> InputSource:
        """
        Gets the monitors input source

        Returns:
            Current input source.

        Example:
            Basic Usage::

                from monitorcontrol import get_monitors

                for monitor in get_monitors():
                    with monitor:
                        print(monitor.get_input_source())

            Handling out-of-spec inputs (observed for USB type-C inputs)::

                from monitorcontrol import get_monitors, InputSourceValueError

                for monitor in get_monitors():
                    with monitor:
                        try:
                            print(monitor.get_input_source())
                        except InputSourceValueError as e:
                            print(e.value)

        Raises:
            VCPError: Failed to get input source from the VCP.
            InputSourceValueError:
                Input source value is not within the MCCS defined inputs.
        """
        code = vcp.VCPCode("input_select")
        value = self._get_vcp_feature(code) & 0xFF
        try:
            return InputSource(value)
        except ValueError:
            raise InputSourceValueError(
                f"{value} is not a valid InputSource", value
            )

    def set_input_source(self, value: Union[int, str, InputSource]):
        """
        Sets the monitors input source.

        Args:
            value: New input source

        Example:
            Basic Usage::

                from monitorcontrol import get_monitors

                for monitor in get_monitors():
                    with monitor:
                        print(monitor.set_input_source("DP1"))

        Raises:
            VCPError: Failed to get the input source.
            KeyError: Set input source string is invalid.
        """

        if isinstance(value, str):
            mode_value = getattr(InputSource, value.upper()).value
        elif isinstance(value, int):
            mode_value = value
        elif isinstance(value, InputSource):
            mode_value = value.value
        else:
            raise TypeError("unsupported input type: " + repr(type(value)))

        code = vcp.VCPCode("input_select")
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


def _extract_a_cap(caps_str: str, key: str) -> str:
    """
    Splits the capabilities string into individual sets.

    Returns:
        Dict of all values for the capability
    """
    start_of_filter = caps_str.upper().find(key.upper())

    if start_of_filter == -1:
        # not all keys are returned by monitor.
        # Also sometimes the string has errors.
        return ""

    start_of_filter += len(key)
    filtered_caps_str = caps_str[start_of_filter:]
    end_of_filter = 0
    for i in range(len(filtered_caps_str)):
        if filtered_caps_str[i] == "(":
            end_of_filter += 1
        if filtered_caps_str[i] == ")":
            end_of_filter -= 1
        if end_of_filter == 0:
            # dont change end_of_filter to remove the closing ")"
            break

    # 1:i to remove the first character "("
    return filtered_caps_str[1:i]


def _convert_to_dict(caps_str: str) -> dict:
    """
    Parses the VCP capabilities string to a dictionary.
    Non continuous capabilities will include an array of
    all supported values.

    Returns:
        Dict with all capabilities in hex

    Example:
        Expected string "04 14(05 06) 16" is converted to::

            {
                0x04: [],
                0x14: [0x05, 0x06],
                0x16: [],
            }
    """

    if len(caps_str) == 0:
        # Sometimes the keys arent found and the extracting of
        # capabilities returns an empty string.
        return {}

    result_dict = {}
    group = None
    prev_digit = None
    for chunk in caps_str.replace("(", " ( ").replace(")", " ) ").split(" "):
        if chunk == "":
            continue
        elif chunk == "(":
            group = prev_digit
        elif chunk == ")":
            group = None
        else:
            val = int(chunk, 16)
            if group is None:
                result_dict[val] = []
            else:
                result_dict[group].append(val)
            prev_digit = val

    return result_dict


def _parse_capabilities(caps_str: str) -> dict:
    """
    Converts the capabilities string into a nice dict
    """
    caps_dict = {
        # Used to specify the protocol class
        "prot": "",
        # Identifies the type of display
        "type": "",
        # The display model number
        "model": "",
        # A list of supported VCP codes. Somehow not the same as "vcp"
        "cmds": "",
        # A list of supported VCP codes with a list of supported values
        # for each nc code
        "vcp": "",
        # undocumented
        "mswhql": "",
        # undocumented
        "asset_eep": "",
        # MCCS version implemented
        "mccs_ver": "",
        # Specifies the window, window type (PIP or Zone) safe area size
        # (bounded safe area) maximum size of the window, minimum size of
        # the window, and window supports VCP codes for control/adjustment.
        "window": "",
        # Alternate name to be used for control
        "vcpname": "",
        # Parsed input sources into text. Not part of capabilities string.
        "inputs": "",
    }

    for key in caps_dict:
        if key in ["cmds", "vcp"]:
            caps_dict[key] = _convert_to_dict(_extract_a_cap(caps_str, key))
        else:
            caps_dict[key] = _extract_a_cap(caps_str, key)

    # Parse the input sources into a text list for readability
    input_source_cap = vcp.VCPCode("input_select").value
    if input_source_cap in caps_dict["vcp"]:
        caps_dict["inputs"] = []
        input_val_list = caps_dict["vcp"][input_source_cap]
        input_val_list.sort()

        for val in input_val_list:
            try:
                input_source = InputSource(val)
            except ValueError:
                input_source = val

            caps_dict["inputs"].append(input_source)

    return caps_dict
