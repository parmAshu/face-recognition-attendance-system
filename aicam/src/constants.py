"""
@author : Ashutosh Singh Parmar
@file : aicam/constants.py
@brief : This file contains various constants needed by the system
"""
import os

# This variable will be populated using its counterpart from the os environment

APP_DIRECTORY = os.environ["AICAM_PATH"]

STATUS_FILE = APP_DIRECTORY + "/data/status.json"

ENCODING_FILE = APP_DIRECTORY + "/data/encoding.pickle"

UNIQUE_ID = os.environ["UNIQUE_ID"]

ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

STATUS_FILE_INIT_DATA = { "authorized": False, "api-key": "", "has-file": False }

