"""
@author : Ashutosh Singh Parmar
@file : settings.py
@brief : This is the main application file
"""

import os, subprocess, traceback, time, datetime, threading

from collections import deque

from siu import siu
import display, networkUtility as nu

from flask import Flask, request, Response, make_response, jsonify

AICAM_PATH = os.environ["AICAM_PATH"]

app = Flask( __name__ )

messageQueue = deque()

@app.route( "/display", methods=[ "POST" ] )
def displayHandler():
    """
    This is the display handler
    """
    global messageQueue
    try:
        msg = request.get_json()
        messageQueue.append( msg["message"] )
        return make_response( jsonify( { "message" : "success" } ) , 200 )
    except:
        return make_response( jsonify( { "message" : "failed" } ), 500 )

# Get the port name of first SIU device connected to the system
SIU_DEVICE_PORT = siu.detectSIUDevices()[0]

# This acts as an update timer
LAST_TIME = datetime.datetime.now() + datetime.timedelta( minutes=5 )

def updateFaces():
    """
    This function is used to request aicam to re-obtain face encodings
    """
    global AICAM_PATH

    try:
        with open( AICAM_PATH + "/src/update.txt", "w" ) as fl:
            pass
        return True
    except:
        traceback.print_exc()
        return False

def startAICAM():
    """
    This function is used to start the aicam program
    """
    try:
        command = "systemctl start aicam.service"
        subprocess.run( command.split() )
        return True
    except:
        return False

def stopAICAM():
    """
    This function is used to stop the aicam program
    """
    try:
        command = "systemctl stop aicam.service"
        subprocess.run( command.split() )
        return True
    except:
        return False


def goTo( screen, dev, disp ):
    """
    This function is used to change the display screen
    """
    global LAST_TIME
    LAST_TIME = datetime.datetime.now() + datetime.timedelta( minutes=5 )
    
    if screen == "HOME":
        disp.home()
    elif screen == "NETWORK":
        disp.networkScreen()
    elif screen == 'AICAM' :
        disp.aicam()

    time.sleep( 0.5 )
    dev.resetInput()

def shutdown_pi( dev, disp ):
    """
    This function executes the shutdown procedure
    """
    dev.clearDisplay()
    dev.show( "Shutdown ?")
    dev.resetInput()
    while True:
        IN = dev.getInput()
        if IN == b'e':
            dev.clearDisplay()
            dev.show( "Power off" )
            time.sleep(2)
            import subprocess
            subprocess.run( ["/usr/bin/sudo", "/sbin/shutdown", "-h", "now" ] )   
        elif IN == b'b':
            goTo( "HOME", dev, disp )
            break 

def Init():
    """
    This function performs all the initialization tasks
    """
    # Create a siu interface object
    siu_device = siu.Device( SIU_DEVICE_PORT )
    
    # Connect to the device
    siu_device.connect()

    disp = display.DISPLAY( siu_device )

    for i in range(1,6):
        siu_device.beepShort()
        time.sleep( 0.1 )

    return siu_device, disp

def home_screen( dev, disp ):
    """
    This function handles home screen tasks
    """
    global messageQueue, LAST_TIME
    
    if datetime.datetime.now() > LAST_TIME:
        goTo("HOME", dev, disp)
        return
    
    IN = dev.getInput()

    if IN == b'r':
        goTo( "NETWORK", dev, disp )
    elif IN == b'b':
        shutdown_pi( dev, disp )
    else:
        if len(messageQueue):
            dev.clearDisplay()
            dev.show( messageQueue.popleft() )
            dev.beepLong()
            time.sleep( 5 )
            goTo( "HOME", dev, disp)
            return
        disp.updateDatetime()
        disp.updateConnectionStatus()


def network_screen( dev, disp ):
    """
    This function handles network screen tasks
    """
    global LAST_TIME
    
    if datetime.datetime.now() > LAST_TIME:
        goTo("HOME", dev, disp )
        return
    
    IN = dev.getInput()

    if ( IN == b'l' ):
        goTo( "HOME", dev, disp )
    elif ( IN == B'r' ):
        goTo( "AICAM", dev, disp )

def aicam_screen( dev, disp ):
    """
    This function handles aicam screen tasks
    """
    global LAST_TIME

    if datetime.datetime.now() > LAST_TIME:
        goTo( "AICAM", dev, disp )
        return

    IN = dev.getInput()
    
    if ( IN == b'l' ):
        goTo( "NETWORK", dev, disp )

    elif IN == b'e':
        dev.clearDisplay()
        dev.show( "SERVICE " )
        time.sleep(5)
        dev.show( "-")
        dev.resetInput()
        while True:
            IN = dev.getInput()
            if IN == b'e':
                dev.show("start")
                dev.cursorPosition( 0, 1 )
                if startAICAM():
                    dev.show("done")
                else:
                    dev.show("failed")
                time.sleep(5)
                goTo( "HOME", dev, disp )
                return

            elif IN == b'b':
                dev.show("stop")
                dev.cursorPosition(0, 1)
                if stopAICAM():
                    dev.show("done")
                else:
                    dev.show("failed")
                time.sleep( 5 )
                goTo( "HOME", dev, disp )
                return

    elif IN == b'b':
        dev.clearDisplay()
        dev.show( "REQ. UPDATE" )
        dev.cursorPosition( 0, 1 )
        if updateFaces():
            dev.show("success")
        else:
            dev.show("failed")
        time.sleep(5)
        goTo( "HOME", dev, disp )


def run():
    """
    The function handles all the main tasks
    """
    siu_device, disp = Init()

    disp.home()

    while True:
        status = disp.DISPLAY_STATUS

        if status == "HOME":
            home_screen( siu_device, disp )
        elif status == "NETWORK":
            network_screen( siu_device, disp )
        elif status == "AICAM":
            aicam_screen( siu_device, disp )

if __name__ ==  "__main__" :
    TH = threading.Thread( target = run, daemon=True )
    TH.start()
    app.run("localhost", port=8000 )

