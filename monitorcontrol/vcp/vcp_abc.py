import abc
from types import TracebackType


class VCPError(Exception):
    """Base class for all VCP related errors."""


class VCPIOError(VCPError):
    """Raised on VCP IO errors."""


class VCPPermissionError(VCPError):
    """Raised on VCP permission errors."""


class VCP(abc.ABC):
    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        exception_traceback: TracebackType | None,
    ) -> bool | None:
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

    @abc.abstractmethod
    def get_vcp_feature(self, code: int) -> tuple[int, int]:
        """
        Gets the value of a feature from the virtual control panel.

        Args:
            code: Feature code.

        Returns:
            Current feature value, maximum feature value.

        Raises:
            VCPError: Failed to get VCP feature.
        """
