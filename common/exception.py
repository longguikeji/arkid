from rest_framework.exceptions import APIException
from rest_framework import status


class DuplicatedIdException(Exception):

    pass


class ValidationFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        self.detail = detail
