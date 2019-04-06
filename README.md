# monitorcontrol

[![PyPi Version](https://badge.fury.io/py/monitorcontrol.svg)](https://badge.fury.io/py/monitorcontrol)
[![Build Status](https://travis-ci.org/newAM/monitorcontrol.svg?branch=master)](https://travis-ci.org/newAM/monitorcontrol)
[![Coverage Status](https://coveralls.io/repos/github/newAM/monitorcontrol/badge.svg?branch=master)](https://coveralls.io/github/newAM/monitorcontrol?branch=master)

Python monitor control using the VESA Monitor Control Command Set (MCCS) over Display Data Channel Command Interface Standard (DDC-CI).

## Supported Platforms
* Linux
* Windows

The Virtual Control Panel (VCP) is re-implemented once per platform.  The monitor class receives a VCP as an argument and uses the VCP for all monitor controls.

## Installation
Simply install with pip.
```
pip3 install monitorcontrol
```

### Manual Installation
Clone (or download) and install the package.
```
git clone https://github.com/newAM/monitorcontrol.git
cd monitorcontrol
python3 setup.py install
```

## Usage
Example using context manager:
```Python
from monitorcontrol import get_monitors

for monitor in get_monitors():
    with monitor as m:
        # set backlight luminance to 100%
        m.luminance = 100
```

Example using open and close:
```Python
from monitorcontrol import get_monitors, VCPError

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

## Known Problems
* Will not work on Windows if you have more than one physical monitor per handle.
* Limited MCCS commands implemented, only back-light and power modes are available.  Please open an issue or pull request if you would like additional controls.

## References
* VESA Monitor Control Command Set Standard Version 2.2a
* Display Data Channel Command Interface Standard Version 1.1
* [Informatic/python-ddcci](https://github.com/Informatic/python-ddcci)
* [siemer/ddcci](https://github.com/siemer/ddcci/)
* [https://stackoverflow.com/a/18065609](https://stackoverflow.com/a/18065609)
