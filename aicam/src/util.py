"""
@author : Ashutosh Singh Parmar
@file : aicam/util.py
@brief : This file contains various utility functions
"""
import json, traceback

import constants as const

try:
    with open( const.STATUS_FILE ) as fl:
        STATUS = json.loads( fl.read() )
except:
    with open( const.STATUS_FILE, "w" ) as fl:
        fl.write( json.dumps( const.STATUS_FILE_INIT_DATA ) )
    STATUS = const.STATUS_FILE_INIT_DATA

def deviceAuthorized():
    """
    This method is used to get the current status of the aicam device

    PARAMETERS :
    ----------
    NONE

    RETURNS : 
    -------
    True : If the device is authorized and has an api-key
    False : Otherwise
    """
    global STATUS
    return STATUS["authorized"]

def getApiKey():
    """
    This method is used to get the saved api key

    PARAMETERS :
    ----------
    NONE

    RETURNS : 
    -------
    The api key 
    /OR/
    None
    """
    global STATUS
    
    if len(STATUS["api-key"]):
        return STATUS["api-key"]
    else:
        return None

def hasEncodingFile():
    """
    This method is used to check whether the device has an encoding file or not

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    True/False
    """
    global STATUS
    return STATUS["has-file"]

def setAuthStatus( **kwargs ):
    """
    This method is used to set the status of the device

    PARAMETERS : The following parameters are NOT OPTIONAL and must be provided as keyworded arguments
    ----------
    authorized : True/False
    key : The api key given to the device by the attendance server ( ONLY WHEN authorized is true )

    RETURNS :
    -------
    True : Success
    False : Otherwise
    """
    global STATUS
    try:
        status_temp = STATUS

        status_temp["authorized"] = kwargs["authorized"]

        if status_temp["authorized"]:
            if not len(kwargs["key"]):
                raise Exception
            status_temp["api-key"] = kwargs["key"]
        else:
            status_temp["api-key"] = ""
            status_temp["has-file"] = False

        with open( const.STATUS_FILE, "w" ) as fl:
            fl.write( json.dumps(status_temp) )

        STATUS = status_temp

        return True
    except Exception as e:
        return False

def setFileStatus( **kwargs ):
    """
    This method is used to set the encoding file status

    PARAMETERS :
    ----------
    has_file : True/False

    RETURNS :
    -------
    True : Success
    False : Failure
    """ 
    global STATUS

    try:
        status_temp = STATUS

        if kwargs["has_file"] and not status_temp["authorized"] :
            return False
        
        status_temp["has-file"] = kwargs["has_file"]

        with open(const.STATUS_FILE, "w") as fl:
            fl.write( json.dumps(status_temp) )

        STATUS = status_temp
        
        return True
    except Exception as e:
        #traceback.print_exc()
        return False