"""
@author : Ashutosh Singh Parmar
@file : exceptions.py
@brief : This file contains custom exception classes used by other modules in this package
"""

class InvalidUIDError(Exception):
    """
    This exception is used to indicate an invalid employee UID
    """
    pass

class InvalidNameError(Exception):
    """
    This exception is used to indicate an invalid employee name
    """
    pass

class InvalidGenderError(Exception):
    """
    This exception is used to indicate an invalid gender data
    """
    pass

class InvalidEmailError(Exception):
    """
    This exception is used to indicate an invalid email
    """
    pass

class InvalidImageDataError(Exception):
    """
    This exception is used to indicate an invalid image data
    """
    pass

class ImageTooBigError(Exception):
    """
    This exception is used to indicate that image size is too large
    """
    pass

class UnsupportedImageTypeError(Exception):
    """
    This exception is used to indicate an invalid image type
    """
    pass

class InvalidDateError(Exception):
    """
    This exception is used to indicate an invalid date object
    """
    pass

class DateDoesNotExistsError(Exception):
    """
    This exception is used to indicate that date does not exist in database
    """

class InvalidDatetimeError(Exception):
    """
    This exception is used to indicate an invalid datetime object
    """
    pass

class UIDNotExistsError(Exception):
    """
    This exception is used to indicate that uid does not exist  in database
    """
    pass

class DuplicateAttendanceError(Exception):
    """
    This exception is used to indicate that attendance is being remarked
    """
    pass

class NoValueError(Exception):
    """
    This exception is used to indicate that none of the required arguments where passed to a function
    """
    pass

class threadError(Exception):
    pass