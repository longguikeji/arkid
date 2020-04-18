'''
demo for middleware plugin
'''

from rest_framework.response import Response
from rest_framework import status


def block_admin(get_response):
    '''
    禁用 admin
    '''
    def middleware(request):
        user = request.user
        if user and user.is_authenticated and user.username == "admin":
            return Response(status=status.HTTP_403_FORBIDDEN)

        response = get_response(request)

        return response

    return middleware
