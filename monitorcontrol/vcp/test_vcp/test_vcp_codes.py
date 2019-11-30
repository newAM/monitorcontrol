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

import pytest
import voluptuous as vol
from ..vcp_codes import VCPCode, get_vcp_code_definition


VCP_CODE_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required("value"): int,
        vol.Required("type"): vol.Any("rw", "ro", "wo"),
        vol.Required("function"): vol.Any("c", "nc", "t"),
    }
)


@pytest.fixture(scope="module", params=VCPCode._VCP_CODE_DEFINTIONS.keys())
def vcp_definition(request):
    return get_vcp_code_definition(request.param)


def test_vcp_code_schema(vcp_definition):
    VCP_CODE_SCHEMA(vcp_definition.definition)


@pytest.mark.parametrize("property", ["name", "value", "type", "function"])
def test_properties(vcp_definition, property):
    getattr(vcp_definition, property)


def test_repr(vcp_definition):
    repr(vcp_definition)


@pytest.mark.parametrize(
    "test_type, readable", [("ro", True), ("wo", False), ("rw", True)]
)
def test_readable(test_type, readable):
    code = VCPCode({"type": test_type})
    assert code.readable == readable


@pytest.mark.parametrize(
    "test_type, writeable", [("ro", False), ("wo", True), ("rw", True)]
)
def test_writeable(test_type, writeable):
    code = VCPCode({"type": test_type})
    assert code.writeable == writeable


def test_properties_value():
    """ Test that dictionary values propagate to properties. """
    test_name = "unit test"
    test_value = 0x123456789
    test_type = "unit test type"
    test_function = "unit test value"
    test_definition = {
        "name": test_name,
        "value": test_value,
        "type": test_type,
        "function": test_function,
    }
    code = VCPCode(test_definition)
    assert code.name == test_name
    assert code.value == test_value
    assert code.type == test_type
    assert code.function == test_function
