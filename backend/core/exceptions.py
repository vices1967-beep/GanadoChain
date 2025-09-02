from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the error response
        response.data = {
            'error': {
                'code': response.status_code,
                'message': response.data.get('detail', 'An error occurred'),
                'details': response.data
            }
        }
    else:
        # For unhandled exceptions
        response = Response(
            {
                'error': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'message': 'Internal server error',
                    'details': str(exc)
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response