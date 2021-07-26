import base64
import copy

from saml2.config import SPConfig
from djangosaml2sp.mxins.SPConfigMixin import SPConfigViewMixin
from djangosaml2sp.overrides import Saml2Client
from djangosaml2sp.cache import IdentityCache, OutstandingQueriesCache
import logging
import saml2

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import (HttpRequest, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.module_loading import import_string
from saml2.response import (RequestVersionTooLow,
                            SignatureError, StatusAuthnFailed, StatusError,
                            StatusNoAuthnContext, StatusRequestDenied,
                            UnsolicitedResponse)
from saml2.saml import SCM_BEARER
from saml2.sigver import MissingKey
from saml2.validate import ResponseLifetimeExceed, ToEarly
from saml2.ident import code

from djangosaml2sp.sp import SP
from djangosaml2sp.utils import get_fallback_login_redirect_url, validate_referral_url

logger = logging.getLogger(__name__)


def _set_subject_id(session, subject_id):
    session['_saml2_subject_id'] = code(subject_id)


@method_decorator(csrf_exempt, name='dispatch')
class AssertionConsumerService(View):
    """ The IdP will send its response to this view, which will process it using pysaml2 and
        log the user in using whatever SAML authentication backend has been enabled in
        settings.py. The `djangosaml2.backends.Saml2Backend` can be used for this purpose,
        though some implementations may instead register their own subclasses of Saml2Backend.
    """

    def custom_validation(self, response):
        """
        自定义验证
        """
        pass

    def handle_acs_failure(self, request, exception=None, status=403, **kwargs):  # pylint: disable=no-self-use
        """ Error handler if the login attempt fails. Override this to customize the error response.
        """

        # Backwards compatibility: if a custom setting was defined, use that one
        custom_failure_function = getattr(
            settings,
            'SAML_ACS_FAILURE_RESPONSE_FUNCTION'
        )
        if custom_failure_function:
            failure_function = custom_failure_function if callable(
                custom_failure_function
            ) else import_string(custom_failure_function)
            return failure_function(request, exception, status, **kwargs)

        return render(request, 'djangosaml2/login_error.html', {'exception': exception}, status=status)

    def post(self, request, tenant_uuid, attribute_mapping=None, create_unknown_user=None):
        """ SAML Authorization Response endpoint
        """

        if 'SAMLResponse' not in request.POST:
            logger.warning('Missing "SAMLResponse" parameter in POST data.')
            return HttpResponseBadRequest('Missing "SAMLResponse" parameter in POST data.')

        attribute_mapping = attribute_mapping or getattr(
            settings,
            'SAML_ATTRIBUTE_MAPPING',
            {
                'uid': ('username', )
            }
        )
        create_unknown_user = create_unknown_user or getattr(
            settings,
            'SAML_CREATE_UNKNOWN_USER',
            True
        )

        conf = SPConfig()
        conf.load(copy.deepcopy(SP.construct_metadata(tenant_uuid)))

        identity_cache = IdentityCache(request.session)
        client = Saml2Client(conf, identity_cache=identity_cache)
        oq_cache = OutstandingQueriesCache(request.session)
        oq_cache.sync()
        outstanding_queries = oq_cache.outstanding_queries()

        _exception = None
        try:
            response = client.parse_authn_request_response(
                request.POST['SAMLResponse'],
                saml2.BINDING_HTTP_POST,
                outstanding_queries
            )
        except (StatusError, ToEarly) as err:
            _exception = err
            logger.exception("Error processing SAML Assertion.")
        except ResponseLifetimeExceed as err:
            _exception = err
            logger.info(
                ("SAML Assertion is no longer valid. Possibly caused "
                 "by network delay or replay attack."), exc_info=True)
        except SignatureError as err:
            _exception = err
            logger.info("Invalid or malformed SAML Assertion.", exc_info=True)
        except StatusAuthnFailed as err:
            _exception = err
            logger.info("Authentication denied for user by IdP.",
                        exc_info=True)
        except StatusRequestDenied as err:
            _exception = err
            logger.warning("Authentication interrupted at IdP.", exc_info=True)
        except StatusNoAuthnContext as err:
            _exception = err
            logger.warning(
                "Missing Authentication Context from IdP.", exc_info=True)
        except MissingKey as err:
            _exception = err
            logger.exception(
                "SAML Identity Provider is not configured correctly: certificate key is missing!")
        except UnsolicitedResponse as err:
            _exception = err
            logger.exception(
                "Received SAMLResponse when no request has been made.")
        except RequestVersionTooLow as err:
            _exception = err
            logger.exception(
                "Received SAMLResponse have a deprecated SAML2 VERSION.")
        except Exception as err:
            _exception = err
            logger.exception("SAMLResponse Error")

        if _exception:
            return self.handle_acs_failure(request, exception=_exception)
        elif response is None:
            logger.warning("Invalid SAML Assertion received (unknown error).")
            return self.handle_acs_failure(request, status=400, exception=SuspiciousOperation('Unknown SAML2 error'))

        try:
            self.custom_validation(response)
        except Exception as err:
            logger.warning(f"SAML Response validation error: {err}")
            return self.handle_acs_failure(request, status=400, exception=SuspiciousOperation('SAML2 validation error'))

        session_id = response.session_id()
        oq_cache.delete(session_id)

        # authenticate the remote user
        session_info = response.session_info()

        # assertion_info
        assertion = response.assertion
        assertion_info = {}
        for sc in assertion.subject.subject_confirmation:
            if sc.method == SCM_BEARER:
                assertion_not_on_or_after = sc.subject_confirmation_data.not_on_or_after
                assertion_info = {'assertion_id': assertion.id,
                                  'not_on_or_after': assertion_not_on_or_after}
                break

        if callable(attribute_mapping):
            attribute_mapping = attribute_mapping()
        if callable(create_unknown_user):
            create_unknown_user = create_unknown_user()

        logger.debug(
            'Trying to authenticate the user. Session info: %s', session_info)
        user = auth.authenticate(
            request=request,
            session_info=session_info,
            attribute_mapping=attribute_mapping,
            create_unknown_user=create_unknown_user,
            assertion_info=assertion_info
        )
        if user is None:
            logger.warning(
                "Could not authenticate user received in SAML Assertion. Session info: %s", session_info)
            return self.handle_acs_failure(request, exception=PermissionDenied('No user could be authenticated.'),
                                           session_info=session_info)

        auth.login(self.request, user)
        _set_subject_id(request.saml_session, session_info['name_id'])
        logger.debug("User %s authenticated via SSO.", user)

        self.post_login_hook(request, user, session_info)
        self.customize_session(user, session_info)

        relay_state = self.build_relay_state()
        custom_redirect_url = self.custom_redirect(
            user,
            relay_state,
            session_info
        )
        if custom_redirect_url:
            return HttpResponseRedirect(custom_redirect_url)
        relay_state = validate_referral_url(request, relay_state)
        logger.debug('Redirecting to the RelayState: %s', relay_state)
        return HttpResponseRedirect(relay_state)

    def post_login_hook(self, request: HttpRequest, user: settings.AUTH_USER_MODEL, session_info: dict) -> None:
        """ If desired, a hook to add logic after a user has succesfully logged in.
        """

    def build_relay_state(self) -> str:
        """ The relay state is a URL used to redirect the user to the view where they came from.
        """
        default_relay_state = get_fallback_login_redirect_url()
        relay_state = self.request.POST.get('RelayState', default_relay_state)
        relay_state = self.customize_relay_state(relay_state)
        if not relay_state:
            logger.warning('The RelayState parameter exists but is empty')
            relay_state = default_relay_state
        return relay_state

    def customize_session(self, user, session_info: dict):
        """ Subclasses can use this for customized functionality around user sessions.
        """

    def customize_relay_state(self, relay_state: str) -> str:
        """ Subclasses may override this method to implement custom logic for relay state.
        """
        return relay_state

    def custom_redirect(self, user, relay_state: str, session_info) -> str:
        """ Subclasses may override this method to implement custom logic for redirect.

            For example, some sites may require user registration if the user has not
            yet been provisioned.
        """
        return None
