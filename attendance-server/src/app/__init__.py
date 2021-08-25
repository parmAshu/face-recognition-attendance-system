"""
@author : Ashutosh Singh Parmar
@file : app.py
@brief : This is the main file for attendance server
"""
from flask import Flask

# Flask application object
#app = Flask(__name__)

# Importing general deecorators
#from serverDecorators import *

# Setting up administrator APIs
#from administrator import refreshTokens, authenticate

# Setting up employee APIs
#import employees

# Setting up attendance APIs
#import attendance

# Setting up camera device APIs
#import cameraDevices

# Web app
#import web

from .administrator import admin
from .attendance import attendance
from .cams import cams
from .employees import employees
from .faceEncoding import encodings
from .web import web


def create_app():
    
    app = Flask( __name__ )

    app.register_blueprint( admin )
    app.register_blueprint( attendance )
    app.register_blueprint( cams )
    app.register_blueprint( employees )
    app.register_blueprint( encodings )
    app.register_blueprint( web )

    return app