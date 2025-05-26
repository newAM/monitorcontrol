class VCPCode:
    """
    Virtual Control Panel code.  Simple container for the control
    codes defined by the VESA Monitor Control Command Set (MCCS).

    Args:
        name: VCP code name.
        value: VCP code value.
        code_type: VCP code type.
        function: VCP code function.

    Raises:
        KeyError: VCP code not found.
    """

    def __init__(self, name: str, value: int, code_type: str, function: str):
        self.name = name
        self.value = value
        self.type = code_type
        self.function = function

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.name} {self.value=} {self.type=} {self.function=}"

    @property
    def readable(self) -> bool:
        """Returns true if the code can be read."""
        if self.type == "wo":
            return False
        else:
            return True

    @property
    def writeable(self) -> bool:
        """Returns true if the code can be written."""
        if self.type == "ro":
            return False
        else:
            return True


# incomplete list of VCP codes from the MCCS specification
# please add new codes to the VCP_CODES list in test_vcp_codes.py
image_factory_default = VCPCode(
    name="restore factory default image",
    value=0x04,
    code_type="wo",
    function="nc",
)
image_luminance = VCPCode(
    name="image luminance",
    value=0x10,
    code_type="rw",
    function="c",
)
image_contrast = VCPCode(
    name="image contrast",
    value=0x12,
    code_type="rw",
    function="c",
)
image_color_preset = VCPCode(
    name="image color preset",
    value=0x14,
    code_type="rw",
    function="nc",
)
active_control = VCPCode(
    name="active control",
    value=0x52,
    code_type="ro",
    function="nc",
)
input_select = VCPCode(
    name="input select",
    value=0x60,
    code_type="rw",
    function="nc",
)
image_orientation = VCPCode(
    name="image orientation",
    value=0xAA,
    code_type="ro",
    function="nc",
)
display_power_mode = VCPCode(
    name="display power mode",
    value=0xD6,
    code_type="rw",
    function="nc",
)
