import os

CURRENT_DIR = os.getcwd()

AICAM_PATH = CURRENT_DIR[0:CURRENT_DIR.index("/interface")] + "/aicam"
INTERFACE_PATH = CURRENT_DIR[0:CURRENT_DIR.index("/setup")] + "/src"

SERVICE_FILE_DATA = """
[Unit]
Description=SIU interface service
After=network.target
After=NetworkManager.service
Requires=NetworkManager.service

[Service]
Environment=PYTHONPATH={%pythonpath%}
Environment=AICAM_PATH={%aicam_path%}
ExecStart=/usr/bin/python3 {%script%}

[Install]
WantedBy=multi-user.target
"""

ENV_VARS_DATA = """
export PYTHONPATH={%pythonpath%}
export AICAM_PATH={%aicam_path%}
"""

with open("interface.service", "w") as fl:
    fl.write( SERVICE_FILE_DATA.replace( "{%pythonpath%}", INTERFACE_PATH ).replace( "{%script%}", INTERFACE_PATH+"/app.py" ).replace( "{%aicam_path%}", AICAM_PATH ) )

with open("env_vars.sh", "w" ) as fl:
    fl.write( ENV_VARS_DATA.replace( "{%pythonpath%}", INTERFACE_PATH ).replace( "{%aicam_path%}", AICAM_PATH ) )