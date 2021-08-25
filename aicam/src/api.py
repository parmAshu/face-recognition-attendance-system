"""
@author : Ashutosh Singh Parmar
@file : aicam/api.py
@description : This file contains utility methods that are used to access the attendance server APIs
"""
import os, io, json, requests

import constants as const

ATTENDANCE_SERVER = os.environ["ATTENDANCE_SERVER_URL"]

REGISTER_URL = ATTENDANCE_SERVER + "/devices/aicam/addone"

GET_FILE_URL = ATTENDANCE_SERVER + "/devices/aicam/getencodingfile"

MARK_ATTENDANCE_URL = ATTENDANCE_SERVER + "/devices/aicam/markattendance/one"

def register( **kwargs ):
    """
    This method is used to register the device with the attendance server.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be provided as keyworded arguments
    ----------
    id : The unique device id

    RETURNS : dict
    -------
    {
        "status" : "unauthorized/authorized/failed",
        "api-key" : "...key..." (ONLY WHEN THE DEVICE HAS BEEN AUTHORIZED)
        "location" : "...assigned device location..." (ONLY WHEN THE DEVICE HAS BEEN AUTHORIZED)
    }

    EXCEPTIONS : 
    ----------
    """

    payload = json.dumps({ "device_id": kwargs["id"] } )

    Headers = { 'Content-Type': 'application/json' }

    response = requests.request("POST", REGISTER_URL, headers=Headers, data=payload )

    response = response.json()

    response_msg = response["message"]
    
    if response_msg == "invalid request" or response_msg == "failed":
        return { "status" : "failed" }
    elif response_msg == "success" or (response_msg == "already exists" and response["device"]["status"] == "unregistered"):
        return { "status" : "unauthorized" }
    else:
        return { "status" : "authorized", "api-key" : response["device"]["api-key"], "location" : response["device"]["location"]}

def getEncodingFile( **kwargs ):
    """
    This method is used to obtain the face encodings file from the attendance server.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be provided as keyworded arguments
    ----------
    key : The api key given to the device by the attendance server

    RETURNS : dict
    -------
    {
        "message" : "success/failed",
        "encoding-file" : The binary encoding file (ONLY WHEN API RETURNS IT)
    }

    EXCEPTIONS :
    ----------
    ***
    """
        
    payload={}
    
    headers = { 'Auth-Key': kwargs["key"] }

    response = requests.request( "GET", GET_FILE_URL, headers=headers, data=payload )

    if response.status_code == 200:
        return { "message" : "success", "encoding-file" : response.content }
    else:
        return { "message" : "failed" }

def markAttendance( **kwargs ):
    """
    This method is used to mark the attendance of an employee

    PARAMETERS : The following parameters are NOT OPTIONAL and must be provided as keyworded arguments.
    ----------
    uid : The employee UID
    time : The datetime object corresponding to the attendance
    key : The authentication key provided to the device by the attendance server

    RETURNS : 
    -------
    1 : Success
    2 : Already marked
    -1 : Failed
    -2 : Invalid UID
    -3 : Invalid Datetime
    """
    payload = json.dumps({ "uid": kwargs["uid"], "datetime": kwargs["time"].strftime(const.ISO_DATETIME_FORMAT) })

    headers = { 'Auth-Key': kwargs["key"], 'Content-Type': 'application/json' }

    response = requests.request( "POST", MARK_ATTENDANCE_URL, headers=headers, data=payload )

    response = response.json()

    if response["message"] == "Attendance marked":
        return 1
    elif response["message"] == "Already marked":
        return 2
    elif response["message"] == "Invalid UID":
        return -2
    elif response["message"] == "Invalid date":
        return -3
    else:
        return -1


def display( uid_list ):
    """
    This method is used to display a list of uids on the attached display screen

    PARAMETERS :
    ----------
    uid_list : A list of uids to display

    RETURNS :
    -------
    NOTHING
    """
    pass