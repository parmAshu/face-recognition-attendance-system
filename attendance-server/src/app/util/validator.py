"""
@author : Ashutosh Singh Parmar
@file : validator.py
@brief : This file contains functions that are used for validating input arguments in database.py module
"""
from util import exceptions
import util.constants as cnst

def uidValidator(fun):
    """
    This is a decorator function which validates the uid data
    """
    def inner(**kwargs):
        if str(type(kwargs["uid"])) != cnst.CLASS_UID or len(kwargs["uid"]) < cnst.MIN_UID or len(kwargs["uid"]) > cnst.MAX_UID :
            raise exceptions.InvalidUIDError
        return fun(**kwargs)
    return inner

def firstnameValidator(fun):
    """
    This is a decorator function which validates the firstname data
    """
    def inner(**kwargs):
        if str(type(kwargs["firstname"])) != cnst.CLASS_NAME :
            raise exceptions.InvalidNameError
        return fun(**kwargs)
    return inner

def lastnameValidator(fun):
    """
    This is a decorator function which validates the last name data
    """
    def inner(**kwargs):
        if str(type(kwargs["lastname"])) != cnst.CLASS_NAME :
            raise exceptions.InvalidNameError
        return fun(**kwargs)
    return inner

def genderValidator(fun):
    """
    This is a decorator function which validates the gender value
    """
    def inner(**kwargs):
        if str(type(kwargs["gender"])) != cnst.CLASS_GENDER or len(kwargs["gender"]) != cnst.LEN_GENDER_DATA or kwargs["gender"] not in ['M', 'F', 'O', 'A']:
            raise exceptions.InvalidGenderError
        return fun(**kwargs)
    return inner

def emailValidator(fun):
    """
    This is a decorator function which validates the email value
    """
    def inner(**kwargs):
        if str(type(kwargs["email"])) != cnst.CLASS_EMAIL :
            raise exceptions.InvalidEmailError
        return fun(**kwargs)
    return inner

def imageValidator(fun):
    """
    This is a decorator function which validates the image data
    """
    def inner(**kwargs):
        if str(type(kwargs["imgType"])) != cnst.CLASS_IMAGE_TYPE or kwargs["imgType"] not in cnst.SUPPORTED_IMAGE_TYPE:
            raise exceptions.UnsupportedImageTypeError
        elif str(type(kwargs["image"])) != cnst.CLASS_IMAGE:
            raise exceptions.InvalidImageDataError
        elif len(kwargs["image"]) > cnst.MAX_IMAGE:
            raise exceptions.ImageTooBigError
        return fun(**kwargs)
    return inner

def dateValidator(fun):
    """
    This is a decorator function which validates the date object
    """
    def inner(**kwargs):
        if str(type(kwargs["date"])) != cnst.CLASS_DATE :
            raise exceptions.InvalidDateError
        return fun(**kwargs)
    return inner

def dateValidator1(fun):
    """
    This is a decorator function which validates the start date and end date objects
    """
    def inner(**kwargs):
        if str(type(kwargs["startdate"])) != cnst.CLASS_DATE or str(type(kwargs["enddate"])) != cnst.CLASS_DATE or kwargs["enddate"] < kwargs["startdate"] :
            raise exceptions.InvalidDateError
        return fun(**kwargs)
    return inner

def datetimeValidator(fun):
    """
    This is a decorator function which validates the datetime object
    """
    def inner(**kwargs):
        if str(type(kwargs["datetime"])) != cnst.CLASS_DATETIME :
            raise exceptions.InvalidDatetimeError
        return fun(**kwargs)
    return inner
    