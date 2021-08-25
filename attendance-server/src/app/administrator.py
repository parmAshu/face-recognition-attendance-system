"""
@author : Ashutosh Singh Parmar
@file : administrator.py
@brief : This file contains admin APIs
"""

import os, sys, traceback, time, datetime, jwt, uuid
from functools import wraps
from flask import request, Response, jsonify, make_response, redirect, send_file, Blueprint
from util import admin as ad

from session import *

# Importing general server decorators
from serverDecorators import *

admin = Blueprint( "admin", __name__ )

# APIs ---------------------------------------------------------------------------------------------------------------

@admin.route('/auth/login', methods=["POST"])
@threadSafe
@refreshTokens
@restrictAdminLogins
def loginHandler(**kwargs):
    """
    This is the login request handler
    """
    global AUTH_KEY, ADMIN, LOGGED_IN_USERS, MAX_ADMIN, TOKEN_EXPIRY_PERIOD

    reqUsername = request.args.get("username")
    reqPassword = request.args.get("password")

    cred = ad.getAdminCredentials()

    if reqUsername == cred[0] and reqPassword == cred[1]:
        authToken, authjwt = generateToken(TOKEN_EXPIRY_PERIOD)
        ADMIN.append( authToken )
        LOGGED_IN_USERS = LOGGED_IN_USERS + 1

        resp = apiResponse( "success", 200 )
        resp.set_cookie( "auth-token", authjwt, httponly=True )
        return resp
    else:
        return apiResponse( "invalid login credentials", 401 )

@admin.route('/auth/logout', methods=["POST", "GET"])
@threadSafe
@refreshTokens
@authenticatePage
def logoutHandler(**kwargs):
    """
    This API is used to terminate current admin session and log out the admin system
    """
    global AUTH_KEY, ADMIN, LOGGED_IN_USERS, MAX_ADMIN
    
    # delete the user entry
    del(ADMIN[kwargs["index"]])
    LOGGED_IN_USERS = LOGGED_IN_USERS - 1

    return redirect( "/app/page/login_page.html", 302 )

@admin.route('/auth/update/admin/credentials', methods=["POST"])
@threadSafe
@refreshTokens
@authenticate
def updateAdminCredentialsHandler(**kwargs):
    """
    This API is used to update admin credentials
    """
    try:
        data = request.get_json()

        if ad.setAdminCredentials( data["username"], data["password"] ):
            return apiResponse( "updated credentials", 200 )
        else:
            return apiResponse( "credentials not accepted", 401 )
    except Exception as e:
        print(e.__class__)
        return apiResponse( "invalid request", 400 )

# --------------------------------------------------------------------------------------------------------------------
