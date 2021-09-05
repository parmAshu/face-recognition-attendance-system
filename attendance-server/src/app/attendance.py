"""
@author : Ashutosh Singh Parmar
@file : app/attendance.py
@brief : This file attendance related APIs
"""

from datetime import date
from os import write
import sys, traceback, io, csv, pymongo
from types import MethodDescriptorType
from functools import wraps
from flask import request, Response, make_response, send_file, jsonify, Blueprint

from util.exceptions import *
from util import database, constants as const

from serverDecorators import *

from session import *

attendance = Blueprint( "attendance", __name__ )

# ATTENDANCE API SPECIFIC VALIDATORS -----------------------------------------------------------------------------------

def prepareDatetime( f ):
    """
    This decorator is used to prepare datetime objects for the request handlers
    """
    @wraps(f)
    def inner(**kwargs):
        try:
            data = request.get_json()
            data_keys = data.keys()

            if "date" in data_keys:
                data["date"] = datetime.datetime.strptime( data["date"], const.DATE_FORMAT ).date()

            if "datetime" in data_keys:
                data["datetime"] = datetime.datetime.strptime( data["datetime"], const.ATTENDANCE_DATETIME_FORMAT )

            if "startdate" in data_keys:
                data["startdate"] = datetime.datetime.strptime( data["startdate"], const.DATE_FORMAT ).date()
                
            if "enddate" in data_keys:
                data["enddate"] = datetime.datetime.strptime( data["enddate"], const.DATE_FORMAT ).date()

            return f(**data)
                
        except ValueError as ve:
            if "timedelta" in str(ve):
                return apiResponse( "Incorrect datetime format", 400 )
            else:
                return apiResponse( "Invalid request", 400 )
        except Exception as e:
            return apiResponse( "Invalid request", 400 )
    return inner

# ----------------------------------------------------------------------------------------------------------------------





# APIs -----------------------------------------------------------------------------------------------------------------

@attendance.route( "/attendance/mark/one", methods=["POST"] )
@threadSafe
@authenticate
@prepareDatetime
def markAttendanceHandler(**kwargs):
    """
    This API is used to mark the attendance of an employee

    REQUEST :
    -------
    method : POST
    route : /attendance/markone
    authentication : bearer token - jwt
    body : json
        {
            "uid" : "the employee id"
            "datetime" : "local datetime in ISO format"
        }
    
    RESPONSE : json
    --------
        {
            "message" : "message string"
        }
    """
    try:

        if not database.dateExists( date=kwargs["datetime"].date() ) and not database.addDate( date=kwargs["datetime"].date() ):
            raise Exception

        if kwargs["datetime"].date() > datetime.date.today():
            raise InvalidDateError

        if not database.markAttendance( uid=kwargs["uid"], datetime=kwargs["datetime"] ):
            raise Exception

        return apiResponse( "Attendance marked", 200 )
    
    except KeyError as ke:
        return apiResponse( "Invalid request parameters", 400 )
    except InvalidDateError:
        return apiResponse( "Invalid date", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except UIDNotExistsError:
        return apiResponse( "No employee with given UID was found", 400 )
    except DuplicateAttendanceError:
        return apiResponse( "Already marked", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Database Error", 500 )
    except Exception as e:
        print( traceback.print_exc() )
        return apiResponse( "Something went wrong", 500 )

@attendance.route( "/attendance/get/one/between", methods=["GET", "POST"] )
@threadSafe
@authenticate
@prepareDatetime
def getAttendanceOfOneBetweenHandler( **kwargs ):
    """
    This API is used to get the attendance of an employee between two given dates

    REQUEST :
    -------
    method : GET
    route : /attendance/get/one/between
    authentication : bearer token - jwt
    body : json
        {
            "uid" : "The employee id",
            "startdate" : "Local startdate in ISO format",
            "enddate" : "Local enddate in ISO format"
        }

    RESPONSE :
    --------
    csv file containing attendance records
    /OR/
    json : 
        {
            "message" : "message string"
        }
    """
    try:
        
        result = database.getAttendanceOf_between( uid = kwargs["uid"], startdate = kwargs["startdate"], enddate = kwargs["enddate"] )

        if result:
            
            result = sorted(result, key = lambda item: item['date'])
            responseFile = io.StringIO()
            respFileWriter = csv.writer(responseFile)
            respFileWriter.writerow( ["date", "attendance", "time"] )

            this_date = kwargs["startdate"]
            end_date = kwargs["enddate"]
            delta = datetime.timedelta(days=1)
            index = 0

            lt = len(result)

            while this_date <= end_date:
                if index < lt and this_date == result[index]["date"]:
                    if result[index]["present"]:
                        respFileWriter.writerow( [ this_date.strftime(const.DATE_FORMAT), "P", result[index]["time"].strftime(const.TIME_FORMAT ) ] )
                    else:
                        respFileWriter.writerow( [ this_date.strftime(const.DATE_FORMAT), "A", "0:0:0" ] )
                    index += 1
                else:
                    respFileWriter.writerow( [ this_date.strftime(const.DATE_FORMAT), "A", "0:0:0" ] )
                this_date += delta

            responseFile.seek(0)
            response_file = io.BytesIO( responseFile.read().encode("utf-8") )
            responseFile.close()
            return send_file( filename_or_fp=response_file, mimetype="text/csv", attachment_filename=kwargs["uid"]+"_attendance.csv" , as_attachment=True )
        else:
            return apiResponse( "Something went wrong", 500 )

    except KeyError as ke:
        print(ke)
        return apiResponse( "Invalid request parameters", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except UIDNotExistsError:
        return apiResponse( "No employee with given UID exists", 400 )
    except InvalidDateError:
        return apiResponse( "Invalid Dates", 400 )
    except Exception as e:
        print( traceback.format_exc() )
        return apiResponse( "Something went wrong", 500 )

@attendance.route( "/attendance/get/all/between", methods=["GET", "POST"] )
@threadSafe
@authenticate
@prepareDatetime
def getAttendanceOfAllBetweenHandler(**kwargs):
    """
    This API is used to get the attendance of all the employees between given dates

    REQUEST : 
    -------
    method : GET
    route : /attendance/get/all/between
    authentication : bearer token - jwt
    body : 
        {
            "startdate" : "Starting date in ISO format",
            "enddate" : "Ending date in ISO format"
        }
    
    RESPONSE : 
    --------
    csv file containing attendance records
    /OR/
    json :
        {
            "message" : "message string"
        }
    """
    try:
        
        result = database.getAttendanceAll_between( startdate = kwargs["startdate"], enddate = kwargs["enddate"] )

        if result:
            num_result = len(result)

            responseFile = io.StringIO()
            respFileWriter = csv.writer(responseFile)

            uidList = []
            dateList = []
            dateListInd = 0

            this_date = kwargs["startdate"]
            end_date = kwargs["enddate"]
            delta = datetime.timedelta( days=1 )
            resultListInd = 0

            num_uid = 0 

            # Getting the list of UIDs
            while this_date <= end_date:
                dateList.append( { "date" : this_date, "attendance" : [] } )
                if resultListInd < num_result and this_date == result[resultListInd]["date"]:

                    for uidAtt in result[resultListInd]["attendance"] :
                        try:
                            i = uidList.index( uidAtt["uid"] )
                            # UID already exists in the list, use the index
                            dateList[ dateListInd ]["attendance"].append( ( i , uidAtt["time"] ) )
                        except ValueError:
                            # UID does not exist in the list, append it to the list
                            uidList.append( uidAtt["uid"] )
                            num_uid += 1
                            dateList[ dateListInd ]["attendance"].append( ( num_uid-1 , uidAtt["time"] ) )

                    resultListInd += 1
                
                dateListInd += 1
                this_date += delta

            # Iterate over all uid and fill in the first row
            writeList = [ "date" ]
            for _uid in uidList:
                writeList.append( _uid )
            respFileWriter.writerow( writeList )

            # Iterate over all the dates
            for dateAtt in dateList:
                writeList = [ dateAtt["date"].strftime(const.DATE_FORMAT) ]
                writeList = writeList + ["A"]*num_uid
                for x in dateAtt["attendance"]:
                    # x[0] is the index of the present candidate and x[1] is the time
                    writeList[ x[0]+1 ] = x[1].time().strftime(const.TIME_FORMAT)
                respFileWriter.writerow( writeList )

            # Send the csv file to the client
            responseFile.seek(0)
            response_file = io.BytesIO( responseFile.read().encode("utf-8") )
            responseFile.close()
            return send_file( filename_or_fp=response_file, mimetype="text/csv", attachment_filename="attendance_" + kwargs["startdate"].strftime(const.DATE_FORMAT) + "_" + kwargs["enddate"].strftime(const.DATE_FORMAT) + ".csv" , as_attachment=True )
        else:
            return apiResponse( "Something went wrong", 500 )

    except KeyError as ke:
        print(ke)
        return apiResponse( "Invalid request parameters", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except InvalidDateError:
        return apiResponse( "Invalid Dates", 400 )
    except Exception as e:
        print( traceback.format_exc() )
        return apiResponse( "Something went wrong", 500 )

@attendance.route( "/attendance/deleterecord/one", methods=["DELETE"] )
@threadSafe
@authenticate
@prepareDatetime
def deleteOneRecordHandler(**kwargs):
    """
    This API is used to delete all attendace records from the database, for a given date

    REQUEST :
    -------
    method : DELETE
    route : /attendance/deleterecord/one
    authentication : bearer token - jwt
    body : json
        {
            "date" : "local date in ISO format"
        }
    
    RESPONSE : json
    --------
        {
            "message" : "message string"
        }
    """
    try:

        if not database.clearAttendanceRecordFor( date=kwargs["date"] ):
            raise Exception

        return apiResponse( "Deleted attendance record", 200 )
    
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except InvalidDateError:
        return apiResponse( "Invalid date", 400 )
    except DateDoesNotExistsError:
        return apiResponse( "No record for given date was found", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Database Error", 500 )
    except Exception as e:
        return apiResponse( "Something went wrong", 500 )


@attendance.route( "/attendance/deleterecord/all", methods=["DELETE"] )
@threadSafe
@authenticate
def deleteAllRecordsHandler(**kwargs):
    """
    This API is used to delete all attendance records from the database

    REQUEST :
    -------
    method : DELETE
    route : /attendance/deleterecord/all
    authentication : bearer token - jwt
    body : none

    RESPONSE : json
    --------
        {
            "message" : "message string"
        }
    """
    try:
        if database.clearAttendanceRecords():
            return apiResponse( "Deleted all attendance records", 200 )
        else:
            return apiResponse( "Failed", 500 )
    except DateDoesNotExistsError:
        return apiResponse( "No record in the database", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Database error", 500 )
    except Exception as e:
        return apiResponse( "Something went wrong", 500 )

# ----------------------------------------------------------------------------------------------------------------------