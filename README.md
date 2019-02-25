# pymonitorcontrol

[![Build Status](https://travis-ci.org/newAM/pymonitorcontrol.svg?branch=master)](https://travis-ci.org/newAM/pymonitorcontrol)
[![Coverage Status](https://coveralls.io/repos/github/newAM/pymonitorcontrol/badge.svg?branch=master)](https://coveralls.io/github/newAM/pymonitorcontrol?branch=master)

Python monitor control using the VESA Monitor Control Command Set (MCCS) over Display Data Channel Command Interface Standard (DDC-CI).

# Supported Platforms
* Linux
* Windows

The Virtual Control Panel (VCP) is re-implemented once per platform.

# Installation
Clone (or download) and install the package.
```
git clone https://github.com/newAM/pymonitorcontrol.git
python3 setup.py install
```

# Usage
Example using context manager:
```Python
from pymonitorcontrol import get_monitors

for monitor in get_monitors():
    with monitor as m:
        # set backlight luminance to 100%
        m.luminance = 100
```

Example using open and close:
```Python
from pymonitorcontrol import get_monitors, VCPError

for monitor in get_monitors():
    try:
        monitor.open()
        # put monitor in standby mode
        monitor.power_mode = "standby"
    except VCPError:
        print("uh-oh")
        raise
    finally:
        monitor.close()
```

# Known Problems
* Will not work on Windows if you have more than one physical monitor per handle.
* Limited command MCCS command implemented, only back-light and power modes are available.  Please open an issue or pull request if you would like additional controls.
