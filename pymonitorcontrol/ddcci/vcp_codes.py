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

import voluptuous as vol
from typing import Dict, Type


class VCPCode:

    # incomplete list of VCP codes from the MCSS specification
    VCP_CODE_DEFINTIONS = {
        "image_factory_default": {
            "name": "restore factory default image",
            "value": 0x04,
            "type": "wo",
            "function": "nc",
        },
        "image_luminance": {
            "name": "image luminance",
            "value": 0x10,
            "type": "rw",
            "function": "c",
        },
        "active_control": {
            "name": "active control",
            "value": 0x52,
            "type": "ro",
            "function": "nc",
        },
        "image_orientation": {
            "name": "image orientation",
            "value": 0xAA,
            "type": "ro",
            "function": "nc",
        },
        "display_power_mode": {
            "name": "display power mode",
            "value": 0xD6,
            "type": "rw",
            "function": "nc",
        },
    }

    VCP_CODE_SCHEMA = vol.Schema({
        vol.Required("name"): str,
        vol.Required("value"): int,
        vol.Required("type"): vol.Any("rw", "ro", "wo"),
        vol.Required("function"): vol.Any("c", "nc", "t"),
    })

    def __init__(self, definition: Dict):
        """
        Args:
            definition: code definition dictionary
        """
        self.definition = definition

    def __repr__(self):
        return (
            "virtual control panel code definition. "
            f"value: {self.value} "
            f"type: {self.type}"
            f"function: {self.function}"
        )

    def validate(self):
        """
        Validates the definition schema.

        Raises:
            voluptuous.Error: code does not match the schema
        """
        self.VCP_CODE_SCHEMA(self.definition)

    @property
    def name(self)-> int:
        """ Friendly name of the code. """
        return self.definition["name"]

    @property
    def value(self)-> int:
        """ Value of the code. """
        return self.definition["value"]

    @property
    def type(self) -> str:
        """ Type of the code. """
        return self.definition["type"]

    @property
    def function(self)-> str:
        """ Function of the code. """
        return self.definition["function"]

    @property
    def readable(self) -> bool:
        """ Returns true if the code can be read. """
        if self.type == "wo":
            return False
        else:
            return True

    @property
    def writeable(self) -> bool:
        """ Returns true if the code can be written. """
        if self.type == "ro":
            return False
        else:
            return True


def get_vcp_code_definition(name: str) -> Type[VCPCode]:
    """
    Gets a code from the dictionary.

    Args:
        name: name of the VCP code definition

    Returns:
        VCPCode class

    Raises:
        KeyError: unable to locate VCP code
    """
    return VCPCode(VCPCode.VCP_CODE_DEFINTIONS[name])
