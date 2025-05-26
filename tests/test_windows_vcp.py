import pytest
from unittest.mock import patch


from monitorcontrol.vcp.vcp_windows import WindowsVCP


@pytest.mark.parametrize(
    "monitor_input, expected",
    [
        [[1], ["1-0"]],
        [[2], ["2-0", "2-1"]],
        [[1, 2], ["1-0", "2-0", "2-1"]],
        [[1, 3], ["1-0", "3-0", "3-1", "3-2"]],
    ],
)
@patch("monitorcontrol.vcp.vcp_windows.WindowsVCP._get_hmonitors")
@patch("monitorcontrol.vcp.vcp_windows.WindowsVCP._physical_monitors_from_hmonitor")
def test_get_physical_monitors(
    physical_monitors_from_hmonitor, get_hmonitors, monitor_input, expected
):
    get_hmonitors.return_value = monitor_input
    physical_monitors = {
        1: ["1-0"],
        2: ["2-0", "2-1"],
        3: ["3-0", "3-1", "3-2"],
    }
    physical_monitors_from_hmonitor.side_effect = (
        lambda hmonitor: physical_monitors.get(hmonitor)
    )
    result = list(WindowsVCP._get_physical_monitors())
    assert result == expected
