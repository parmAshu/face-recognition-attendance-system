"""
@author : Ashutosh Singh Parmar
@file : admin.py
@brief : This file contains APIs for managing admin credentials
"""

import os, json, base64, hashlib
from Crypto import Cipher
from Crypto.Cipher import AES

ATT_SERVER_PATH = os.environ["ATT_SERVER_PATH"]

KEY = os.environ["ADMIN_KEY"].encode()
IV = os.environ["ADMIN_IV"].encode()

# IN FINAL VERSION THESE THREE VARIABLES WILL BE POPULATED USING THEIR COUNTERPARTS FROM THE OS ENVIRONMENT
DB_FILE = ATT_SERVER_PATH + "/data/admin.cred"

admin_username = None
admin_password = None

def getAdminCredentials():
    """
    This function returns the admin username and password

    PARAMETERS
    ----------
    NONE

    RETURNS
    -------
    ( username, password )
    """
    global admin_username, admin_password
    
    if not admin_username or not admin_password:
        with open(DB_FILE) as fl:

            # 'data' contains base64 encoded strings
            data = fl.read()

            # 'data' contains decoded data
            data = base64.b64decode( data.encode() )

            # decrypting data
            cipher = AES.new(KEY, AES.MODE_CBC, IV)
            data = cipher.decrypt(data)

            # obtaining the length of string
            lt = data[0] | ( (data[1] << 8 ) & 0xff00 )

            # obtaining the json string
            data = data[2:2+lt].decode()

            # obtaining the json object
            data = json.loads(data)

            admin_username = data["username"]
            admin_password = data["password"]
    
    return (admin_username, admin_password)

def setAdminCredentials(usr, pwd):
    """
    This function is used to update admin username and password

    PARAMETERS
    ----------
    usr : username string
    pwd : password string

    RETURNS
    -------
    NOTHING
    """
    global admin_username, admin_password

    if len(pwd) < 8 and len(pwd) <= 64:
        return False

    # The json object
    data = {}
    data['username'] = usr
    data['password'] = pwd

    # The json string
    data = json.dumps(data)
    
    # Converting to bytes array
    data = data.encode()

    # Length of the data bytes
    lt = len(data)

    # Adding the length information
    data = lt.to_bytes(2, 'little') + data

    # Padding
    pad_num = len(data) % 16
    if pad_num:
        data = data + (16-pad_num) * b"P"

    # Encrypting data
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    data = base64.b64encode((cipher.encrypt(data))).decode()

    try:
        with open(DB_FILE, 'w') as fl:
            fl.write( json.dumps(data) )
        
        admin_username = usr
        admin_password = pwd
        return True
    except:
        return False

try:
    fl = open(DB_FILE)
    fl.close()
except:
    setAdminCredentials('admin', 'password')