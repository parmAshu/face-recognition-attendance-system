"""
@author : Ashutosh Singh Parmar
@file : aicam/app.py
@brief : This file is the main file for the aicam system
"""
import os, threading, time, cv2, pickle, face_recognition

import constants as const

import api, util, datetime

print("STATE : INITIAL")

if not util.deviceAuthorized():
    while True:
        response = api.register( id = const.UNIQUE_ID )
        if response["status"] == "authorized" and util.setAuthStatus( authorized = True , key = response["api-key"] ):
            print("registered")
            break
        else:
            print("failed")
            time.sleep( 10 )

print("STATE : REGISTERED")

api_key = util.getApiKey()

if not util.hasEncodingFile():
    while True:
        response = api.getEncodingFile( key = api_key )
        if response["message"] == "success":
            with open( const.ENCODING_FILE, "wb" ) as fl:
                fl.write( response["encoding-file"] )
            util.setFileStatus( has_file = True )
            print("got file")
            break
        else:
            print("failed")
            time.sleep( 10 )

get_frames_thread_running = False
camera_frame = None
camera_thread = None

def getFrames():
    """
    This thread fetches frames from the camera and stores them for use by other threads in the program

    PARAMETERS
    ----------
    NONE

    RETURNS
    -------
    NOTHING
    """
    global get_frames_thread_running, camera_frame
    
    get_frames_thread_running = True
    camera = cv2.VideoCapture(0)
    
    try:
        while get_frames_thread_running:
            success, frame = camera.read()
            if success:
                camera_frame = frame
            else:
                raise Exception
    except Exception as e:
        camera.release()
        get_frames_thread_running = False

with open( const.ENCODING_FILE, "rb" ) as fl:
    data = fl.read()
data = pickle.loads( data )

def startCameraThread():
    """
    This method is used to start the camera

    PARAMETERS
    ----------
    NONE

    RETURNS
    -------
    NOTHING
    """
    global camera_thread

    if camera_thread and camera_thread.is_alive():
        return
    
    camera_thread = threading.Thread(target=getFrames, daemon=True)
    camera_thread.start()

def stopCameraThread():
    """
    This method is used to stop the camera thread

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    NOTHING
    """
    global camera_thread, get_frames_thread_running

    if not camera_thread or not camera_thread.is_alive():
        return

    get_frames_thread_running = False

    while camera_thread.is_alive():
        time.sleep(0.1)

def detectFacesAndMarkAttendance():
    """
    This function is used to detect faces in the current camera frame and mark attendance

    PARAMETERS
    ----------
    NONE

    RETURNS :
    -------
    NOTHING
    """
    global camera_frame, camera_thread, data

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if str(type(camera_frame)) == "<class 'NoneType'>" or not camera_thread.is_alive():
        return

    gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)
    rgb = camera_frame
    #rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)

    rects = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5 )
 
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    encodings = face_recognition.face_encodings(rgb, boxes)

    # Iterate over encodings
    for encoding in encodings:

        matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.4 )

        # Determine indexes for matches
        if True in matches:
            indxs = [ i for (i, b) in enumerate(matches) if b ]

            # Iterate over the indexes
            for indx in indxs:
            
                # Mark the attendance and display the uid on the display device
                resp = api.markAttendance( uid = data["names"][indx] , time = datetime.datetime.now(), key = api_key )
                if resp == 1:
                    print( data["names"][indx] )
                    print( "marked" )
                    api.display( [data["names"][indx]] )
                elif resp == 2:
                    print( data["names"][indx] )
                    print( "already marked" )

# start the camera thread
startCameraThread()

while True:
    detectFacesAndMarkAttendance()