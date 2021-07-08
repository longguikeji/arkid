"""
SAML2协议 收集需要的参数并写入session
"""
from django.utils.datastructures import MultiValueDictKeyError
from django.http.request import HttpRequest
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

def store_params_in_session(request: HttpRequest, passed_data, binding) -> None:
    """ Gathers the SAML parameters from the HTTP request and store them in the session
    """
    try:
        saml_request = passed_data['SAMLRequest']
    except (KeyError, MultiValueDictKeyError) as err:
        raise ValidationError( # pylint: disable=raise-missing-from
            _('not a valid SAMLRequest: {}').format(repr(err))
        )

    request.session['Binding'] = binding
    request.session['SAMLRequest'] = saml_request
    request.session['RelayState'] = passed_data.get('RelayState', '')
    