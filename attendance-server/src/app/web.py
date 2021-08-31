"""
@author : Ashutosh Singh Parmar
@file : serverDecorator.py
@brief : This file servers the web application
"""

import os, io, pymongo
from typing import MutableSet
from functools import wraps
from flask import request, Response, make_response, send_file, jsonify, redirect, Blueprint

from util.exceptions import *
from util import database, constants as const

from serverDecorators import *

from session import *

web = Blueprint( "web_app", __name__ )

ATT_SERVER_PATH = os.environ["ATT_SERVER_PATH"]

def checkToken( f ):
    """
    This decorator is used during login page request; if the user has authentication then, home page will be served directly
    """
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            token = request.cookies.get("auth-token")
            if authenticate_util( token ):
                return redirect( "/app/auth/page/home_page.html" )
            else:
                raise Exception
        except Exception as e:
            return f(*args, **kwargs)
    return inner

@web.route( "/app/page/login_page.html", methods=["GET"] )
@checkToken
def getLoginPageHandler( *args, **kwargs ):
    """
    This is used to handle requests for login page
    """
    try:
        return send_file( ATT_SERVER_PATH + "/web-app/html/login_page.html" )
    except Exception as e:
        return apiResponse( "Page not found", 404 )

@web.route( "/app/script/login_page_script.js", methods=["GET"])
def getLoginPageScriptHandler( *args, **kwargs ):
    """
    This handler is used to return login page javascript to the client; it does not require authentication
    """
    try:
        return send_file( ATT_SERVER_PATH + "/web-app/js/login_page_script.js" )
    except Exception as e:
        return apiResponse( "Script not found", 404 )

@web.route( "/app/style/<path>", methods=["GET"] )
def getStylesHandler( path ):
    """
    This handler is used to return stylesheets back to the client; it does not require any authentication
    """
    try:
        return send_file( ATT_SERVER_PATH + "/web-app/css/" + path )
    except Exception as e:
        return apiResponse( "Not found", 404 )

@web.route( "/app/auth/page/<path>", methods=["GET"] )
@threadSafe
@authenticatePage
def getWebPagesHandler( *args, **kwargs ):
    """
    This is used to handle requests for other web-pages

    AUTHENTICATION REQUIRED !
    """
    try:
        return send_file( ATT_SERVER_PATH + "/web-app/html/" + kwargs["path"] )
    except Exception as e:
        return apiResponse( "Page not found", 404 )

@web.route( "/app/auth/script/<path>", methods=["GET"] )
@threadSafe
@authenticatePage
def getScriptsHandler( *args, **kwargs ):
    """
    This is used to handle requests for web-page javascripts

    AUTHENTICATION REQUIRED !
    """
    try:
        return send_file( ATT_SERVER_PATH + "/web-app/js/" + kwargs["path"] )
    except Exception as e:
        return apiResponse( "Script not found", 404 )
