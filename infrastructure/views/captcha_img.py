'''
views for captcha
- get captcha
- check captcha
'''
from captcha.fields import CaptchaField
from captcha.models import CaptchaStore
from rest_framework import views
from rest_framework.response import Response
from django.urls import reverse
from django.http.response import HttpResponseBadRequest
from django.forms import ValidationError


def check_captcha(captcha_code, captcha_key):
    '''
    :param str captcha_code: 来自用户输入
    :param str captcha_key: 随图片一起返回的key
    :rtype: bool
    '''
    captcha_field = CaptchaField()
    try:
        captcha_field.clean([captcha_key, captcha_code])
        return True
    except ValidationError:
        return False


class CaptchaAPIView(views.APIView):
    '''
    captcha api
    '''

    authentication_classes = []
    permission_classes = []

    def get(self, request):    # pylint: disable=unused-argument, no-self-use
        '''
        get captcha
        '''
        captcha_key = CaptchaStore.generate_key()
        captcha_img = reverse('siteapi_oneid:infra:captcha-image', args=(captcha_key, ))
        return Response({'captcha_key': captcha_key, 'captcha_img': captcha_img})

    def post(self, request):    # pylint: disable=no-self-use
        '''
        check captcha
        '''
        captcha_code = request.data.get('captcha')
        captcha_key = request.data.get('captcha_key')
        if check_captcha(captcha_code, captcha_key):
            return Response('captcha is valid')

        return HttpResponseBadRequest('captcha is invalid')
