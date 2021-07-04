from django.http.response import HttpResponseBadRequest, HttpResponseRedirect
from django.urls.base import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT

@method_decorator(never_cache, name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
class SSOEntry(View):

    def get(self,request,tenant_uuid,app_id):
        passed_data = request.GET
        binding = BINDING_HTTP_REDIRECT

        return self.make_response(request,passed_data,binding)

    def post(self, request,tenant_uuid,app_id):
        passed_data = request.POST
        binding = BINDING_HTTP_POST
        return self.make_response(request,passed_data,binding)


    def make_response(self,request,passed_data,binding):
        request.session['Binding'] = binding
        try:
            request.session['SAMLRequest'] = passed_data['SAMLRequest']
        except (KeyError, MultiValueDictKeyError) as e:    # pylint: disable=invalid-name
            return HttpResponseBadRequest(e)
        request.session['RelayState'] = passed_data.get('RelayState', '')
        # TODO check how the redirect saml way works. Taken from example idp in pysaml2.
        if "SigAlg" in passed_data and "Signature" in passed_data:
            request.session['SigAlg'] = passed_data['SigAlg']
            request.session['Signature'] = passed_data['Signature']
        return HttpResponseRedirect(reverse('djangosaml2idp:saml_login_process'))