import pytest
from monitorcontrol.vcp import vcp_codes
from monitorcontrol.vcp.vcp_codes import VCPCode


VCP_CODES = [
    vcp_codes.image_factory_default,
    vcp_codes.image_luminance,
    vcp_codes.image_contrast,
    vcp_codes.image_color_preset,
    vcp_codes.active_control,
    vcp_codes.input_select,
    vcp_codes.image_orientation,
    vcp_codes.display_power_mode,
]


@pytest.mark.parametrize("vcp_code", VCP_CODES)
def test_type(vcp_code: VCPCode):
    assert vcp_code.type in ("rw", "ro", "wo")


@pytest.mark.parametrize("vcp_code", VCP_CODES)
def test_function(vcp_code: VCPCode):
    assert vcp_code.function in ("c", "nc", "t")


@pytest.mark.parametrize("vcp_code", VCP_CODES)
def test_repr(vcp_code: VCPCode):
    repr(vcp_code)


@pytest.mark.parametrize("vcp_code", VCP_CODES)
def test_str(vcp_code: VCPCode):
    repr(vcp_code)


@pytest.mark.parametrize(
    "test_type, readable", [("ro", True), ("wo", False), ("rw", True)]
)
def test_readable(test_type: str, readable: bool):
    code = vcp_codes.image_luminance
    code.type = test_type
    assert code.readable == readable


@pytest.mark.parametrize(
    "test_type, writeable", [("ro", False), ("wo", True), ("rw", True)]
)
def test_writeable(test_type: str, writeable: bool):
    code = vcp_codes.image_luminance
    code.type = test_type
    assert code.writeable == writeable
