"""
SAML2IDPError
"""
import logging
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class SAML2IDPError(TemplateView):
    """ Default error view used when a 'known' error occurs in the saml2 authentication views.
        Subclass this to use your own template and styling for the error page (only set template_name on your subclass),
        or to do entirely customized error handling (override the handle_error method).
        settings.SAML_IDP_ERROR_VIEW_CLASS should point to your customized subclass.
    """
    template_name = 'saml2/error.html'

    @classmethod
    def handle_error(cls, request: HttpRequest, exception: Exception, status_code: int = 500, **kwargs) -> HttpResponse:
        """ Default behaviour: log the exception as error-level, and render an error page with the desired status_code on the response. """
        logger.error(kwargs, exc_info=exception)

        # Render an http response and return it
        response = cls.as_view()(request, exception=exception, **kwargs)
        response.status_code = status_code
        return response

    def get_context_data(self, **kwargs) -> dict:
        """ Add some exception-related variables to the context for usage in the template. """
        context = super().get_context_data(**kwargs)
        exception = kwargs.get("exception")

        context.update({
            "exception": exception,
            "exception_type": exception.__class__.__name__ if exception else None,
            "exception_msg": exception.message if exception and hasattr(exception, 'message') else str(exception) if exception else None,
            "extra_message": kwargs.get("extra_message"),
        })
        return context
