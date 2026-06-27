from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import InvalidToken

from core.constants import (
    DEFAULT_ERROR_RESPONSE_FIELDS,
    EXPIRED_SIGNATURE_CODE,
    SIGNATURE_EXPIRED_MESSAGE,
)


def _invalid_token_message(exception):
    detail = exception.detail
    if isinstance(detail, dict):
        value = detail.get('detail', detail)
        if isinstance(value, list):
            return str(value[0])
        return str(value)
    if isinstance(detail, list):
        return str(detail[0])
    return str(detail)


class CargoPortalAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, code, detail, status_code=None, scope='global'):
        super().__init__(detail=detail, code=code)
        self.scope = scope
        if status_code is not None:
            self.status_code = status_code

    def get_full_details(self):
        details = super().get_full_details()
        details['scope'] = self.scope
        return details


def get_error_scope(error_data):
    if isinstance(error_data, dict) and set(error_data.keys()) - DEFAULT_ERROR_RESPONSE_FIELDS:
        return 'field'
    return 'global'


def custom_exception_handler(exception, context):
    """
    Format API errors in a consistent envelope, similar to GravtyAPIExceptionHandler.
    """
    response = exception_handler(exception, context)

    if response is not None and isinstance(exception, InvalidToken):
        if _invalid_token_message(exception) == SIGNATURE_EXPIRED_MESSAGE:
            response.data = {
                'error': SIGNATURE_EXPIRED_MESSAGE,
                'code': EXPIRED_SIGNATURE_CODE,
            }
            return response

    if response is not None and isinstance(exception, APIException):
        data = exception.get_full_details()
        if isinstance(data, dict) and not data.get('scope'):
            data['scope'] = get_error_scope(data)
        response.data = {'error': data}
        return response

    if isinstance(exception, DjangoValidationError):
        if hasattr(exception, 'error_dict'):
            error = ValidationError(exception.error_dict)
        else:
            error = ValidationError(exception.error_list)
        data = error.get_full_details()
        if isinstance(data, dict) and not data.get('scope'):
            data['scope'] = get_error_scope(data)
        return Response({'error': data}, status=status.HTTP_400_BAD_REQUEST)

    return response
