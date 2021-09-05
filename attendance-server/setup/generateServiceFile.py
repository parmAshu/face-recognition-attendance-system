import os, secrets, subprocess

CURRENT_DIR = os.getcwd()

temp = CURRENT_DIR.index( "/setup" )
ATT_SERVER_PATH_MAIN = CURRENT_DIR[0:temp]

SERVICE_FILE_DATA = """
[Unit]
Description=Attendance server
After=mongodb.service

[Service]
Environment=PYTHONPATH={%pythonpath%}
Environment=ATT_SERVER_PATH={%att_server_path%}
Environment=MONGODB_URL={%mongodb_url%}
Environment=MONGODB_PORT={%mongodb_port%}
Environment=ADMIN_KEY={%admin_key%}
Environment=ADMIN_IV={%admin_iv%}
Environment=AUTH_KEY={%auth_key%}
Environment=FLASK_APP={%flask_app%}
ExecStart={%program%}

[Install]
WantedBy=multi-user.target
"""

ENV_VARS_DATA = """
export ATT_SERVER_PATH={%att_server_path%}
export MONGODB_URL={%mongodb_url%}
export MONGODB_PORT={%mongodb_port%}
export ADMIN_KEY={%admin_key%}
export ADMIN_IV={%admin_iv%}
export AUTH_KEY={%auth_key%}
export FLASK_APP={%flask_app%}
export PYTHONPATH={%pythonpath%}
"""

ATT_SERVER_PATH = ATT_SERVER_PATH_MAIN + "/src/app"
MONGODB_URL = "localhost"
MONGODB_PORT = "27017"
ADMIN_KEY = secrets.token_urlsafe(16)[0:16]
ADMIN_IV = secrets.token_urlsafe(16)[0:16]
AUTH_KEY = secrets.token_urlsafe(32)[0:32]
FLASK_APP = ATT_SERVER_PATH
PYTHONPATH = ATT_SERVER_PATH
PROGRAM_PATH = subprocess.run( [ "which", "python3" ], capture_output=True ).stdout.decode().strip() + " " + ATT_SERVER_PATH_MAIN + "/src/run.py"

try:
    os.mkdir( ATT_SERVER_PATH+"/data" )
except:
    pass

try:
    os.remove( ATT_SERVER_PATH+"/data/admin.cred" )
    os.remove( ATT_SERVER_PATH+"/data/dbinit.emt" )
    os.remove( ATT_SERVER_PATH+"/data/encodings.pickle" )
except:
    pass

with open( "env_vars.sh", "w" ) as fl:
    fl.write( ENV_VARS_DATA.replace( "{%att_server_path%}", ATT_SERVER_PATH ).replace( "{%mongodb_url%}", MONGODB_URL ).replace( "{%mongodb_port%}", MONGODB_PORT ).replace( "{%admin_key%}", ADMIN_KEY ).replace( "{%admin_iv%}", ADMIN_IV ).replace( "{%auth_key%}", AUTH_KEY ).replace( "{%flask_app%}", FLASK_APP ).replace( "{%pythonpath%}", PYTHONPATH ) )

with open( "attendanceServer.service", "w" ) as fl:
    fl.write( SERVICE_FILE_DATA.replace( "{%att_server_path%}", ATT_SERVER_PATH ).replace( "{%mongodb_url%}", MONGODB_URL ).replace( "{%mongodb_port%}", MONGODB_PORT ).replace( "{%admin_key%}", ADMIN_KEY ).replace( "{%admin_iv%}", ADMIN_IV ).replace( "{%auth_key%}", AUTH_KEY ).replace( "{%flask_app%}", FLASK_APP ).replace( "{%pythonpath%}", PYTHONPATH ).replace( "{%program%}", PROGRAM_PATH ) )
