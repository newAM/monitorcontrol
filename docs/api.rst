API
***

Monitor
#######
.. automodule:: monitorcontrol.monitor_control
   :members:

Virtual Control Panel
#####################
.. autoexception:: monitorcontrol.vcp.VCPError

.. autoclass:: monitorcontrol.vcp.vcp_abc.VCP

Examples
########

Example using context manager:

.. code:: python

    from monitorcontrol import get_monitors

    for monitor in get_monitors():
        with monitor as m:
            # set backlight luminance to 100%
            m.luminance = 100

Example using open and close:

.. code:: python

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

