import itertools
import os
import struct
import sys
from unittest import mock

import pytest

from monitorcontrol.vcp import vcp_linux
from monitorcontrol.vcp.vcp_abc import VCPIOError, VCPPermissionError
from monitorcontrol.vcp.vcp_linux import LinuxVCP


linux_only = pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Linux-only VCP implementation",
)


def open_vcp() -> LinuxVCP:
    """A LinuxVCP with a fake open file descriptor and stubbed bus I/O."""
    vcp = LinuxVCP(0)
    vcp.fd = 10
    vcp.write_bytes = mock.Mock()
    return vcp


def build_get_vcp_reply(
    code: int,
    current: int,
    maximum: int,
    reply_code: int = LinuxVCP.GET_VCP_REPLY,
    result_code: int = 0,
    source: int = 0x6E,
) -> tuple[bytes, bytes]:
    """Builds a (header, payload+checksum) DDC-CI get-VCP-feature reply."""
    payload = struct.pack(
        ">BBBBHH", reply_code, result_code, code, 0x00, maximum, current
    )
    length = len(payload)
    header = bytes([source, length | LinuxVCP.PROTOCOL_FLAG])
    checksum = LinuxVCP.get_checksum(bytearray(header + payload))
    return header, payload + bytes([checksum])


def build_caps_packet(
    text: bytes,
    offset: int,
    reply_code: int = LinuxVCP.GET_VCP_CAPS_REPLY,
    source: int = 0x6E,
) -> tuple[bytes, bytes]:
    """Builds a (header, payload+checksum) capabilities reply packet."""
    payload = struct.pack(">B", reply_code) + struct.pack(">H", offset) + text
    length = len(payload)
    header = bytes([source, length | LinuxVCP.PROTOCOL_FLAG])
    checksum = LinuxVCP.get_checksum(bytearray(header + payload))
    return header, payload + bytes([checksum])


# ---------------------------------------------------------------------------
# get_vcps
# ---------------------------------------------------------------------------


@linux_only
def test_get_vcps_skips_devices_without_sys_number():
    # i2c devices without a sysfs number cannot map to a /dev/i2c-* bus and
    # must be skipped rather than passed to LinuxVCP.
    device = mock.Mock(sys_number=None)
    context = mock.Mock()
    context.list_devices.return_value = [device]
    with mock.patch.object(vcp_linux, "pyudev") as pyudev_mock:
        pyudev_mock.Context.return_value = context
        assert vcp_linux.get_vcps() == []
    context.list_devices.assert_called_once_with(subsystem="i2c")


# ---------------------------------------------------------------------------
# __enter__ / __exit__
# ---------------------------------------------------------------------------


@linux_only
def test_enter_success():
    vcp = LinuxVCP(0)
    with (
        mock.patch.object(vcp_linux.os, "open", return_value=7) as m_open,
        mock.patch.object(vcp_linux.fcntl, "ioctl"),
        mock.patch.object(vcp_linux.os, "read", return_value=b"\x00"),
    ):
        assert vcp.__enter__() is vcp
    assert vcp.fd == 7
    m_open.assert_called_once_with(vcp.fp, os.O_RDWR)


@linux_only
def test_enter_permission_error():
    vcp = LinuxVCP(0)
    with (
        mock.patch.object(vcp_linux.os, "open", side_effect=PermissionError()),
        mock.patch.object(vcp_linux.os, "close") as m_close,
    ):
        with pytest.raises(VCPPermissionError):
            vcp.__enter__()
    # open failed before assigning fd, so there is nothing to close
    m_close.assert_not_called()


@linux_only
def test_enter_io_error_closes_fd():
    vcp = LinuxVCP(0)
    with (
        mock.patch.object(vcp_linux.os, "open", return_value=7),
        mock.patch.object(vcp_linux.fcntl, "ioctl", side_effect=OSError()),
        mock.patch.object(vcp_linux.os, "close") as m_close,
    ):
        with pytest.raises(VCPIOError):
            vcp.__enter__()
    m_close.assert_called_once_with(7)


@linux_only
def test_exit_closes_fd():
    vcp = open_vcp()
    with mock.patch.object(vcp_linux.os, "close") as m_close:
        assert vcp.__exit__(None, None, None) is False
    assert vcp.fd is None
    m_close.assert_called_once_with(10)


@linux_only
def test_exit_close_error():
    vcp = open_vcp()
    with mock.patch.object(vcp_linux.os, "close", side_effect=OSError()):
        with pytest.raises(VCPIOError):
            vcp.__exit__(None, None, None)


# ---------------------------------------------------------------------------
# read_bytes / write_bytes
# ---------------------------------------------------------------------------


@linux_only
def test_read_bytes_success():
    vcp = open_vcp()
    with mock.patch.object(vcp_linux.os, "read", return_value=b"ab") as m_read:
        assert vcp.read_bytes(2) == b"ab"
    m_read.assert_called_once_with(10, 2)


@linux_only
def test_read_bytes_no_fd():
    vcp = LinuxVCP(0)
    with pytest.raises(VCPIOError, match="no open file descriptor"):
        vcp.read_bytes(1)


@linux_only
def test_read_bytes_os_error():
    vcp = open_vcp()
    with mock.patch.object(vcp_linux.os, "read", side_effect=OSError()):
        with pytest.raises(VCPIOError, match="unable to read"):
            vcp.read_bytes(1)


@linux_only
def test_write_bytes_success():
    vcp = LinuxVCP(0)
    vcp.fd = 10
    with mock.patch.object(vcp_linux.os, "write") as m_write:
        vcp.write_bytes(b"xy")
    m_write.assert_called_once_with(10, b"xy")


@linux_only
def test_write_bytes_no_fd():
    vcp = LinuxVCP(0)
    with pytest.raises(VCPIOError, match="no open file descriptor"):
        vcp.write_bytes(b"x")


@linux_only
def test_write_bytes_os_error():
    vcp = LinuxVCP(0)
    vcp.fd = 10
    with mock.patch.object(vcp_linux.os, "write", side_effect=OSError()):
        with pytest.raises(VCPIOError, match="unable write"):
            vcp.write_bytes(b"x")


# ---------------------------------------------------------------------------
# rate_limt
# ---------------------------------------------------------------------------


@linux_only
def test_rate_limt_no_last_set():
    vcp = open_vcp()
    with mock.patch.object(vcp_linux.time, "sleep") as m_sleep:
        vcp.rate_limt()
    m_sleep.assert_not_called()


@linux_only
def test_rate_limt_sleeps_when_recent():
    vcp = open_vcp()
    vcp.last_set = 100.0
    with (
        mock.patch.object(vcp_linux.time, "time", return_value=100.01),
        mock.patch.object(vcp_linux.time, "sleep") as m_sleep,
    ):
        vcp.rate_limt()
    m_sleep.assert_called_once()
    assert m_sleep.call_args[0][0] == pytest.approx(LinuxVCP.CMD_RATE - 0.01)


@linux_only
def test_rate_limt_no_sleep_when_elapsed():
    vcp = open_vcp()
    vcp.last_set = 100.0
    with (
        mock.patch.object(vcp_linux.time, "time", return_value=200.0),
        mock.patch.object(vcp_linux.time, "sleep") as m_sleep,
    ):
        vcp.rate_limt()
    m_sleep.assert_not_called()


# ---------------------------------------------------------------------------
# set_vcp_feature
# ---------------------------------------------------------------------------


@linux_only
def test_set_vcp_feature():
    vcp = open_vcp()
    writes = mock.Mock()
    vcp.write_bytes = writes
    with mock.patch.object(vcp_linux.time, "time", return_value=123.0):
        vcp.set_vcp_feature(0x10, 50)

    data = writes.call_args[0][0]
    assert data[0] == LinuxVCP.HOST_ADDRESS
    assert data[1] == (4 | LinuxVCP.PROTOCOL_FLAG)
    assert data[2] == LinuxVCP.SET_VCP_CMD
    assert data[3] == 0x10
    assert (data[4] << 8) | data[5] == 50
    expected_checksum = LinuxVCP.get_checksum(
        bytearray([LinuxVCP.DDCCI_ADDR << 1]) + bytearray(data[:-1])
    )
    assert data[-1] == expected_checksum
    assert vcp.last_set == 123.0


# ---------------------------------------------------------------------------
# get_vcp_feature
# ---------------------------------------------------------------------------


@linux_only
def test_get_vcp_feature():
    vcp = open_vcp()
    writes = mock.Mock()
    vcp.write_bytes = writes
    header, body = build_get_vcp_reply(0x10, current=50, maximum=100)
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        assert vcp.get_vcp_feature(0x10) == (50, 100)
    writes.assert_called_once()


@linux_only
def test_get_vcp_feature_unexpected_reply_code():
    vcp = open_vcp()
    header, body = build_get_vcp_reply(0x10, 50, 100, reply_code=0x00)
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        with pytest.raises(VCPIOError, match="unexpected response code"):
            vcp.get_vcp_feature(0x10)


@linux_only
def test_get_vcp_feature_unexpected_opcode():
    vcp = open_vcp()
    header, body = build_get_vcp_reply(0x10, 50, 100)
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        with pytest.raises(VCPIOError, match="unexpected opcode"):
            vcp.get_vcp_feature(0x20)


@linux_only
def test_get_vcp_feature_result_code_known():
    vcp = open_vcp()
    header, body = build_get_vcp_reply(0x10, 50, 100, result_code=1)
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        with pytest.raises(VCPIOError, match="Unsupported VCP code"):
            vcp.get_vcp_feature(0x10)


@linux_only
def test_get_vcp_feature_result_code_unknown():
    vcp = open_vcp()
    header, body = build_get_vcp_reply(0x10, 50, 100, result_code=5)
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        with pytest.raises(VCPIOError, match="unknown code"):
            vcp.get_vcp_feature(0x10)


@linux_only
def test_get_vcp_feature_checksum_strict_raises():
    vcp = open_vcp()
    vcp.CHECKSUM_ERRORS = "strict"
    header, body = build_get_vcp_reply(0x10, 50, 100)
    body = body[:-1] + bytes([body[-1] ^ 0xFF])  # corrupt checksum
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        with pytest.raises(VCPIOError, match="checksum"):
            vcp.get_vcp_feature(0x10)


@linux_only
def test_get_vcp_feature_checksum_warning_logs():
    vcp = open_vcp()
    vcp.CHECKSUM_ERRORS = "warning"
    vcp.logger = mock.Mock()
    header, body = build_get_vcp_reply(0x10, 50, 100)
    body = body[:-1] + bytes([body[-1] ^ 0xFF])  # corrupt checksum
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        assert vcp.get_vcp_feature(0x10) == (50, 100)
    vcp.logger.warning.assert_called_once()


# ---------------------------------------------------------------------------
# get_vcp_capabilities
# ---------------------------------------------------------------------------


@linux_only
def test_get_vcp_capabilities():
    vcp = open_vcp()
    header1, body1 = build_caps_packet(b"cap", offset=0)
    header2, body2 = build_caps_packet(b"", offset=3)  # empty payload -> stop
    vcp.read_bytes = mock.Mock(side_effect=[header1, body1, header2, body2])
    with mock.patch.object(vcp_linux.time, "sleep"):
        assert vcp.get_vcp_capabilities() == "cap"


@linux_only
def test_get_vcp_capabilities_bad_length():
    vcp = open_vcp()
    header = bytes([0x6E, 2 | LinuxVCP.PROTOCOL_FLAG])  # length 2 < 3
    body = bytes([0x00, 0x00, 0x00])
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        with pytest.raises(VCPIOError, match="unexpected response length"):
            vcp.get_vcp_capabilities()


@linux_only
def test_get_vcp_capabilities_unexpected_reply_code():
    vcp = open_vcp()
    header, body = build_caps_packet(b"x", offset=0, reply_code=0x00)
    vcp.read_bytes = mock.Mock(side_effect=[header, body])
    with mock.patch.object(vcp_linux.time, "sleep"):
        with pytest.raises(VCPIOError, match="unexpected response code"):
            vcp.get_vcp_capabilities()


@linux_only
def test_get_vcp_capabilities_loop_limit():
    vcp = open_vcp()
    header, body = build_caps_packet(b"x", offset=0)  # never terminates
    vcp.read_bytes = mock.Mock(side_effect=itertools.cycle([header, body]))
    with mock.patch.object(vcp_linux.time, "sleep"):
        with pytest.raises(VCPIOError, match="incomplete or too long"):
            vcp.get_vcp_capabilities()


# ---------------------------------------------------------------------------
# get_checksum
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "data, checksum",
    [
        (bytearray([0x6E, 0x51, 0x82, 0x01, 0x10]), 0xAC),
        (bytearray([0xF0, 0xF1, 0x81, 0xB1]), 0x31),
        (bytearray([0x6E, 0xF1, 0x81, 0xB1]), 0xAF),
    ],
)
def test_get_checksum(data: bytearray, checksum: int):
    computed = LinuxVCP.get_checksum(data)
    xor = checksum ^ computed
    assert computed == checksum, (
        f"computed=0x{computed:02X} 0b{computed:08b} "
        f"checksum=0x{checksum:02X} 0b{checksum:08b} "
        f"xor=0x{xor:02X} 0b{xor:08b}"
    )
