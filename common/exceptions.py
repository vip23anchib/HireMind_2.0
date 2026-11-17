"""
Custom DRF Exception Handler.
Formats all API error responses into standardized, predictable JSON envelopes.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Returns standardized error response envelope:
    {
        "status_code": 400,
        "error_code": "VALIDATION_ERROR",
        "message": "Human readable summary",
        "details": { field: [errors] }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_code = getattr(exc, 'default_code', 'API_ERROR').upper()
        if response.status_code == 400:
            error_code = 'VALIDATION_ERROR'
        elif response.status_code == 401:
            error_code = 'UNAUTHORIZED'
        elif response.status_code == 403:
            error_code = 'PERMISSION_DENIED'
        elif response.status_code == 404:
            error_code = 'NOT_FOUND'

        message = "An error occurred while processing your request."
        details = response.data

        if isinstance(response.data, dict):
            if 'detail' in response.data:
                message = str(response.data['detail'])
            elif response.data:
                first_key = next(iter(response.data))
                first_val = response.data[first_key]
                if isinstance(first_val, list) and first_val:
                    message = f"{first_key}: {first_val[0]}"
                else:
                    message = f"{first_key}: {first_val}"
        elif isinstance(response.data, list) and response.data:
            message = str(response.data[0])

        response.data = {
            "status_code": response.status_code,
            "error_code": error_code,
            "message": message,
            "details": details,
        }
    else:
        # Unhandled 500 error
        logger.exception("Unhandled server exception: %s", exc)
        response = Response(
            {
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later.",
                "details": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
