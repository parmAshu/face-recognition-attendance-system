"""
@author : Ashutosh Singh Parmar
@file : camera.py
@brief : This file contains functions to access the camera
"""

import os, face_recognition, pickle
import time
import cv2

import constants as const

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
camera = cv2.VideoCapture(0)

get_frames_thread_running = False
camera_frame = None

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
    try:
        while True:
            success, frame = camera.read()
            if success:
                camera_frame = frame
            else:
                get_frames_thread_running = False
    except:
        camera.release()
        get_frames_thread_running = False


with open( const.ENCODING_FILE, "rb" ) as fl:
    data = fl.read()
data = pickle.loads( data )

if __name__ == "__main__":
    import threading
    
    cam_thread = threading.Thread(target=getFrames, daemon=True)
    cam_thread.start()

    time.sleep(1)
    
    while True:
        gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)
        rgb = camera_frame
        #rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)

        rects = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5 )
 
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        encodings = face_recognition.face_encodings(rgb, boxes)

        for (x, y, w, h) in rects:
            cv2.rectangle( rgb, (x,y), (x+w,y+h), (0,255,0), 2 )

        # Iterate over encodings
        for encoding in encodings:

            matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.4)

            # Determine indexes for matches
            if True in matches:
                indxs = [ i for (i, b) in enumerate(matches) if b ]

                # Iterate over the indexes
                for indx in indxs:
                    print( data["names"][indx] )
        
        cv2.imshow("Feed", rgb)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()



