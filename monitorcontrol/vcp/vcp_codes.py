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


# incomplete list of VCP codes from the MCSS specification
_VCP_CODE_DEFINTIONS = {
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
    "image_contrast": {
        "name": "image contrast",
        "value": 0x12,
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


class VCPCode:
    """
    Virtual Control Panel code.  Simple container for the control
    codes defined by the VESA Monitor Control Command Set (MCSS).

    This should be used by getting the code from
    :py:meth:`get_vcp_code_definition()`

    Args:
        name: VCP code name.

    Raises:
        KeyError: VCP code not found.
    """

    def __init__(self, name: str):
        self.definition = _VCP_CODE_DEFINTIONS[name]

    def __repr__(self) -> str:
        return (
            "virtual control panel code definition. "
            f"value: {self.value} "
            f"type: {self.type}"
            f"function: {self.function}"
        )

    @property
    def name(self) -> int:
        """ Friendly name of the code. """
        return self.definition["name"]

    @property
    def value(self) -> int:
        """ Value of the code. """
        return self.definition["value"]

    @property
    def type(self) -> str:
        """ Type of the code. """
        return self.definition["type"]

    @property
    def function(self) -> str:
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
