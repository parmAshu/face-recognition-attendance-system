import os, secrets

CURRENT_DIR = os.getcwd()

ind = CURRENT_DIR.index( "/setup" )
AICAM_PATH = CURRENT_DIR[0:ind]

AICAM_PATH = AICAM_PATH + "/src"

try:
    os.remove( AICAM_PATH + "/data/encoding.pickle" )
    os.remove( AICAM_PATH + "/data/status.json" )
except:
    pass

with open( "env_vars.sh", "w" ) as fl:
    fl.write( "export AICAM_PATH="+AICAM_PATH+"\n" )
    fl.write( "export ATTENDANCE_SERVER_URL=http://localhost\n" )
    fl.write( "export UNIQUE_ID=" + secrets.token_urlsafe(64)[0:64]+"\n" )
    fl.write( "export PYTHONPATH=" + AICAM_PATH + "\n" )