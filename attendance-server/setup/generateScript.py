import os, secrets

CURRENT_DIR = os.getcwd()

temp = CURRENT_DIR.index( "/setup" )
ATT_SERVER_PATH = CURRENT_DIR[0:temp]

ATT_SERVER_PATH = ATT_SERVER_PATH + "/src/app"

try:
    os.remove( ATT_SERVER_PATH+"/data/admin.cred" )
    os.remove( ATT_SERVER_PATH+"/data/dbinit.emt" )
    os.remove( ATT_SERVER_PATH+"/data/encodings.pickle" )
except:
    pass

with open( "env_vars.sh", "w" ) as fl:
    fl.write( "export ATT_SERVER_PATH="+ATT_SERVER_PATH+"\n" )
    fl.write( "export MONGODB_URL=localhost\n" )
    fl.write( "export MONGODB_PORT=27017\n")
    fl.write( "export ADMIN_KEY=" + secrets.token_urlsafe(16)[0:16]+"\n" )
    fl.write( "export ADMIN_IV=" + secrets.token_urlsafe(16)[0:16]+"\n" )
    fl.write( "export AUTH_KEY=" + secrets.token_urlsafe(32)[0:32]+"\n" )
    fl.write( "export FLASK_APP="+ATT_SERVER_PATH+"\n" )
    fl.write( "export PYTHONPATH="+ATT_SERVER_PATH+"\n" )
