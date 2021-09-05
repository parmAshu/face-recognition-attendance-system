"""
@author : Ashutosh Singh Parmar
@file : display.py
"""
import time, datetime

from siu import settings as st

import networkUtility as nu

class DISPLAY:
    """
    This class is used to display items on the siu display
    """

    def __init__(self, device):
        """
        This is the class constructor
        """
        self.DEVICE = device
        self.DISPLAY_STATUS = None
        self.CONN_STATUS = False
        self.LAST_DATETIME = None

    def home(self):
        """
        This function displays the home screen
        """
        self.DEVICE.clearDisplay()
        self.DEVICE.show( datetime.datetime.now().strftime( st.DATETIME_FORMAT ) + "wifi:" )

        if ( nu.wifiConnected() ):
            self.DEVICE.show( "-)" )
            self.CONN_STATUS = True
        else:
            self.DEVICE.show( "x)" )
            self.CONN_STATUS = False

        self.DISPLAY_STATUS = "HOME"

    def updateDatetime(self):
        """
        This function is used to update datetime on the home screen
        """
        if self.DISPLAY_STATUS != "HOME":
            return False
        
        temp = datetime.datetime.now().strftime( st.DATETIME_FORMAT )
        if temp == self.LAST_DATETIME:
            return True
        
        self.LAST_DATETIME = temp

        self.DEVICE.displayHome()
        self.DEVICE.show( temp )

        return True

    def updateConnectionStatus(self):
        """
        This function is used to update the connection status on home screen
        """
        if self.DISPLAY_STATUS != "HOME":
            return False

        temp = nu.wifiConnected()
        if temp == self.CONN_STATUS:
            return True

        if temp:
            text = "-)"
        else:
            text = "x)"

        self.DEVICE.cursorPosition( 5, 1 )
        self.DEVICE.show( text )
        self.CONN_STATUS = temp

        return True

    def networkScreen(self):
        """
        This function is used to display the network screen
        """
        self.DEVICE.clearDisplay()
        self.DEVICE.show( "Net: ")

        if nu.wifiConnected():
            temp = nu.wifiGetSSID()
            if temp :
                self.DEVICE.show( temp )
            temp = nu.getIPAddress()
            if temp:
                self.DEVICE.cursorPosition( 0, 1 )
                self.DEVICE.show(temp)
        else:
            self.DEVICE.show("NC")
        
        self.DISPLAY_STATUS = "NETWORK"

    def networkScanScreen(self):
        """
        This function is used to display the network scanning screen
        """
        self.DEVICE.clearDisplay()
        self.DISPLAY_STATUS = "SCANNING"