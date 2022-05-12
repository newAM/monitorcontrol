import pytest
from monitorcontrol.vcp.vcp_linux import LinuxVCP


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
