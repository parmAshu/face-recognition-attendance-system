"""
@author : Ashutosh Singh Parmar
@file : settings.py
@brief : This file contains functions for network related tasks
"""
import os, subprocess, socket

WIFI_INTERFACE = "wlan0"

INVALID_SSID = [ "--" ]

def wifiStart():
    """
    This function is used to turn on the wifi

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
    command = "nmcli wifi radio on"
    subprocess.run( command.split() )


def wifiStop():
    """
    This function is used to turn off the wifi

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
    command = "nmcli wifi radio off"
    subprocess.run( command.split() )

def wifiConnected():
    """
    This function is used to check whether the system is connected to a WiFi or not

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    SSID of WAP the device is currently connected to
    /OR/
    None

    EXCEPTIONS :
    ----------
    ***
    """
    command = "nmcli networking connectivity"
    out = subprocess.run( command.split(), capture_output=True ).stdout.decode().strip()
    if out == "limited" or out == "full":
        return True
    else:
        return False

def wifiGetSSID():
    """
    This function is used to get the ssid of current wifi network

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    SSID of active wifi network
    /OR/
    None

    EXCEPTIONS :
    ----------
    ***
    """
    command = "nmcli connection show --active"
    out = subprocess.run( command.split(), capture_output=True ).stdout.decode().strip()
    
    if len(out):
        out = out.split('\n')[1]
        return out[ 0:out.index(" ") ]
    else :
        return None

def wifiSavedNetworks():
    """
    This function is used to obtain a list of saved networks

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
    command = "nmcli connection show"
    out = subprocess.run( command.split(), capture_output=True ).stdout.decode().strip()

    if not len(out):
        return None
    
    out = out.split('\n')

    networks = []
    for l in out:
        if "wifi" in l:
            networks.append( l[0:l.index(" ")] )

    if not len(networks):
        return None
    else :
        return networks

def wifiForgetNetwork( ssid ):
    """
    This function is used to forget a wifi network

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    True : Success
    False : Otherwise
    """
    command = "nmcli connection delete "+ssid
    out = subprocess.run( command.split(), capture_output=True ).stdout.decode().strip()

    if "success" in out:
        return True
    else:
        return False

def wifiScan():
    """
    This function is used to scan for available wifi networks

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    A list of available networks
    /OR/
    None otherwise

    EXCEPTIONS :
    ----------
    ***
    """
    command = "nmcli device wifi list"
    out = subprocess.run( command.split(), capture_output=True ).stdout.decode().strip()

    if not len(out):
        return None
    
    out = out.split('\n')
    out = out[1:len(out)]

    networks = []

    for l in out:
        if "*" not in l:
            temp = l[1:len(l)].strip()
            if temp not in INVALID_SSID:
                networks.append( temp[0:temp.index(" ")] )
    
    if not len(networks):
        return None
    else:
        return networks

def wifiConnect( ssid, password ):
    """
    This function is used to connect the device to a particular wifi network

    PARAMETERS :
    ----------
    ssid : WiFi ssid
    password : WiFi password

    RETURNS :
    -------
    ***

    EXCEPTIONS :
    ----------
    ***
    """
    command = "nmcli device wifi connect "+ssid+" password "+password
    out = subprocess.run( command.split(), capture_output=True ).stdout.decode().strip()

    if "success" in out:
        return True
    else:
        return False

def wifiSwitch( ssid ):
    """
    This function is used to connect to a different wifi network than current one

    PARAMETERS :
    ----------
    ssid : SSID of the network to switch to

    RETURNS :
    -------
    True
    /OR/
    False

    EXCEPTIONS :
    ----------
    ***
    """
    command = "nmcli connection up "+ssid
    out = subprocess.run( command.split(), capture_output=True ).stdout.decode().strip()

    if "success" in out:
        return True
    else:
        return False

def wifiDisconnect():
    """
    This function is used to disconnect from any connected wifi network

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
    command = "nmcli device disconnect wlan0"
    subprocess.run( command.split() )


def getIPAddress():
    """
    This function is used to obtain the ip address of the system

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    IP address as string
    /OR/
    None
    """
    try:
        s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        s.connect( ("8.8.8.8", 80) )
        return s.getsockname()[0]
    except:
        return None