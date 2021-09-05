"""
@author : Ashutosh Singh Parmar
@file : app/employees.py
@brief : This file contains APIs related to manage employee database
"""

import os, sys, traceback, io, pymongo
from functools import wraps
from flask import request, Response, make_response, send_file, jsonify, Blueprint

from util.exceptions import *
from util import database, constants as const

from serverDecorators import *

from session import *

employees = Blueprint( "employee", __name__ )

# APIS ---------------------------------------------------------------------------------------------------------------

@employees.route( "/employee/addone", methods=["POST"] )
@threadSafe
@authenticate
def addEmployeeHandler(**kwarg ):
    """
    This API is used to add an employee to the database

    REQUEST :
    -------
    method : POST
    route : /employee/addone
    authentication : token bearer - jwt
    body : form-data

        uid : Employee UID
        firstname : employee firstname
        lastname : employee lastname
        gender : employee gender ( M, F, O, A )
        email : employee email
        dob : date of birth of employee in the format : d/m/Y
        doj : date of joining of employee in the format : d/m/Y
        department : current department of employee
        title : current title of employee
        image : face image of the employee

    RESPONSE : json 
    --------
        {
            "message" : " ...message string... "
        }

    """
    try:
        data = {}
        for item in request.form.items():
            if item[0] == "uid":
                data["uid"] = item[1]
            elif item[0] == "firstname":
                data["firstname"] = item[1]
            elif item[0] == "lastname":
                data["lastname"] = item[1]
            elif item[0] == "gender":
                data["gender"] = item[1]
            elif item[0] == "email":
                data["email"] = item[1]
            elif item[0] == "dob":
                data["dob"] = datetime.datetime.strptime( item[1], const.DATE_FORMAT ).replace( hour = 0, minute = 0, second = 0, microsecond = 0)
            elif item[0] == "doj":
                data["doj"] = datetime.datetime.strptime( item[1], const.DATE_FORMAT ).replace( hour = 0, minute = 0, second = 0, microsecond = 0)
            elif item[0] == "department":
                data["department"] = item[1]
            elif item[0] == "title":
                data["title"] = item[1]
        
        im = request.files["image"]
        data["image"] = im.read()
        data["imgType"] = im.filename.split(".")[1]

        if database.addEmployee( **data ):
            return apiResponse( "Employee details added to database", 201 )
        else:
            return apiResponse( "Something went wrong", 500 )
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except ValueError as ve:
        if str(ve).__contains__("time data"):
            return apiResponse( "Invalid date format", 400 )
        else :
            return apiResponse( "Invalid request", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except InvalidNameError:
        return apiResponse( "Invald name", 400 )
    except InvalidGenderError:
        return apiResponse( "Invalid gender", 400 )
    except InvalidEmailError:
        return apiResponse( "Invalid email", 400 )
    except UnsupportedImageTypeError:
        return apiResponse( "Unsupported image type", 400 )
    except ImageTooBigError:
        return apiResponse( "Image size too large", 400 )
    except InvalidImageDataError:
        return apiResponse( "Invalid image", 400 )
    except pymongo.errors.DuplicateKeyError:
        return apiResponse( "An employee with same UID or email already exists in the database", 403 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Something went wrong", 500 )
    except Exception as e:
        print(e.__class__)
        return apiResponse( "Invalid request", 400 )

@employees.route( "/employee/removeone", methods=["DELETE"])
@threadSafe
@authenticate
def removeEmployeeHandler(**kwargs):
    """
    This API is used to remove an employee from the database

    REQUEST :
    -------
    method : DELETE
    route : /employee/removeone
    authentication : token bearer - jwt
    body : json
        {
            "uid" : "..valid employee UID..."
        }

    RESPONSE : json
    --------
        {
            "message" : " ...message string... "
        }
    """
    try:
        data = request.get_json()

        if database.removeEmployee( **data ):
            return apiResponse( "Employee details removed from database", 200 )
        else:
            return apiResponse( "Something went wrong", 500 )
    except KeyError:
        return apiResponse( "Invalid request", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except UIDNotExistsError:
        return apiResponse( "No employee with given UID exists",  400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Something went wrong", 500 )
    except Exception as e:
        return apiResponse( "Invalid request", 400 )

@employees.route( "/employee/updateone/details", methods=["PATCH"] )
@threadSafe
@authenticate
def updateEmployeeDetailsHandler(**kwargs):
    """
    This API is used to update details of an employee, in the database

    REQUEST : 
    -------
    method : PATCH
    route : /employee/updateone/details
    authentication : bearer token - jwt
    body : json
        {
            "uid" : " ...valid employee uid...",
            "email" : " ...valid employee email...",
            "department" : "...department of employee..."
            "title" : "...title of employee..."
        }

    RESPONSE : json
    --------
        {
            "message" : "...message string..."
        }
    """
    try:
        data = request.get_json()

        if database.updateEmployeeDetails( **data ):
            return apiResponse( "Employee details updated", 200 )
        else :
            return apiResponse( "Something went wrong", 500 )
    except KeyError:
        return apiResponse( "Invalid parameters", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except UIDNotExistsError:
        return apiResponse( "No employee with given UID exists", 400 )
    except InvalidEmailError:
        return apiResponse( "Invalid email", 400 )
    except NoValueError:
        return apiResponse( "Empty request", 400 )
    except pymongo.errors.DuplicateKeyError :
        return apiResponse( "Email address belongs to another employee", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Something went wrong", 500 )
    except Exception as e:
        return apiResponse( "Invalid request", 400 )

@employees.route( "/employee/updateone/image", methods=["PATCH"] )
@threadSafe
@authenticate
def updateEmployeeImageHandler(**kwargs):
    """
    This API is used to update the image of an employee in the database

    REQUEST : form-data
    -------
        uid : The employee uid
        image : The face image file

    RESPONSE : json
    --------
        {
            "message" : "...message string..."
        }
    """
    try:
        img = request.files["image"]
        img_type = img.filename.split(".")[1]
        
        _uid = request.form.to_dict()["uid"]

        if database.updateEmployeeImage( image = img.read(), uid =_uid, imgType = img_type ):
            return apiResponse( "Employee image updated", 200 )
        else:
            return apiResponse( "Something went wrong", 500 )
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except InvalidUIDError:
        return apiResponse("Invalid UID", 400 )
    except UIDNotExistsError:
        return apiResponse("No employee with given UID exists", 400 )
    except UnsupportedImageTypeError:
        return apiResponse( "Unsupported image type", 400 )
    except ImageTooBigError:
        return apiResponse( "Image size too large", 400 )
    except InvalidImageDataError:
        return apiResponse( "Invalid image", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Something went wrong", 500 )
    except Exception as e:
        return apiResponse( "Invalid request", 400 )

@employees.route( "/employee/getone/details", methods=["GET", "POST"] )
@threadSafe
@authenticate
def getEmployeeDetailsHandler(**kwargs):
    """
    This API is used to get the details of an employee from the database

    REQUEST : json
    -------
        {
            "uid" : "...employee uid..."
        }

    RESPONSE : json
    --------
        {
            "message" : "...success...",
            "details" : 
            {
                "uid" : "...employee uid...",
                "firstname" : "...first name of employee...",
                "lastname" : "...last name of employee...",
                .
                .
                .
            }
        }

        /OR/

        {
            "message" : "...message string..."
        }
    """
    try:
        data = request.get_json()

        result = database.getEmployeeDetails( **data )

        if result:
            result["DOJ"] = result["DOJ"].date().strftime( const.DATE_FORMAT )
            result["DOB"] = result["DOB"].date().strftime( const.DATE_FORMAT )
            return make_response( jsonify( { "message" : "success" , "details" : result } ), 200 )
        else:
            return apiResponse( "No employee with given UID found", 400 )
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Something went wrong", 500 )
    except Exception as e:
        traceback.print_exc()
        return apiResponse( "Invalid request", 400 )

@employees.route( "/employee/getone/image", methods=["GET"] )
@threadSafe
@authenticate
def getEmployeeImagehandler(**kwargs):
    """
    This API is used to get the image of an employee from the database

    REQUEST : json
    -------
        {
            "uid" : "...employee uid..."
        }

    RESPONSE :
    --------
        Image file with name - <employeeUID_image>.<extension>

        /OR/

        {
            "message" : "...message string..."
        }

    """
    try:
        data = { "uid" : request.args.get("uid") }
        #data = request.get_json()

        img = database.getEmployeeImage( **data )
        
        if img:
            img_type = img[1]
            img = img[0]
            return send_file( filename_or_fp=io.BytesIO(img), mimetype="image/"+img_type, as_attachment=True, attachment_filename=data["uid"]+str(int(datetime.datetime.utcnow().timestamp()))+"image."+img_type )
        else:
            return apiResponse( "No employee with given UID found", 400 )
    except KeyError:
        return apiResponse( "Invalid request parameters", 400 )
    except InvalidUIDError:
        return apiResponse( "Invalid UID", 400 )
    except pymongo.errors.ServerSelectionTimeoutError:
        return apiResponse( "Something went wrong", 500 )
    except Exception as e:
        traceback.print_exc()
        return apiResponse( "Invalid request", 400 )



#---------------------------------------------------------------------------------------------------------------------
