Linux Setup
###########

If you see no /dev/i2c-* devices, then you may need to load the i2c kernel module.

.. code-block:: bash

   sudo mkdir -p /etc/modules-load.d; echo i2c-dev | sudo tee /etc/modules-load.d/i2c-dev.conf

For most use cases you will not want to run as root to access your monitors,
you can use these commands to enable non-root access for your user.

.. code-block:: bash

    sudo groupadd i2c
    sudo chown :i2c /dev/i2c-*
    sudo usermod -aG i2c $USER
    echo 'KERNEL=="i2c-[0-9]*", GROUP="i2c"' | sudo tee -a /etc/udev/rules.d/10-i2c.rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger

Logout and log back in to reload the groups.
