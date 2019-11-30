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

import abc
from typing import Tuple


class VCPError(IOError):
    """ Raised upon an error reading or writing the VCP. """

    pass


class VCP(abc.ABC):
    @abc.abstractmethod
    def open(self):
        """
        Opens the connection to the monitor.

        Raises:
            VCPError: unable to open monitor
        """
        pass

    @abc.abstractmethod
    def close(self):
        """
        Closes the connection to the monitor.

        Raises:
            VCPError: unable to open monitor
        """
        pass

    @abc.abstractmethod
    def set_vcp_feature(self, code: int, value: int):
        """
        Sets the value of a feature on the virtual control panel.

        Args:
            code: feature code
            value: feature value

        Raises:
            VCPError: failed to set VCP feature
        """
        pass

    @abc.abstractmethod
    def get_vcp_feature(self, code: int) -> Tuple[int, int]:
        """
        Gets the value of a feature from the virtual control panel.

        Args:
            code: feature code

        Returns:
            current feature value, maximum feature value

        Raises:
            VCPError: failed to get VCP feature
        """
        pass
