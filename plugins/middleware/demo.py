'''
demo for middleware plugin
'''

from django.http.response import HttpResponseForbidden


def localhostonly_plugin(get_response):
    '''
    只允许从 localhost 访问
    '''
    def middleware(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if ip != "127.0.0.1":
            return HttpResponseForbidden()

        response = get_response(request)

        return response

    return middleware
