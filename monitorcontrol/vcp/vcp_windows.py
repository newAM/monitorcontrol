from .vcp_abc import VCP, VCPError
from types import TracebackType
from typing import Iterator, List, Optional, Tuple, Type
import ctypes
import logging

from ctypes.wintypes import (
    DWORD,
    RECT,
    BOOL,
    HMONITOR,
    HDC,
    LPARAM,
    HANDLE,
    BYTE,
    WCHAR,
)


# structure type for a physical monitor
class PhysicalMonitor(ctypes.Structure):
    _fields_ = [("handle", HANDLE), ("description", WCHAR * 128)]


class WindowsVCP(VCP):
    """
    Windows API access to a monitor's virtual control panel.

    References:
        https://stackoverflow.com/questions/16588133/
    """

    def __init__(self, handle: HANDLE, description: str):
        """
        Args:
            handle: Handle to the physical monitor.
            description: Text description of the physical monitor.
        """
        self.logger = logging.getLogger(__name__)
        self.handle = handle
        self.description = description

    def __del__(self):
        WindowsVCP._destroy_physical_monitor(self.handle)

    def __enter__(self):
        pass

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        return False

    def set_vcp_feature(self, code: int, value: int):
        """
        Sets the value of a feature on the virtual control panel.

        Args:
            code: Feature code.
            value: Feature value.

        Raises:
            VCPError: Failed to set VCP feature.
        """
        self.logger.debug(
            "SetVCPFeature(_, {code=}, {value=})",
            extra=dict(code=code, value=value),
        )
        try:
            if not ctypes.windll.dxva2.SetVCPFeature(
                HANDLE(self.handle), BYTE(code), DWORD(value)
            ):
                raise VCPError("failed to set VCP feature: " + ctypes.FormatError())
        except OSError as e:
            raise VCPError("failed to close handle") from e

    def get_vcp_feature(self, code: int) -> Tuple[int, int]:
        """
        Gets the value of a feature from the virtual control panel.

        Args:
            code: Feature code.

        Returns:
            Current feature value, maximum feature value.

        Raises:
            VCPError: Failed to get VCP feature.
        """
        feature_current = DWORD()
        feature_max = DWORD()
        self.logger.debug(
            "GetVCPFeatureAndVCPFeatureReply(_, {code=}, None, _, _)",
            extra=dict(code=code),
        )
        try:
            if not ctypes.windll.dxva2.GetVCPFeatureAndVCPFeatureReply(
                HANDLE(self.handle),
                BYTE(code),
                None,
                ctypes.byref(feature_current),
                ctypes.byref(feature_max),
            ):
                raise VCPError("failed to get VCP feature: " + ctypes.FormatError())
        except OSError as e:
            raise VCPError("failed to get VCP feature") from e
        self.logger.debug(
            "GetVCPFeatureAndVCPFeatureReply -> ({feat_cur}, {feat_max})",
            extra=dict(feat_cur=feature_current.value, feat_max=feature_max.value),
        )
        return feature_current.value, feature_max.value

    def get_vcp_capabilities(self):
        """
        Gets capabilities string from the virtual control panel

        Returns:
            One long capabilities string in the format:
            "(prot(monitor)type(LCD)model(ACER VG271U)cmds(01 02 03 07 0C)"

            No error checking for the string being valid. String can have
            bit errors or dropped characters.

        Raises:
            VCPError: Failed to get VCP feature.
        """

        cap_length = DWORD()
        self.logger.debug("GetCapabilitiesStringLength")
        try:
            if not ctypes.windll.dxva2.GetCapabilitiesStringLength(
                HANDLE(self.handle), ctypes.byref(cap_length)
            ):
                raise VCPError(
                    "failed to get VCP capabilities: " + ctypes.FormatError()
                )
            cap_string = (ctypes.c_char * cap_length.value)()
            self.logger.debug("CapabilitiesRequestAndCapabilitiesReply")
            if not ctypes.windll.dxva2.CapabilitiesRequestAndCapabilitiesReply(
                HANDLE(self.handle), cap_string, cap_length
            ):
                raise VCPError(
                    "failed to get VCP capabilities: " + ctypes.FormatError()
                )
        except OSError as e:
            raise VCPError("failed to get VCP capabilities") from e
        return cap_string.value.decode("ascii")

    @staticmethod
    def _get_physical_monitors() -> Iterator[Tuple[HANDLE, str]]:
        """
        Returns a list of physical monitors.
        """
        return (
            physical_monitor
            for hmonitor in WindowsVCP._get_hmonitors()
            for physical_monitor in WindowsVCP._physical_monitors_from_hmonitor(
                hmonitor
            )
        )

    @staticmethod
    def _get_hmonitors() -> List[HMONITOR]:
        """
        Calls the Windows `EnumDisplayMonitors` API in Python-friendly form.
        """
        hmonitors = []  # type: List[HMONITOR]
        try:

            def _callback(hmonitor, hdc, lprect, lparam):
                hmonitors.append(HMONITOR(hmonitor))
                del hmonitor, hdc, lprect, lparam
                return True  # continue enumeration

            MONITORENUMPROC = ctypes.WINFUNCTYPE(  # noqa: N806
                BOOL, HMONITOR, HDC, ctypes.POINTER(RECT), LPARAM
            )
            callback = MONITORENUMPROC(_callback)
            if not ctypes.windll.user32.EnumDisplayMonitors(0, 0, callback, 0):
                raise VCPError("Call to EnumDisplayMonitors failed")
        except OSError as e:
            raise VCPError("failed to enumerate VCPs") from e
        return hmonitors

    @staticmethod
    def _physical_monitors_from_hmonitor(
        hmonitor: HMONITOR,
    ) -> Iterator[Tuple[HANDLE, str]]:
        """
        Calls the Windows `GetPhysicalMonitorsFromHMONITOR` API in Python-friendly form.
        """
        num_physical = DWORD()
        try:
            if not ctypes.windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(
                hmonitor, ctypes.byref(num_physical)
            ):
                raise VCPError(
                    "Call to GetNumberOfPhysicalMonitorsFromHMONITOR failed: "
                    + ctypes.FormatError()
                )
        except OSError as e:
            raise VCPError(
                "Call to GetNumberOfPhysicalMonitorsFromHMONITOR failed"
            ) from e

        physical_monitors = (PhysicalMonitor * num_physical.value)()
        try:
            if not ctypes.windll.dxva2.GetPhysicalMonitorsFromHMONITOR(
                hmonitor, num_physical.value, physical_monitors
            ):
                raise VCPError(
                    "Call to GetPhysicalMonitorsFromHMONITOR failed: "
                    + ctypes.FormatError()
                )
        except OSError as e:
            raise VCPError("failed to open physical monitor handle") from e
        return (
            [physical_monitor.handle, physical_monitor.description]
            for physical_monitor in physical_monitors
        )

    @staticmethod
    def _destroy_physical_monitor(handle: HANDLE) -> None:
        """
        Calls the Windows `DestroyPhysicalMonitor` API in Python-friendly form.
        """
        try:
            if not ctypes.windll.dxva2.DestroyPhysicalMonitor(handle):
                raise VCPError(
                    "Call to DestroyPhysicalMonitor failed: " + ctypes.FormatError()
                )
        except OSError as e:
            raise VCPError("failed to close handle") from e


def get_vcps() -> List[WindowsVCP]:
    """
    Opens handles to all physical VCPs.

    Returns:
        List of all VCPs detected.

    Raises:
        VCPError: Failed to enumerate VCPs.
    """
    physical_monitors = WindowsVCP._get_physical_monitors()
    return list(
        WindowsVCP(handle, description) for (handle, description) in physical_monitors
    )
