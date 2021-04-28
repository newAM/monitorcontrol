Change Log
##########

`2.4.2`_ 2021-04-27
*******************

Fixed
=====
- Fixed an exception that occured when getting the input source from a
  powered off monitor.


`2.4.1`_ 2021-04-10
*******************

Fixed
=====
- Fixed ``get_input_source`` failing for monitors that set the reserved byte.
- Fixed ``get_input_source`` returning a ``str`` instead of a ``InputSource`` as
  the type hint indicated.

`2.4.0`_ 2021-03-14
*******************

Added
=====
- Added ``--monitor`` optional argument to select a specific monitor for the command
- Added ``--set-input-source`` and ``--get-input-source`` to change monitor input source

`2.3.0`_ 2020-10-07
*******************

Added
=====
- Added ``-v`` / ``--verbose`` argument to the CLI.

Fixed
=====
- Fixed `AttributeError: 'LinuxVCP' object has no attribute 'logger'`

`2.2.0`_ 2020-10-04
*******************

Added
=====
- Added python 3.9 support.

Fixed
=====
- Disabled ``VCPIOErrors`` by default on Linux.

`2.1.1`_ 2020-09-12
*******************

Fixed
=====
- Fixed the ``--version`` command in the CLI.

Added
=====
- Added a changelog.

.. _2.4.2: https://github.com/newAM/monitorcontrol/releases/tag/2.4.2
.. _2.4.1: https://github.com/newAM/monitorcontrol/releases/tag/2.4.1
.. _2.4.0: https://github.com/newAM/monitorcontrol/releases/tag/2.4.0
.. _2.3.0: https://github.com/newAM/monitorcontrol/releases/tag/2.3.0
.. _2.2.0: https://github.com/newAM/monitorcontrol/releases/tag/2.2.0
.. _2.1.1: https://github.com/newAM/monitorcontrol/releases/tag/2.1.1
