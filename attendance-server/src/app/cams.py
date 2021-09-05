"""
@author : Ashutosh Singh Parmar
@file : app/cams.py
@brief : This file contains aicam related APIs
"""

import io, sys, traceback, pymongo
from functools import wraps
from flask import request, Response, make_response, send_file, jsonify, Blueprint
from pymongo.common import KW_VALIDATORS

from util.exceptions import *
from util import database, constants as const

from serverDecorators import *

from session import *

import faceEncoding

cams = Blueprint( "cams", __name__ )

DEVICES = database.getCameraDevices()


ATT_SERVER_PATH = os.environ["ATT_SERVER_PATH"]

# This variable will be populated using their counterparts from os environment
ENCODING_FILE_PATH = ATT_SERVER_PATH + "/data/encodings.pickle"





# ATTENDANCE API SPECIFIC VALIDATORS -----------------------------------------------------------------------------------------

def prepareDatetime( f ):
    """
    This decorator is used to prepare datetime objects for the request handlers
    """
    @wraps(f)
    def inner(**kwargs):
        try:
            data = request.get_json()
            data_keys = data.keys()

            if "date" in data_keys:
                data["date"] = datetime.datetime.strptime( data["date"], const.DATE_FORMAT ).date()

            if "datetime" in data_keys:
                data["datetime"] = datetime.datetime.strptime( data["datetime"], const.ATTENDANCE_DATETIME_FORMAT )

            if "startdate" in data_keys:
                data["startdate"] = datetime.datetime.strptime( data["startdate"], const.DATE_FORMAT ).date()
                
            if "enddate" in data_keys:
                data["enddate"] = datetime.datetime.strptime( data["enddate"], const.DATE_FORMAT ).date()

            return f(**data)
                
        except ValueError as ve:
            if str(ve).contains("timedata"):
                return apiResponse( "Incorrect datetime format", 400 )
            else:
                return apiResponse( "Invalid request", 400 )
        except Exception as e:
            return apiResponse( "Invalid request", 400 )
    return inner

# ----------------------------------------------------------------------------------------------------------------------------





# DECORATOR FUNCTIONS ---------------------------------------------------------------------------------------------------------

def authenticateDevice(f):
    """
    This decorator is used to authenticate requests from aicam devices
    """
    @wraps(f)
    def inner(**kwargs):
        global DEVICES
        try:
            authKey = request.headers["Auth-Key"]
            
            flag = False
            for d in DEVICES:
                if d["registered"] and d["api key"] == authKey:
                    flag = True
                    break
            
            if not flag:
                return apiResponse( "authentication required", 401 )
            else:
                return f(**kwargs)
            
        except Exception as e:
            return apiResponse( "something went wrong", 500 )
    return inner

# -----------------------------------------------------------------------------------------------------------------------------





# APIs ------------------------------------------------------------------------------------------------------------------------

@cams.route( "/devices/aicam/addone", methods = ["POST"] )
def aicamRegisterDeviceHandler(**kwargs):
    """
    This API is used by an aicam device to register itself with the system

    REQUEST :
    -------
    method : POST
    route : /devices/aicam/addone
    authenticaton : none
    body :  json
        {
            "device_id" : "manufacturer assigned unique device id"
        }

    RESPONSE : json
    --------
    {
        "message" : "message string",
        "device" : 
            {
                "id" : "unique device ID",
                "api key" : "...api key (only if the device is authenticated)..."
                "location" : "...location (only is the device is authenticated)..."
            }
    }
    /OR/
    {
        "message" : "message string"
    }
    """
    try:
        global DEVICES

        # Get the json data from the request
        data = request.get_json()

        # Checking whether the device exists in the database
        thisDevice = None
        for d in DEVICES:
            if d["device_id"] == data["device_id"]:
                thisDevice = d
                break

        if thisDevice and thisDevice["registered"] :
            # The device has already been authorized by the admin
            return make_response( jsonify( { "message" : "already exists" , "device" : { "id" : thisDevice["device_id"], "api-key" : thisDevice["api key"], "location" : thisDevice["location"], "status" : "registered" } } ), 200 )
        elif thisDevice and not thisDevice["registered"] :
            # The device is in the database but not authorized
            return make_response( jsonify( { "message" : "already exists", "device" : { "id" : thisDevice["device_id"], "status" : "unregistered" } } ), 200 )
        else:
            # Save the device in database
            if database.addCameraDevice( device_id = data["device_id"] ):
                DEVICES = database.getCameraDevices()
                return make_response( jsonify( { "message" : "success", "device" : { "id" : data["device_id"], "status" : "unregistered" } } ), 201 )
            else:
                return make_response( jsonify( { "message" : "failed" } ), 500 )
    except Exception as e:
        traceback.print_exc()
        return apiResponse( "Invalid request", 400 )

@cams.route( "/devices/aicam/getencodingfile", methods=["GET"] )
@authenticateDevice
def aicamGetEncodingFileHandler(**kwargs):
    """
    This API is used by an aicam device to obtain the face encoding file from the attendance server

    REQUEST : 
    -------
    method : GET
    route : /devices/aicam/getencodingfile
    authentication : api key
    body : none

    RESPONSE : 
    --------
    The pickle file containing face encoding data
    /OR/
    json : If there is some problem (like the encoding file is not present)
        {
            "message" : "message string"
        }
    """
    try:
        encodingData = faceEncoding.getEncodingFile()
        if not encodingData:
            return apiResponse( "No encoding file exists", 404 )

        return send_file( filename_or_fp=io.BytesIO( encodingData ), attachment_filename="encodings.pickle", as_attachment=True )
    except Exception as e:
        return apiResponse( "Something went wrong", 500 )


@cams.route( "/devices/aicam/authorize", methods=["PATCH"] )
@threadSafe
@authenticate
def aicamAuthorizeHandler( **kwargs ):
    """
    This API is used to authorize an aicam device in the database

    REQUEST :
    -------
    method : PATCH
    route : /devices/aicam/authorize
    authentication : bearer token - jwt
    body : json
        {
            "device_id" : "The unique device id",
        }

    RESPONSE : json
    --------
    {
        "message" : "message string"
    }
    """
    try:
        global DEVICES

        data = {
            "device_id" : request.args.get("device_id")
        }

        dev = None
        for d in DEVICES:
            if d["device_id"] == data["device_id"]:
                dev = d
        
        if not dev:
            return apiResponse( "No such device exists", 400 )

        if dev["registered"]:
            return apiResponse( "Device is already authorized", 200 )
        
        if database.cameraDeviceRegister( device_id = data["device_id"], status = True ):
            DEVICES[ DEVICES.index(dev) ]["registered"] = True
            return apiResponse( "Device authorized", 200 )
        else:
            return apiResponse( "Something went wrong", 500 )
 
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Database Error", 500 )
    except Exception as e:
        print(e)
        return apiResponse( "Invalid request", 400 )

@cams.route( "/devices/aicam/deauthorize", methods=["PATCH"] )
@threadSafe
@authenticate
def aicamDeauthorizeHandler( **kwargs ):
    """
    This API is used to deauthorize an aicam device in the database

    REQUEST :
    -------
    method : PATCH
    route : /devices/aicam/deauthorize
    authentication : bearer token - jwt
    body : json
        {
            "device_id" : "The unique device id",
        }

    RESPONSE : json
    --------
    {
        "message" : "message string"
    }
    """
    try:
        global DEVICES

        data = {
            "device_id" : request.args.get("device_id")
        }

        dev = None
        for d in DEVICES:
            if d["device_id"] == data["device_id"]:
                dev = d
        
        if not dev:
            return apiResponse( "No such device exists", 400 )

        if not dev["registered"]:
            return apiResponse( "Device is already deauthorized", 200 )

        if database.cameraDeviceRegister( device_id = data["device_id"], status = False ):
            DEVICES[ DEVICES.index(dev) ]["registered"] = False
            return apiResponse( "Device deauthorized", 200 )
        else:
            return apiResponse( "Something went wrong", 500 )
 
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Database Error", 500 )
    except Exception as e:
        print(e)
        return apiResponse( "Invalid r9equest", 400 )

@cams.route( "/devices/aicam/updateone/location", methods=["PATCH", "POST"] )
@threadSafe
@authenticate
def aicamUpdateLocationHandler(**kwargs):
    """
    This API is used to update the location of an aicam device, in the database

    REQUEST :
    -------
    methods : PATCH
    route : /devices/aicam/updateone/location
    authentication : bearer token - jwt
    body : json
        {
            "device_id" : "The unique device id",
            "location" : "The device location"
        }

    RESPONSE : json
    --------
        {
            "message" : "message string"
        }
    """
    try:

        data = request.get_json()

        dev = None
        for d in DEVICES:
            if d["device_id"] == data["device_id"]:
                dev = d
        
        if not dev:
            return apiResponse( "No such device exists", 400 )

        if database.updateCameraDeviceLocation( device_id = data["device_id"], location = data["location"] ):
            DEVICES[ DEVICES.index(dev) ]["location"] = data["location"]
            return apiResponse( "Location updated", 200 )
        else :
            return apiResponse( "Something went wrong", 500 )
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except Exception as e:
        return apiResponse( "Invalid request", 500 )

@cams.route( "/devices/aicam/getall", methods=["GET"] )
@threadSafe
@authenticate
def aicamGetDetailsAll(**kwargs):
    """
    This API is used to get the details of all aicam devices in the database

    REQUEST :
    -------
    method : PATCH
    route : /devices/aicam/getall
    authentication : bearer token - jwt
    body : none

    RESPONSE : json
    --------
    {
        "message" : "done",
        "devices" : [
            .
            .
            .
        ]
    }
    /OR/
    {
        "message" : "message string"
    }
    """
    try:
        global DEVICES
        return make_response( jsonify( {"message" : "done", "devices" : DEVICES } ), 200 )
    except Exception as e:
        return apiResponse( "something went wrong", 500 )

@cams.route( "/devices/aicam/removeone", methods=["DELETE"] )
@threadSafe
@authenticate
def aicamRemoveDeviceHandler(**kwargs):
    """
    This API is used to remove an aicam device from the database

    REQUEST :
    -------
    method : DELETE
    route : /devices/aicam/removeone
    authentication : bearer token - jwt
    body : json
        {
            "device_id" : "unique device id"
        }

    RESPONSE : json
    --------
    {
        "message" : "message string"
    }
    """
    try:

        #data = request.get_json()
        data = {
            "device_id" : request.args.get( "device_id" )
        }
        
        dev = None
        for d in DEVICES:
            if d["device_id"] == data["device_id"]:
                dev = d
        
        if not dev:
            return apiResponse( "No such device exists", 400 )

        if database.removeCameraDevice( device_id = data["device_id"] ):
            del(DEVICES[ DEVICES.index(dev) ])
            return apiResponse( "Deleted", 200 )
        else :
            return apiResponse( "Something went wrong", 500 )
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except Exception as e:
        return apiResponse( "Invalid request", 500 )


@cams.route( "/devices/aicam/markattendance/one", methods=["POST"] )
@authenticateDevice
@prepareDatetime
def aicamMarkAttendanceHandler(**kwargs):
    """
    This API is used to mark the attendance of an employee

    REQUEST :
    -------
    method : POST
    route : /attendance/markone
    authentication : api key
    body : json
        {
            "uid" : "the employee id"
            "datetime" : "local datetime in ISO format"
        }
    
    RESPONSE : json
    --------
        {
            "message" : "message string"
        }
    """
    try:

        if not database.dateExists( date=kwargs["datetime"].date() ) and not database.addDate( date=kwargs["datetime"].date() ):
            raise Exception

        if kwargs["datetime"].date() > datetime.date.today():
            raise InvalidDateError

        if not database.markAttendance( uid=kwargs["uid"], datetime=kwargs["datetime"] ):
            raise Exception

        return apiResponse( "Attendance marked", 200 )
    
    except KeyError as ke:
        print(ke)
        return apiResponse( "Invalid request parameters", 400 )
    except InvalidDateError:
        return apiResponse( "Invalid date", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except UIDNotExistsError:
        return apiResponse( "No employee with given UID was found", 400 )
    except DuplicateAttendanceError:
        return apiResponse( "Already marked", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Database Error", 500 )
    except Exception as e:
        print( traceback.print_exc() )
        return apiResponse( "Something went wrong", 500 )

# -----------------------------------------------------------------------------------------------------------------------------
