from runtime import Runtime
from common.extension import InMemExtension
from common.provider import MFAProvider
# import pyotp
from django.http.response import HttpResponseRedirect


class OTPMFAProvider(MFAProvider):

    def setup(self):
        # '''
        # 1. 
        # '''
        # secret = pyotp.random_base32()
        return HttpResponseRedirect('/')

    def trigger(self):
        '''
        1. 渲染 /
        2. 
        '''
        pass

    def verify(self, *args, **kwargs):
        '''
        检查
        '''
        pass


class OTPMFAExtension(InMemExtension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        super().start(runtime=runtime, *args, **kwargs)


extension = OTPMFAExtension(
    name='otp_mfa',
    description='demonstration only',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)
