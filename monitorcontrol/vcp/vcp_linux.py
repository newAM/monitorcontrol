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

from .vcp_abc import VCP, VCPIOError, VCPPermissionError
from types import TracebackType
from typing import List, Optional, Tuple, Type
import os
import struct
import sys
import time

# hide the Linux code from Windows CI coverage
if sys.platform.startswith("linux"):
    import fcntl
    import pyudev


class LinuxVCP(VCP):
    """
    Linux API access to a monitor's virtual control panel.

    References:
        https://github.com/Informatic/python-ddcci
        https://github.com/siemer/ddcci/
    """

    GET_VCP_HEADER_LENGTH = 2  # header packet length
    PROTOCOL_FLAG = 0x80  # protocol flag is bit 7 of the length byte

    # VCP commands
    GET_VCP_CMD = 0x01  # get VCP feature command
    GET_VCP_REPLY = 0x02  # get VCP feature reply code
    SET_VCP_CMD = 0x03  # set VCP feature command

    # timeouts
    GET_VCP_TIMEOUT = 0.04  # at least 40ms per the DDCCI specification
    CMD_RATE = 0.05  # at least 50ms between messages

    # addresses
    DDCCI_ADDR = 0x37  # DDC-CI command address on the I2C bus
    HOST_ADDRESS = 0x50  # virtual I2C slave address of the host
    I2C_SLAVE = 0x0703  # I2C bus slave address

    GET_VCP_RESULT_CODES = {
        0: "No Error",
        1: "Unsupported VCP code",
    }

    def __init__(self, bus_number: int):
        """
        Args:
            bus_number: I2C bus number.
        """
        self.bus_number = bus_number
        self.fd: Optional[str] = None
        self.fp = None
        # time of last feature set call
        self.last_set: Optional[float] = None

    def __enter__(self):
        try:
            self.fp = f"/dev/i2c-{self.bus_number}"
            self.fd = os.open(self.fp, os.O_RDWR)
            fcntl.ioctl(self.fd, self.I2C_SLAVE, self.DDCCI_ADDR)
            self.read_bytes(1)
        except PermissionError as e:
            raise VCPPermissionError(f"permission error for {self.fp}") from e
        except OSError as e:
            raise VCPIOError(f"unable to open VCP at {self.fp}") from e
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        try:
            os.close(self.fd)
        except OSError as e:
            raise VCPIOError("unable to close descriptor") from e
        self.fd = None

        return False

    def set_vcp_feature(self, code: int, value: int):
        """
        Sets the value of a feature on the virtual control panel.

        Args:
            code: feature code
            value: feature value

        Raises:
            VCPIOError: failed to set VCP feature
        """
        self.rate_limt()

        # transmission data
        data = bytearray()
        data.append(self.SET_VCP_CMD)
        data.append(code)
        low_byte, high_byte = struct.pack("H", value)
        data.append(high_byte)
        data.append(low_byte)

        # add headers and footers
        data.insert(0, (len(data) | self.PROTOCOL_FLAG))
        data.insert(0, self.HOST_ADDRESS)
        data.append(self.get_checksum(data))

        # write data
        self.write_bytes(data)

        # store time of last set VCP
        self.last_set = time.time()

    def get_vcp_feature(self, code: int) -> Tuple[int, int]:
        """
        Gets the value of a feature from the virtual control panel.

        Args:
            code: Feature code.

        Returns:
            Current feature value, maximum feature value.

        Raises:
            VCPIOError: Failed to get VCP feature.
        """
        self.rate_limt()

        # transmission data
        data = bytearray()
        data.append(self.GET_VCP_CMD)
        data.append(code)

        # add headers and footers
        data.insert(0, (len(data) | self.PROTOCOL_FLAG))
        data.insert(0, self.HOST_ADDRESS)
        data.append(self.get_checksum(data))

        # write data
        self.write_bytes(data)

        time.sleep(self.GET_VCP_TIMEOUT)

        # read the data
        header = self.read_bytes(self.GET_VCP_HEADER_LENGTH)
        source, length = struct.unpack("BB", header)
        length &= ~self.PROTOCOL_FLAG  # clear protocol flag
        payload = self.read_bytes(length + 1)

        # check checksum
        payload, checksum = struct.unpack(f"{length}sB", payload)
        calculated_checksum = self.get_checksum(header + payload)
        checksum_xor = checksum ^ calculated_checksum
        if checksum_xor:
            raise VCPIOError(f"checksum does not match: {checksum_xor}")

        # unpack the payload
        (
            reply_code,
            result_code,
            vcp_opcode,
            vcp_type_code,
            feature_max,
            feature_current,
        ) = struct.unpack(">BBBBHH", payload)

        if reply_code != self.GET_VCP_REPLY:
            raise VCPIOError(
                f"received unexpected response code: {reply_code}"
            )

        if vcp_opcode != code:
            raise VCPIOError(f"received unexpected opcode: {vcp_opcode}")

        if result_code > 0:
            try:
                message = self.GET_VCP_RESULT_CODES[result_code]
            except KeyError:
                message = f"received result with unknown code: {result_code}"
            raise VCPIOError(message)

        return feature_current, feature_max

    def get_checksum(self, data: List, prime: bool = False) -> int:
        """
        Computes the checksum for a set of data, with the option to
        use the virtual host address (per the DDC-CI specification).

        Args:
            data: data array to transmit
            prime: compute checksum using the 0x50 virtual host address

        Returns:
            checksum for the data
        """
        checksum = self.HOST_ADDRESS
        for data_byte in data:
            checksum ^= data_byte
        return checksum

    def rate_limt(self):
        """ Rate limits messages to the VCP. """
        if self.last_set is None:
            return

        rate_delay = self.CMD_RATE - time.time() - self.last_set
        if rate_delay > 0:
            time.sleep(rate_delay)

    def read_bytes(self, num_bytes: int) -> bytes:
        """
        Reads bytes from the I2C bus.

        Args:
            num_bytes: number of bytes to read

        Raises:
            VCPIOError: unable to read data
        """
        try:
            return os.read(self.fd, num_bytes)
        except OSError as e:
            raise VCPIOError("unable to read from I2C bus") from e

    def write_bytes(self, data: bytes):
        """
        Writes bytes to the I2C bus.

        Args:
            data: data to write to the I2C bus

        Raises:
            VCPIOError: unable to write data
        """
        try:
            os.write(self.fd, data)
        except OSError as e:
            raise VCPIOError("unable write to I2C bus") from e


def get_vcps() -> List[LinuxVCP]:
    """
    Interrogates I2C buses to determine if they are DDC-CI capable.

    Returns:
        List of all VCPs detected.
    """
    vcps = []

    # iterate I2C devices
    for device in pyudev.Context().list_devices(subsystem="i2c"):
        vcp = LinuxVCP(device.sys_number)
        try:
            with vcp:
                pass
        except (OSError, VCPIOError):
            pass
        else:
            vcps.append(vcp)

    return vcps
