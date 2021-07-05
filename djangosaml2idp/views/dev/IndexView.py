from django.views import View
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

@method_decorator(never_cache, name='dispatch')
class IndexView(View):
    """
    SAML2.0  IDP默认页面
    """
    def get(self, request,tenant_uuid,app_id):    # pylint: disable=no-self-use
        res = self.check_login(request,tenant_uuid,app_id)
        
        if res:
            return res
            
        res =  redirect(reverse("api:saml2idp:response", args=[tenant_uuid,app_id]))
        res.set_cookie("spauthn",request.GET['spauthn'])
        return res

    def check_login(self,request,tenant_uuid,app_id):
        try:
            from rest_framework.authtoken.models import Token
            spauthn = request.GET['spauthn']
            token = Token.objects.get(key=spauthn)
            if token:
                return
        except Exception:    # pylint: disable=broad-except
            if not request.user.is_anonymous:
                print(type(request.user))
                return
        
        return redirect(reverse("api:saml2idp:dev_mock_login", args=[tenant_uuid, app_id]))