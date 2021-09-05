"""
@author : Ashutosh Singh Parmar
@file : siu/siu.py
@brief : This file contains utility functions to interact with siu devices connected to the computer
"""

from sys import byteorder
import time
import serial, serial.tools.list_ports

import siu.settings as st

from siu.errors import *

def SIMPLE_SERIAL_FRAME( title, data ):
    """
    This API is used to return a simple serial frame using the provided parameters

    PARAMETERS :
    ----------
    1. title (int): A byte representing the title of the simple serial message
    2. data (bytesarray): Data bytes to be sent

    RETURNS :
    -------
    Bytes belonging to the simple serial frame

    EXCEPTIONS :
    ----------
    siu.errors.InvalidSimpleSerialFrame - If the provided title or data is invalid
    """
    if title > 255 or len( data ) > 255:
        raise InvalidSimpleSerialFrame
    
    result = b"\x0D" + title.to_bytes( length = 1, byteorder = 'little' ) + len(data).to_bytes( length = 1, byteorder = "little" ) + data + b"\x1E"

    return result


    

def detectSIUDevices():
    """
    This API is used to return a list of SIU devices connected to the system

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    A list of siu devices connected to the system
    
    EXCEPTIONS :
    ----------
    ***
    """
    siu_devices = []

    serial_devices = list(serial.tools.list_ports.comports())
    serial_devices = [ temp.device for temp in serial_devices ]

    for dev in serial_devices:
        p = serial.Serial()
        p.port = dev
        p.baudrate = st.SIU_BAUDRATE
        p.timeout = 0.1 
        try:
            p.open()
            time.sleep( st.SIU_BOOT_TIME )
            p.write( SIMPLE_SERIAL_FRAME( st.SIU_DETECT, b'' ) )
            resp = p.read_until( '\n' ).decode( "ASCII" )
            if resp.startswith("siu") : 
                siu_devices.append( dev )
            raise Exception
        except:
            p.close()

    return siu_devices

class Device:
    """
    This class contains functions to interact with the siu device
    """

    def __init__( self, PORT ):
        """
        This is the class constructor

        PARAMETERS :
        ----------
        port (string) - The port name

        RETURNS :
        -------
        NOTHING
        """
        self.DEVICE = serial.Serial()
        self.DEVICE.port = PORT
        self.DEVICE.baudrate = st.SIU_BAUDRATE
        self.DEVICE.timeout = 0

    def connect( self ):
        """
        This function is used to connect to the siu device

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.open()
        time.sleep( 5 )

    def clearDisplay( self ):
        """
        This function is used to clear the display

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_CLEAR_DISPLAY, b'' ) )
        time.sleep(0.1)

    def displayHome( self ):
        """
        This function is used to move the cursor to home position

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_DISPLAY_HOME, b'' ) )
        time.sleep(0.01)

    def displayOn( self ):
        """
        This function is used to turn on the display

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_DISPLAY_ON, b'' ) )
        time.sleep(0.1)

    def displayOff( self ):
        """
        This function is used to turn off the display

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_DISPLAY_OFF, b'' ) )
        time.sleep(0.1)

    def enableCursor( self ):
        """
        This function is used to enable the cursor

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_CURSOR_ENABLE, b'' ) )
        time.sleep(0.05)

    def cursorDisable( self ):
        """
        This function is used to disable the cursor

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_CURSOR_DISABLE, b'' ) )
        time.sleep(0.05)

    def backlightOn( self ):
        """
        This function is used to turn on the backlight

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_BACKLIGHT_ENABLE, b'' ) )
        time.sleep(0.05)

    def backlightOff( self ):
        """
        This function is used to turn off the backlight

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_BACKLIGHT_DISABLE, b'' ) )
        time.sleep(0.05)

    def cursorPosition( self, X, Y ):
        """
        This function is used to set the cursor position on the LCD display

        PARAMETERS :
        ----------
        X : Horizontal position (0-15)
        Y : Vertical position (0-1)

        RETURNS :
        -------
        True - success
        False - otherwise

        EXCEPTIONS :
        ----------
        ***
        """
        if X > 15 or X < 0 or Y > 1 or Y < 0 :
            return False
        
        data = X.to_bytes( length = 1, byteorder = "little" ) + Y.to_bytes( length = 1, byteorder = "little" )

        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_CURSOR_POSITION, data ) )

        time.sleep(0.05)
        return True

    def beepLong( self ):
        """
        This function is used to sound a long blocking beep

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_LONG_BEEP, b'' ) )
        time.sleep( 0.2)

    def beepShort( self ):
        """
        This function is used to sound a short blocking beep

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_SHORT_BEEP, b'' ) )
        time.sleep(0.02)

    def show( self, data ):
        """
        This function is used to print to the display at current position

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.write( SIMPLE_SERIAL_FRAME( st.SIU_PRINT, data.encode( "ASCII" ) ) )
        time.sleep(0.1)

    def getInput( self ):
        """
        This function is used to get input from the siu device

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        ***

        EXCEPTIONS :
        ----------
        ***
        """
        return self.DEVICE.read( 1 )

    def resetInput( self ):
        """
        This function is used to reset the inputs from the siu device

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.reset_input_buffer()

    def disconnect( self ):
        """
        This function is used to close the port

        PARAMETERS :
        ----------
        NONE

        RETURNS :
        -------
        NOTHING

        EXCEPTIONS :
        ----------
        ***
        """
        self.DEVICE.close()