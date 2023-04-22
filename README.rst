monitorcontrol
##############

|PyPi Version| |Build Status| |Documentation Status| |Coverage Status| |Black|

Python monitor control using the VESA Monitor Control Command Set (MCCS)
over the Display Data Channel Command Interface Standard (DDC-CI).

Supported Platforms
*******************
-  Linux (tested with NixOS)
-  Windows (tested with Windows 10)

Windows Install
***************

.. code-block:: bash

   py -3 -m pip install monitorcontrol

Linux Install
*************

.. code-block:: bash

   python3 -m pip install monitorcontrol

Documentation
*************

Full documentation including examples are avaliable in the `docs <https://newam.github.io/monitorcontrol>`__.

.. |PyPi Version| image:: https://badge.fury.io/py/monitorcontrol.svg
   :target: https://badge.fury.io/py/monitorcontrol
.. |Build Status| image:: https://github.com/newAM/monitorcontrol/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/newAM/monitorcontrol/actions/workflows/ci.yml
.. |Coverage Status| image:: https://coveralls.io/repos/github/newAM/monitorcontrol/badge.svg?branch=master
   :target: https://coveralls.io/github/newAM/monitorcontrol?branch=master
.. |Documentation Status| image:: https://img.shields.io/badge/docs-latest-blue
   :target: https://newam.github.io/monitorcontrol
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
