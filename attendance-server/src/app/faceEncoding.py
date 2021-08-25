import os, sys, traceback, io, pymongo, numpy as np, cv2, pickle, face_recognition as fr
from threading import ThreadError
from functools import wraps
from flask import request, Response, make_response, send_file, jsonify, Blueprint

from util.exceptions import *
from util import database, constants as const

from serverDecorators import *

from session import *

encodings = Blueprint( "encodings", __name__ )

# This variable will be populated using its counterpart from the os environment ----------------------------------------------

ATT_SERVER_PATH = os.environ["ATT_SERVER_PATH"]

ENCODING_FILE_PATH = ATT_SERVER_PATH + "/data/encodings.pickle"

# ----------------------------------------------------------------------------------------------------------------------------

process_status = 0
ThreadObj = None

def generateEncodingFileThread():
    """
    This function will be used to generate the encodings file
    """
    global process_status
    process_status = 1

    try:
        uidList = database.getAllEmployeeID()
        known_faces = []
        known_uids = []
        for uid in uidList:
            # Obtain the employee image
            img = database.getEmployeeImage( uid = uid )

            if img:
                # If the image was obtained , convert the binary image data to numpy ndarray
                image = np.asarray( bytearray(img[0]), dtype="uint8" )
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                faces = fr.face_locations( image )
            
                # Get the face encoding in for the image file
                encoding = fr.face_encodings(image, faces)[0]

                # Append the encodings and uids to the list
                known_faces.append(encoding)
                known_uids.append(uid)
            else:
                # If the image could not be obtained then raise exception which will cause thread to exit
                raise Exception

        # Save to encodings file
        data = { "encodings" : known_faces, "names" : known_uids }
        with open( ENCODING_FILE_PATH, "wb" ) as fl:
            fl.write( pickle.dumps(data) )

        process_status = 0
        return
    except Exception as e:
        process_status = -1
        traceback.print_exc()

def getEncodingFile():
    """
    This API is used to get the raw encoding file data

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    Raw file data
    None : If the file does not exist

    EXCEPTIONS :
    ----------
    ***
    """
    try:
        with open( ENCODING_FILE_PATH, "rb" ) as fl:
            data = fl.read()
        return data
    except Exception as e:
        return None

@encodings.route("/encodingfile/generate", methods=["PUT"] )
@threadSafe
@authenticate
def generateEncodingFileHandler(**kwargs):
    """
    This API is used to generate the encoding file.

    REQUEST :
    -------
    method : PUT
    route : /encodingfile/generate
    authentication : bearer token - jwt
    body : 
    none

    RESPONSE : json
    --------
        {
            "message" : "message string"
        }
    """
    try:
        global ThreadObj

        if ThreadObj and ThreadObj.is_alive():
            return apiResponse( "running", 200 )

        ThreadObj = threading.Thread( target=generateEncodingFileThread )
        ThreadObj.start()

        return apiResponse( "started", 200 )

    except Exception as e:
        return apiResponse( "Something went wrong", 500 )

@encodings.route( "/encodingfile/status", methods=["GET"] )
@threadSafe
@authenticate
def getStatusEncodingFileHandler(**kwargs):
    """
    This API is used to get the status of encoding file generation thread

    REQUEST :
    -------
    method : GET
    route : encodingfile/status
    authentication : bearer token - jwt
    body : none

    RESPONSE : json
    --------
        {
            "message" : "message string"
        }
    """
    global ThreadObj, process_status

    if ThreadObj and ThreadObj.is_alive():
        return apiResponse( "running", 200 )
    elif ThreadObj and not ThreadObj.is_alive():
        if process_status == 0:
            return apiResponse( "stopped", 200 )
        else:
            return apiResponse( "failed while generating file", 200 )
    else:
        return apiResponse( "not available", 200 )