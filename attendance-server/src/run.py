"""
@author : Ashutosh Singh Parmar
@file : run.py
@brief : Starting point for the application
"""

import app

APP = app.create_app()

if __name__ == "__main__":
    APP.run( "0.0.0.0", 80 )
