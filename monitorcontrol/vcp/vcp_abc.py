import abc
from types import TracebackType
from typing import Optional, Tuple, Type


class VCPError(Exception):
    """Base class for all VCP related errors."""

    pass


class VCPIOError(VCPError):
    """Raised on VCP IO errors."""

    pass


class VCPPermissionError(VCPError):
    """Raised on VCP permission errors."""

    pass


class VCP(abc.ABC):
    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        pass

    @abc.abstractmethod
    def set_vcp_feature(self, code: int, value: int):
        """
        Sets the value of a feature on the virtual control panel.

        Args:
            code: Feature code.
            value: Feature value.

        Raises:
            VCPError: Failed to set VCP feature.
        """
        pass

    @abc.abstractmethod
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
        pass
