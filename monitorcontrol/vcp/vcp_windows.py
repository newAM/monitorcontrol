from .vcp_abc import VCP, VCPError
from types import TracebackType
from typing import List, Optional, Tuple, Type
import ctypes
import sys

# hide the Windows code from Linux CI coverage
if sys.platform == "win32":
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

        def __init__(self, hmonitor: HMONITOR):
            """
            Args:
                hmonitor: logical monitor handle
            """
            self.hmonitor = hmonitor

        def __enter__(self):
            num_physical = DWORD()
            try:
                ctypes.windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(
                    self.hmonitor, ctypes.byref(num_physical)
                )
            except ctypes.WinError as e:
                raise VCPError("Windows API call failed") from e

            if num_physical.value == 0:
                raise VCPError("no physical monitor found")
            elif num_physical.value > 1:
                # TODO: Figure out a clever way around the Windows API since
                # it does not allow opening and closing of individual physical
                # monitors without their hmonitors.
                raise VCPError("more than one physical monitor per hmonitor")

            physical_monitors = (PhysicalMonitor * num_physical.value)()
            try:
                ctypes.windll.dxva2.GetPhysicalMonitorsFromHMONITOR(
                    self.hmonitor, num_physical.value, physical_monitors
                )
            except ctypes.WinError as e:
                raise VCPError("failed to open physical monitor handle") from e
            self.handle = physical_monitors[0].handle
            return self

        def __exit__(
            self,
            exception_type: Optional[Type[BaseException]],
            exception_value: Optional[BaseException],
            exception_traceback: Optional[TracebackType],
        ) -> Optional[bool]:
            try:
                ctypes.windll.dxva2.DestroyPhysicalMonitor(self.handle)
            except ctypes.WinError as e:
                raise VCPError("failed to close handle") from e
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
            try:
                ctypes.windll.dxva2.SetVCPFeature(
                    HANDLE(self.handle), BYTE(code), DWORD(value)
                )
            except ctypes.WinError as e:
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
            try:
                ctypes.windll.dxva2.GetVCPFeatureAndVCPFeatureReply(
                    HANDLE(self.handle),
                    BYTE(code),
                    None,
                    ctypes.byref(feature_current),
                    ctypes.byref(feature_max),
                )
            except ctypes.WinError as e:
                raise VCPError("failed to get VCP feature") from e
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

            try:
                ctypes.windll.dxva2.GetCapabilitiesStringLength(
                    HANDLE(self.handle), ctypes.byref(cap_length)
                )
                cap_string = (ctypes.c_char * cap_length.value)()
                ctypes.windll.dxva2.CapabilitiesRequestAndCapabilitiesReply(
                    HANDLE(self.handle), cap_string, cap_length
                )
            except ctypes.WinError as e:
                raise VCPError("failed to get VCP feature") from e
            return cap_string.value.decode("ascii")

    def get_vcps() -> List[WindowsVCP]:
        """
        Opens handles to all physical VCPs.

        Returns:
            List of all VCPs detected.

        Raises:
            VCPError: Failed to enumerate VCPs.
        """
        vcps = []
        hmonitors = []

        try:

            def _callback(hmonitor, hdc, lprect, lparam):
                hmonitors.append(HMONITOR(hmonitor))
                del hmonitor, hdc, lprect, lparam
                return True  # continue enumeration

            MONITORENUMPROC = ctypes.WINFUNCTYPE(  # noqa: N806
                BOOL, HMONITOR, HDC, ctypes.POINTER(RECT), LPARAM
            )
            callback = MONITORENUMPROC(_callback)
            ctypes.windll.user32.EnumDisplayMonitors(0, 0, callback, 0)
        except ctypes.WinError as e:
            raise VCPError("failed to enumerate VCPs") from e

        for logical in hmonitors:
            vcps.append(WindowsVCP(logical))

        return vcps
