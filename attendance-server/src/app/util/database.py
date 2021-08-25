"""
@author : Ashutosh Singh Parmar
@file : database.py
@brief : This file contains APIs for performing database operations. These APIs are constitute the database abstraction layer.
This layer ensures that the attendance system server remains independent of the database or database system being used.
"""

from enum import unique
import os, base64, datetime, secrets
from pymongo import MongoClient

import face_recognition as fr
import pickle

from util import exceptions
import util.constants as const
from util.validator import *





# CONSTANTS -----------------------------------------------------------------------------------------------------------

# THESE VARIABLES WILL BE POPULATED USING THE OS ENVIRONMENT

ATT_SERVER_PATH = os.environ["ATT_SERVER_PATH"]

MONGODB_URL = os.environ["MONGODB_URL"]
MONGODB_PORT = int(os.environ["MONGODB_PORT"])

MONGODB_USER = None
MONGODB_PASS = None

DB_CHECK_FILE = ATT_SERVER_PATH + "/data/dbinit.emt"

# ---------------------------------------------------------------------------------------------------------------------





# DATABASE INITIALIZATION --------------------------------------------------------------------------------------------

# This part will check whether the database has been previously initialized or not. This is done by detecting the presence.
# A dbinit.emt file at a specified location. If the file is not present, it means that the database has not been initialized.
# In that case, the following code will initialize the database for the system.

# Connecting to local mongodb server
CLIENT = MongoClient(MONGODB_URL, MONGODB_PORT)
DB = CLIENT.attendance_system

try:
    fl = open(DB_CHECK_FILE)
    # The file exists which means that database has been initialized
    #print("Database is already initialized !")
    fl.close()
except:
    #print("initializing database")
    # Initialize the database
    DB.employee.create_index("UID", unique=True)
    DB.employee.create_index("email", unique=True)
    DB.attendance.create_index("date", unique=True)
    DB.attendance.create_index("entry time")
    DB.devices.create_index("device id", unique=True)
    DB.devices.create_index("api key", unique=True)
    fl = open(DB_CHECK_FILE, 'w')
    fl.close()

# ---------------------------------------------------------------------------------------------------------------------





# DATABASE SPECIFIC VALIDATORS-----------------------------------------------------------------------------------------

def uidExists(fun):
    """
    This function makes sure that a uid exists in the database, an exception is raised if the uid does not exist in the database.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments otherwise the function will raise exceptions
    ----------
    uid : The employee uid

    RETURNS :
    -------
    Whatever the decorated function returns

    EXCEPTIONS :
    ----------
    util.exceptions.UIDNotExistsException : If the uid does not exist in the database
    KeyError : If the uid argument is not passed
    util.exceptions.UIDNotExistError : If no employee with the given uid exists in the database
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    def inner(**kwargs):
        Filter = {}
        Filter["UID"] = kwargs["uid"]
        result = DB.employee.find_one(Filter)
        if not result:
            raise exceptions.UIDNotExistsError
        return fun(**kwargs)
    return inner

# ---------------------------------------------------------------------------------------------------------------------





# GENERAL APIs --------------------------------------------------------------------------------------------------------

def test():
    """
    This function is used to test whether database is online or not.

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    True : Database online
    False : Otherwise
    """
    try:
        global CLIENT
        CLIENT.server_info()
        return True
    except :
        return False

# ---------------------------------------------------------------------------------------------------------------------





# EMPLOYEE APIs -------------------------------------------------------------------------------------------------------

@uidValidator
@firstnameValidator
@lastnameValidator
@genderValidator
@emailValidator
@imageValidator
def addEmployee(**kwargs):
    """
    This function is used to add an employee to the database

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ---------
    uid : The unique employee id
    firstname : First name of the employee
    lastname : Last name of the employee
    gender : Sex of the employee
    email : contact email of the employee
    img : image of the employee as bytes array
    dob: data of birth of the employee
    doj : data of joining of the employee
    department : current department of the employee
    title : job title of the employee
    image : employee image
    image type : image type (extension)

    RETURNS
    -------
    True : Success
    False : When failed to commit changes to database

    EXCEPTIONS : 
    ----------
    KeyError : If any of the above parameters are not provided
    pymongo.errors.DuplicateKeyError : If the an employee with same uid or email already exists in the database
    util.exceptions.InvalidUIDError : If the uid is invalid
    util.exceptions.InvalidNameError : If the first name or last name is invalid
    util.exceptions.InvalidGenderError : If the gender is invalid
    util.exceptions.InvalidEmailError : If the email is invalid
    util.exceptions.InvalidDateError : If the DOB or DOJ are invalid
    util.exceptions.UnsupportedImageTypeError : If the image extension is not supported
    util.exceptions.InvalidImageError : If the image data is invalid
    util.exceptions.ImageTooBigError : If the image size is too large
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    data = {}
    data["UID"] = kwargs["uid"]
    data["first name"] = kwargs["firstname"]
    data["last name"] = kwargs["lastname"]
    data["gender"] = kwargs["gender"]
    data["email"] = kwargs["email"]
    data["DOB"] = kwargs["dob"]
    data["DOJ"] = kwargs["doj"]
    data["department"] = kwargs["department"]
    data["title"] = kwargs["title"]
    data["image"] = kwargs["image"]
    data["image type"] = kwargs["imgType"]

    result = DB.employee.insert_one(data)
    return result.acknowledged

@uidValidator
def removeEmployee(**kwargs):
    """
    This function is used to remove and employee from the database.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ----------
    uid : The unique employee id

    RETURNS :
    -------
    True : Success
    False : Failed to commit changes to the database
    
    EXCEPTIONS : 
    ----------
    KeyError : If any of the above parameters are not provided
    util.exceptions.InvalidUIDError : If the uid is invalid
    util.exceptions.UIDNotExistsError : If no employee with the passed uid exists in the database
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """

    data = {}
    data["UID"] = kwargs["uid"]

    result = DB.employee.delete_one(data)
    
    if result.acknowledged :
        
        if not result.deleted_count:
            raise exceptions.UIDNotExistsError
        
        att = DB.attendance.find( {} )
        
        # remove attendance entries of this employee from the database
        for dt in att:
            _entry = []
            for x in dt["entry time"]:
                if x["uid"] != kwargs["uid"]:
                    _entry.append( x )
            
            flt = {}
            flt["date"] = dt["date"]
            data = {}
            data["$set"] = {}
            data["$set"]["entry time"] = _entry
            DB.attendance.update_one( flt, data )

        return True
    else:
        return False

def getNumEmployees():
    """
    This function returns the number of employees in the database

    PARAMETERS 
    ----------
    NONE

    RETURNS
    -------
    The number of employees in the database

    EXCEPTIONS :
    ----------
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    return DB.employee.count_documents({})

@uidValidator
def getEmployeeDetails(**kwargs):
    """
    This function returns the name of the employee with given uid

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ----------
    uid : The employee id

    RETURNS :
    -------
    1. A dictionary containing employee details
    2. 'None' if no employee with given uid, exists in the database

    EXCEPTIONS :
    ----------
    KeyError : If any of the above parameters are not provided
    util.exceptions.InvalidUIDError : If the uid is invalid
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    Filter = {}
    Filter["UID"] = kwargs["uid"]
    result = DB.employee.find_one( Filter )
    if result:
        result["firstname"] = result["first name"]
        result["lastname"] = result["last name"]
        del result["first name"]
        del result["last name"]
        del result["_id"]
        del result["image"]
        del result["image type"]
        return result
    else:
        return None

@uidValidator
def updateEmployeeDetails(**kwargs):
    """
    This function is used to update the email of an employee in the database.

    PARAMETERS : The following parameters must be provided as keyworded arguments
    ----------
    uid (*REQUIRED): The unique employee id
    email (OPTIONAL) : contact email of the employee
    department (OPTIONAL) : The department of employee
    title (OPTIONAL) : job title of the employee

    RETURNS :
    -------
    True : Success
    False : If the changes could not be committed to the database

    EXCEPTIONS :
    ----------
    utils.exceptions.InvalidUIDError : If the uid is invalid
    utils.exceptions.InvalidEmailError : If the email is invalid
    KeyError : If the keys are invalid i.e. any unrecognized keys are present in the parameters
    utils.exceptions.NoValueError : If none of the optional arguments were provided
    pymongo.errors.DuplicateKeyError : If the email is not unique
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    keys = kwargs.keys()

    if len(keys) > 4:
        raise KeyError

    if "email" not in keys and "department" not in keys and "title" not in keys:
        raise exceptions.NoValueError

    for k in keys:
        if k != "email" and k != "title" and k != "department" and k!="uid":
            raise KeyError


    Filter = {}
    Filter["UID"] = kwargs["uid"]

    data = {}
    data["$set"] = {}
    data["$set"] = kwargs

    result = DB.employee.update_one(Filter, data)

    if result.acknowledged and result.matched_count:
        return True
    else:
        return False


@uidValidator
def getEmployeeImage(**kwargs):
    """
    This function returns the name of the employee with given uid

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ----------
    uid : The employee id

    RETURNS :
    -------
    1. A tuple of the form ( ...image data as bytes array...  ,   <image type/extension> )
    2. 'None' if no employee with the given uid exists in the database

    EXCEPTIONS :
    ----------
    KeyError : If any of the above parameters are not provided
    util.exceptions.InvalidUIDError : If the uid is invalid
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    Filter = {}
    Filter["UID"] = kwargs["uid"]
    result = DB.employee.find_one( Filter )

    if result:
        return result["image"], result["image type"]
    else:
        return None

@uidValidator
@imageValidator
@uidExists
def updateEmployeeImage(**kwargs):
    """
    This function is used to update the image of an employee in the database.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ----------
    uid : The employee id
    image : Image data as bytes array
    imgType : Image extension - 'jpeg' , 'png' etc.

    RETURNS :
    -------
    True : Success
    False : Failed to commit changes to the database

    EXCEPTIONS :
    ----------
    KeyError : If any of the above parameters are not provided
    util.exceptions.InvalidUIDError : If the uid is invalid
    util.exceptions.UnsupportedImageTypeError : If the image extension is not supported
    util.exceptions.InvalidImageError : If the image data is invalid
    util.exceptions.ImageTooBigError : If the image size is too large
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    Filter = {}
    Filter["UID"] = kwargs["uid"]

    data = {}
    data["$set"] = {}
    data["$set"]["image"] = kwargs["image"]
    data["$set"]["image type"] = kwargs["imgType"]

    result = DB.employee.update_one(Filter, data)

    if result.acknowledged and result.matched_count:
        return True
    else:
        return False

def getAllEmployeeID():
    """
    This function is used to obtain a list of all the employee UID in the database

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    A list of employee ids
    /OR/
    None : If something goes wrong

    EXCEPTIONS :
    ----------
    ***
    """
    result = DB.employee.find({}, { "UID" : 1, "_id" : 0 } )
    uidList = []
    if result:
        for x in result:
            uidList.append(x["UID"])
        return uidList
    else:
        return None

# ---------------------------------------------------------------------------------------------------------------------





# ATTENDANCE APIs -----------------------------------------------------------------------------------------------------

@dateValidator
def addDate(**kwargs):
    """
    This function is used to add a date to the database.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ----------
    date : date object

    RETURNS :
    -------
    True : Success
    False : Failed to commit changes to the database

    EXCEPTIONS :
    ----------
    KeyError : If the required arguments are not provided
    util.exceptions.InvalidDateError : If the date object is invalid
    pymongo.errors.DuplicateKeyError : If the date already exists in the database
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    data = {}
    data["date"] = datetime.datetime.strptime( kwargs["date"].strftime(const.DATE_FORMAT), const.DATE_FORMAT )
    data["entry time"] = []

    result = DB.attendance.insert_one(data)

    return result.acknowledged

@uidValidator
@uidExists
@datetimeValidator
def markAttendance(**kwargs):
    """
    This function is used to mark the attendance of an employee.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ----------
    uid : employee id
    datetime : datetime object representing the date and entry time ( in local time ) for the employee

    RETURNS :
    -------
    True : success
    False : If changes could not be committed to the database

    EXCEPTIONS :
    ----------
    KeyError : If one the above arguments is not provided
    utils.exceptions.InvalidUIDError : If the uid is invalid
    utils.exceptions.InvalidDateError : If the date object is invalid
    utils.exceptions.UIDNotExistsError : If no employee with the passed uid exists
    utils.exceptions.DuplicateAttendanceError : If the attendance has been already marked
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """

    attendanceList = getAttendanceAll( date=kwargs["datetime"].date() )

    if not attendanceList:
        return False

    for x in attendanceList["attendance"]:
        if x["uid"] == kwargs["uid"] :
            raise exceptions.DuplicateAttendanceError

    Filter = {}
    Filter["date"] = kwargs["datetime"].replace( hour = 0, minute = 0, second = 0, microsecond = 0 )

    data={}
    data["$push"] = {}
    data["$push"]["entry time"] = { "uid" : kwargs["uid"], "time" : kwargs["datetime"] }

    result = DB.attendance.update_one(Filter, data)

    if result.acknowledged and result.matched_count :
        return True
    else:
        return False

@dateValidator
def getAttendanceAll(**kwargs):
    """
    This function returns the list of all employees present at a given date

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ----------
    date : date object for the given date

    RETURNS :
    -------
    { "date" : date objects, "attendance" : [ { "uid" : "employee uid", "time" : datetime object } ... ] } dictionary
    None : If something goes wrong

    EXCEPTIONS :
    ----------
    KeyError : If one of the above arguments is not provided
    util.exceptions.InvalidDateError : If the date object is invalid
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """

    Filter = {}
    Filter["date"] = datetime.datetime.strptime( kwargs["date"].strftime(const.DATE_FORMAT), const.DATE_FORMAT )
    
    result = DB.attendance.find_one(Filter)

    if result:
        del( result["_id"] )
        result["attendance"] = result["entry time"]
        del(result["entry time"])
        return result
    else:
        return None

@uidValidator
@uidExists
def getAttendanceOf(**kwargs):
    """
    This function returns the attendance details for a specific employee

    PARAMETERS : The following parameters are NOT OPTIONAL and must be passed as keyworded arguments.
    ----------
    uid : The employee id
    
    RETURNS :
    -------
    List of { datetime : "P/A" } dictionaries

    List of { "date" : dateobject, "present" : True/False, "time" : timeobject } dictionaries
    None : upon failure

    EXCEPTIONS :
    ----------
    KeyError : If any of the above arguments are not passed
    utils.exceptions.InvalidUIDError : If the uid is invalid
    utils.exceptions.UIDNotExistsError : If no employee with the passed uid exists in the database
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """

    result = DB.attendance.find({})
    
    if result:
        attendanceList = []
        for Date in result:
            flag = False
            data = { "date" : Date["date"] }
            for person in Date["entry time"]:
                if person["uid"] == kwargs["uid"]:
                    # The person was present, append the datetime object
                    data["time"] = person["time"].time()
                    data["present"] = True
                    flag = True
                    break
            if not flag:
                data["time"] = datetime.time( 0,0 )
                data["present"] = False
            attendanceList.append( data )
        return attendanceList
    else:
        return None

@dateValidator1
def getAttendanceAll_between(**kwargs):
    """
    This function is used to get the attendance of all employee within a range of dates.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be provided as  keyworded arguments.
    ----------
    startdate : The starting date object
    enddate : The ending date object

    RETURNS : 
    -------
    List of { "date" : date objects, "attendance" : [ { "uid" : "employee uid", "time" : datetime object } ... ] } dictionaries
    None : If something goes wrong

    EXCEPTIONS :
    ----------
    KeyError : If any of the above arguments are not provided
    utils.exceptions.InvalidUIDError : If the passed uid is not valid
    utils.exceptions.UIDNotExistsError : If no employee with the passed uid exists in the database
    utils.exceptions.InvalidDateError : If the provided dates are invalid
    """
    startdate = datetime.datetime.strptime( kwargs["startdate"].strftime(const.DATE_FORMAT), const.DATE_FORMAT )
    enddate = datetime.datetime.strptime( kwargs["enddate"].strftime(const.DATE_FORMAT), const.DATE_FORMAT )

    result = DB.attendance.find( { "date" : { "$gte" : startdate, "$lte" : enddate } } )

    attendanceList = []
    if result:
        for x in result:
            attendanceList.append( { "date"  : x["date"].date(), "attendance" : x["entry time"] } )
        return attendanceList
    else:
        return None
    
@uidValidator
@uidExists
@dateValidator1
def getAttendanceOf_between(**kwargs):
    """
    This function is used to get the attendance of an employee within a range of dates.

    PARAMETERS : The following parameters are NOT OPTIONAL and must be provided as  keyworded arguments.
    ----------
    uid : The uid of the employee
    startdate : The starting date object
    enddate : The ending date object

    RETURNS : 
    -------
    List of { "date" : dateobject, "present" : True/False, "time" : timeobject } dictionaries
    None : upon failure

    EXCEPTIONS :
    ----------
    KeyError : If any of the above arguments are not provided
    utils.exceptions.InvalidUIDError : If the passed uid is not valid
    utils.exceptions.UIDNotExistsError : If no employee with the passed uid exists in the database
    utils.exceptions.InvalidDateError : If the provided dates are invalid
    """
    startdate = datetime.datetime.strptime( kwargs["startdate"].strftime(const.DATE_FORMAT), const.DATE_FORMAT )
    enddate = datetime.datetime.strptime( kwargs["enddate"].strftime(const.DATE_FORMAT), const.DATE_FORMAT )

    result = DB.attendance.find( { "date" : { "$gte" : startdate, "$lte" : enddate } } )

    attendanceList = []
    if result:
        for Date in result:
            flag = False
            data = { "date" : Date["date"].date() }
            for person in Date["entry time"]:
                if person["uid"] == kwargs["uid"]:
                    # The persion was present, append the datetime object
                    data["time"] = person["time"].time()
                    data["present"] = True
                    flag = True
                    break
            if not flag:
                data["time"] = datetime.time( 0,0 )
                data["present"] = False
            attendanceList.append( data )
        return attendanceList
    else:
        return None

@dateValidator
def clearAttendanceRecordFor(**kwargs):
    """
    This function is used to clear the attendance record for a give date

    PARAMETERS : The following parameters are NOT OPTIONAL and must be provided as keyworded arguments
    ----------
    date : The date object

    RETURNS :
    -------
    True : Success
    False : Otherwise

    EXCEPTIONS : 
    ----------
    util.exceptions.InvalidDateError : If the date object is invalid
    util.exceptions.DateDoesNotExistError : If no record for given date exists in the database
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """

    Filter = { "date" : datetime.datetime.strptime( kwargs["date"].strftime(const.DATE_FORMAT), const.DATE_FORMAT ) }

    result = DB.attendance.delete_one( Filter )

    if result.acknowledged:
        if result.deleted_count:
            return True
        else:
            raise exceptions.DateDoesNotExistsError
    else:
        return False

def clearAttendanceRecords():
    """
    This function is used to clear all the attendance records in the database

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    True : Success
    False : If the database could not be modified

    EXCEPTIONS :
    ----------
    util.exceptions.DateDoesNotExistsError : If no date object exists in the database
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """
    result = DB.attendance.delete_many({})
    if result.acknowledged :
        if result.deleted_count:
            return True
        else:
            raise exceptions.DateDoesNotExistsError
    else:
        return False

@dateValidator
def dateExists(**kwargs):
    """
    This function is used to check whether a date exists in the database

    PARAMETERS : The following parameters are NOT OPTIONAL and must be provided as keyworded arguments
    ----------
    date : The date object corresponding to date of interest

    RETURNS :
    -------
    True : exists
    False : does not exist

    EXCEPTIONS : 
    ----------
    util.exceptions.InvalidDateError : If the date object is invalid
    pymongo.errors.ServerSelectionTimeoutError : If the connection to database could not be established
    """

    Filter = { "date" : datetime.datetime.strptime( kwargs["date"].strftime(const.DATE_FORMAT), const.DATE_FORMAT ) }
    result = DB.attendance.find_one( Filter )

    if result:
        return True
    else:
        return False
# ---------------------------------------------------------------------------------------------------------------------





# AI CAMERA DEVICE APIs -----------------------------------------------------------------------------------------------------

def addCameraDevice( **kwargs ):
    """
    This function is used to add an AI camera device to the database

    PARAMETERS :  The following parameters are NOT OPTIONAL and must be provided as keyworded arguments.
    ----------
    device_id : The unique device id

    RETURNS :
    -------
    True : Success
    False : Failed to commit changes to database

    EXCEPTIONS :
    ----------
    KeyError : If any of the above arguments were not provided
    pymongo.DuplicateKeyError : If either API key or device id is repeated
    pymongo.ServerSelectionTimeoutError : If connection to database could not be established
    """
    data = {}
    data["device id"] = kwargs["device_id"]
    data["location"] = "NA"
    data["api key"] = secrets.token_urlsafe(const.API_KEY_LENGTH)
    data["registered"] = False
    data["has file"] = False

    result = DB.devices.insert_one( data )

    return result.acknowledged

def getCameraDevices():
    """
    This function is used to get the details about all the AI camera devices in the database

    PARAMETERS :
    ----------
    NONE

    RETURNS :
    -------
    A list of dictionaries containing details about various devices
    None : if something went wrong

    EXCEPTIONS :
    ----------
    ***
    """
    result = DB.devices.find( {} )

    device_list = []
    if result:
        for x in result:
            x["device_id"] = x["device id"]
            del( x["device id"] )
            del( x["_id"] )
            device_list.append( x )
        return device_list
    else:
        return None

def removeCameraDevice(**kwargs):
    """
    This function is used to remove an AI camera device from the database

    PARAMETERS :  The following parameters are NOT OPTIONAL and must be provided as keyworded arguments.
    ----------
    device_id : The unique device id

    RETURNS :
    -------
    True : Success
    False : If the device was not removed from the database

    EXCEPTIONS :
    ----------
    KeyError : If any of the above arguments were not provided
    """
    Filter = {}
    Filter["device id"] = kwargs["device_id"]
    result = DB.devices.delete_one( Filter )

    if result.acknowledged and result.deleted_count:
        return True
    else:
        return False

def cameraDeviceRegister( **kwargs ):
    """
    This function is used to update the registered status of the device

    PARAMETERS :
    ----------
    device_id : The unique device id
    status : True/False

    RETURNS :
    -------
    True : Success
    False : Otherwise

    EXCEPTIONS :
    ----------
    ***
    """
    Filter = {}
    Filter["device id"] = kwargs["device_id"]
    result = DB.devices.update_one( Filter, { "$set" : { "registered" : kwargs["status"] } } )
    if result.acknowledged and result.modified_count:
        return True
    else:
        return False

def cameraDeviceHasFile( **kwargs ):
    """
    This function is used to commit whether the AI camera device has face encodings file, in the database

    PARAMETERS :
    ----------
    device_id : The unique device id
    status : True/False

    RETURNS :
    -------
    True : Success
    False : Otherwise

    EXCEPTIONS :
    ----------
    ***
    """
    Filter = {}
    Filter["device id"] = kwargs["device_id"]
    result = DB.devices.update_one( Filter, { "$set" : { "has file" : kwargs["status"] } } )
    if result.acknowledged and result.modified_count:
        return True
    else:
        return False

def updateCameraDeviceLocation(**kwargs):
    """
    This function is used to update the device location in the database

    PARAMETERS :
    ----------
    device_id : The unique device id
    location : The new device location

    RETURNS :
    -------
    True : Success
    False : Otherwise

    EXCEPTIONS :
    ----------
    ***
    """
    Filter = {}
    Filter["device id"] = kwargs["device_id"]
    result = DB.devices.update_one( Filter, { "$set" : { "location" : kwargs["location"] } } )
    if result.acknowledged and result.modified_count:
        return True
    else:
        return False

# ---------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    print( getNumEmployees() )