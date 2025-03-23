import pytest
import sys
from monitorcontrol.vcp.vcp_windows import WindowsVCP


if sys.platform == "win32":

    @pytest.mark.parametrize(
        "input,expected",
        [
            [[1], ["1-0"]],
            [[2], ["2-0", "2-1"]],
            [[1, 2], ["1-0", "2-0", "2-1"]],
            [[1, 3], ["1-0", "3-0", "3-1", "3-2"]],
        ],
    )
    def test_get_physical_monitors(input, expected):
        physical_monitors = {
            1: ["1-0"],
            2: ["2-0", "2-1"],
            3: ["3-0", "3-1", "3-2"],
        }
        result = list(
            WindowsVCP._get_physical_monitors(
                lambda: input, lambda hmonitor: physical_monitors.get(hmonitor)
            )
        )
        assert result == expected
