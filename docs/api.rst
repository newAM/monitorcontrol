API
###

Monitor
*******
.. automodule:: monitorcontrol.monitorcontrol
   :members:

Virtual Control Panel
*********************
.. autoexception:: monitorcontrol.vcp.VCPError

.. autoexception:: monitorcontrol.vcp.VCPIOError

.. autoexception:: monitorcontrol.vcp.VCPPermissionError

.. autoclass:: monitorcontrol.vcp.vcp_abc.VCP

Checksum Behaviour
==================

By default if a monitor responds with a bad checksum this will be ignored on
Windows, this is not controlable by the user.

To maintain consistentency across platforms checksums are disabled on Linux by
default as well (see `issue #5`_).

The behaviour of incorrect checksums on Linux can be set with the static class
variable ``monitorcontrol.vcp.vcp_linux.LinuxVCP.CHECKSUM_ERRORS``.

* ``"ignore"`` (default) ignore checksum errors.
* ``"strict"`` raise a :py:class:`~monitorcontrol.vcp.VCPIOError`.
* ``"warning"`` log a warning.

.. _issue #5: https://github.com/newAM/monitorcontrol/issues/5
