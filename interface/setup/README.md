# Setup interface for camera devices

The interface unit is a piece of hardware that connects to the computer on the camera device and acts as a human interface device. The necessary software can be installed using the following steps:

# Installing Dependencies

1. Install python3 (if not already installed.)
2. Install `Network-Manager` using the following guide - [installing network manager](nmcli_install.md)

# Deploying Software

1. Now, execute the `generateServiceFile.py` script from the `setup` directory itself.
2. Test the program using the following commands:<br>
`source env_vars.sh`<br>
`python3 <project-path>/interface/src/app.py`
3. If there are any erros then, rectify them before proceeding to the next step.
4. Now move the `interface.service` file to `systemd` service file directory and install the service using following commands:<br>
`systemctl enable interface.service`<br>
`systemctl start interface.service`
