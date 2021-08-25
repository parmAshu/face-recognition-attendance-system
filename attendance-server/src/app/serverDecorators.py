"""
@author : Ashutosh Singh Parmar
@file : serverDecorator.py
@brief : This file contains decorators used by API handlers 
"""

import os, threading, time, datetime, base64, json, jwt
import traceback
from functools import wraps
from flask import Response, request, make_response, jsonify, Blueprint

from util.exceptions import *


def apiResponse(message, code):
    """
    This function is used to send a response to the client. It is a utility function that acts as wrapper around existing functions.

    PARAMETERS :
    ----------
    message : The message string
    code : The status code

    RETURNS :
    -------
    Response object to be sent back to the client
    """
    return make_response( jsonify( { "message" : message } ), code )

# Binary semaphore for accessing tokens
LOCK = threading.Lock()

def threadSafe(f):
    """
    This decorator is used to make a function thread safe
    """
    @wraps(f)
    def inner(*args, **kwargs):
        global LOCK
        try:
            if not LOCK.acquire(blocking=True, timeout=0.1):
                raise threadError
            res = f( *args, **kwargs )
            LOCK.release()
            return res
        except threadError:
            traceback.print_exc()
            return apiResponse( "something went wrong", 500 )
        except Exception as e:
            traceback.print_exc()
            LOCK.release()
            return apiResponse( "something went wrong", 500 )
    return inner

def block(f):
    """
    This decorator is used to block an API
    """
    @wraps(f)
    def inner( *args, **kwargs ):
        return apiResponse( "not operational", 503 )
    return inner