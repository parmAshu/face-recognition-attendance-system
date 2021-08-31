"""
@author : Ashutosh Singh Parmar
@file : app/session.py
@brief : This file contains decorators used to make APIs thread safe
"""

import os, traceback, uuid, datetime, jwt
from functools import wraps
from flask import request, Response, redirect, send_file

from serverDecorators import apiResponse

# CONSTANTS ----------------------------------------------------------------------------------------------------------

# This variable will be populated using its conterpart from the environment
AUTH_KEY = os.environ["AUTH_KEY"]

# Maximum number of admin users that can be logged in simultaneously 
MAX_ADMIN = 2

# Token expiry period in minutes
TOKEN_EXPIRY_PERIOD = 30

ATT_SERVER_PATH = os.environ["ATT_SERVER_PATH"]

# --------------------------------------------------------------------------------------------------------------------





# This list will contain currently valid admin token ids
ADMIN = []

# Number of currently logged in admin users
LOGGED_IN_USERS = 0





# UTILITY METHODS ----------------------------------------------------------------------------------------------------------

def generateToken(expiry):
    """
    This function constructs and returns a JWT authentication token

    PARAMETERS
    ----------
    expiry : Time in minutes after which the token will become invalid

    RETURNS
    -------
    JWT TOKEN STRING
    """
    global AUTH_KEY, ADMIN, LOGGED_IN_USERS, MAX_ADMIN

    token = {}
    token["_id"] = str(uuid.uuid4())
    token["iat"] = datetime.datetime.utcnow()
    token["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry)

    return token, jwt.encode(token, AUTH_KEY, algorithm="HS256")

# --------------------------------------------------------------------------------------------------------------------





# DECORATORS ---------------------------------------------------------------------------------------------------------

def authenticate(fun):
    """
    This decorator method is used to authenticate requests
    """
    @wraps(fun)
    def innerFun(*args, **kwargs):
        global AUTH_KEY, ADMIN, LOGGED_IN_USERS, MAX_ADMIN
        try:
            token = request.cookies.get("auth-token")

            jwtToken = token
            tokenObj = jwt.decode( jwtToken, key=AUTH_KEY, algorithms="HS256")

            # check if the id exists in saved ids
            i = 0
            for x in ADMIN:
                if x["_id"] == tokenObj["_id"]:
                    break
                i = i + 1
            else:
                raise Exception

            return fun( *args, token=tokenObj, index=i, **kwargs )
        except Exception as e:
            traceback.print_exc()
            return apiResponse( "authentication required", 401 )
    return innerFun

def authenticatePage(fun):
    """
    This decorator method is used to authenticate requests
    """
    @wraps(fun)
    def innerFun(*args, **kwargs):
        global AUTH_KEY, ADMIN, LOGGED_IN_USERS, MAX_ADMIN
        try:
            token = request.cookies.get("auth-token")

            jwtToken = token
            tokenObj = jwt.decode( jwtToken, key=AUTH_KEY, algorithms="HS256")

            # check if the id exists in saved ids
            i = 0
            for x in ADMIN:
                if x["_id"] == tokenObj["_id"]:
                    break
                i = i + 1
            else:
                raise Exception

            return fun( *args, token=tokenObj, index=i, **kwargs )
        except Exception as e:
            #traceback.print_exc()
            return redirect( "/app/page/login_page.html", 302 )
    return innerFun

def authenticate_util(token):
    """
    This decorator method is used to authenticate requests
    """
    global AUTH_KEY, ADMIN, LOGGED_IN_USERS, MAX_ADMIN
    jwtToken = token
    tokenObj = jwt.decode( jwtToken, key=AUTH_KEY, algorithms="HS256")

    # check if the id exists in saved ids
    for x in ADMIN:
        if x["_id"] == tokenObj["_id"]:
            return True
    
    return False

        

def restrictAdminLogins(f):
    """
    This decorator is used to restrict the number of admin logins
    """
    @wraps(f)
    def inner(*args, **kwargs):
        global AUTH_KEY, ADMIN, LOGGED_IN_USERS, MAX_ADMIN
        if LOGGED_IN_USERS == MAX_ADMIN:
            return apiResponse( "not allowed", 401 )
        return f()
    return inner

def refreshTokens(f):
    """
    This decorator is used to remove expired tokens from the ADMIN list
    """
    @wraps(f)
    def inner(*args, **kwargs):
        global AUTH_KEY, ADMIN, LOGGED_IN_USERS, MAX_ADMIN
        
        to_remove = []

        for token in ADMIN:
            if token["exp"] < (datetime.datetime.utcnow()):
                to_remove.append(ADMIN.index(token))
        
        LOGGED_IN_USERS = LOGGED_IN_USERS - len(to_remove)

        for y in to_remove:
            del( ADMIN[y] )
        
        return f()
    return inner

# DECORATORS ---------------------------------------------------------------------------------------------------------
