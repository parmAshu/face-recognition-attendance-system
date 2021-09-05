import os, secrets

CURRENT_DIR = os.getcwd()

ind = CURRENT_DIR.index( "/setup" )
AICAM_PATH = CURRENT_DIR[0:ind]
AICAM_PATH = AICAM_PATH + "/src"

ATTENDANCE_SERVER_URL = "http://localhost"
UNIQUE_ID = secrets.token_urlsafe(64)[0:64]
PYTHONPATH = AICAM_PATH

SERVICE_FILE_DATA = """
[Unit]
Description=aicam service
After=network.target
After=NetworkManager.service
Requires=NetworkManager.service

[Service]
Environment=AICAM_PATH={%aicam_path%}
Environment=ATTENDANCE_SERVER_URL={%attendance_server_url%}
Environment=UNIQUE_ID={%unique_id%}
Environment=PYTHONPATH={%pythonpath%}
ExecStart=/usr/bin/python3 {%script%}

[Install]
WantedBy=multi-user.target
"""

ENV_VARS_DATA = """
export AICAM_PATH={%aicam_path%}
export ATTENDANCE_SERVER_URL={%attendance_server_url%}
export UNIQUE_ID={%unique_id%}
export PYTHONPATH={%pythonpath%}
"""

# Create the data directory
try:
    os.mkdir( AICAM_PATH + "/data" )
except:
    pass

# Remove the previous data files
try:
    os.remove( AICAM_PATH + "/data/encoding.pickle" )
    os.remove( AICAM_PATH + "/data/status.json" )
except:
    pass

with open( "aicam.service", "w" ) as fl:
    fl.write( SERVICE_FILE_DATA.replace( "{%aicam_path%}", AICAM_PATH ).replace( "{%attendance_server_url%}", ATTENDANCE_SERVER_URL ).replace( "{%unique_id%}", UNIQUE_ID ).replace( "{%pythonpath%}", PYTHONPATH ).replace( "{%script%}", AICAM_PATH + "/app.py" ) )

with open( "env_vars.sh", "w" ) as fl:
    fl.write( ENV_VARS_DATA.replace( "{%aicam_path%}", AICAM_PATH ).replace( "{%attendance_server_url%}", ATTENDANCE_SERVER_URL ).replace( "{%unique_id%}", UNIQUE_ID ).replace( "{%pythonpath%}", PYTHONPATH ) )
    