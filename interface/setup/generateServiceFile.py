import os

CURRENT_DIR = os.getcwd()

ind = CURRENT_DIR.index("/setup")
INTERFACE_PATH = CURRENT_DIR[0:ind] + "/src"

SERVICE_FILE_DATA = """
[Unit]
Description=SIU interface service
After=network.target
After=NetworkManager.service
Requires=NetworkManager.service

[Service]
Environment=PYTHONPATH={%pythonpath%}
ExecStart=/usr/bin/python3 {%script%}

[Install]
WantedBy=multi-user.target
"""

with open("interface.service", "w") as fl:
    fl.write( SERVICE_FILE_DATA.replace( "{%pythonpath%}", INTERFACE_PATH ).replace( "{%script%}", INTERFACE_PATH+"/app.py" ) )