'''
django saml error views
'''
from django.views.generic import TemplateView


class SamlIDPErrorView(TemplateView):
    """ Default error view when a 'known' error occurs in the saml2 authentication views.
    """
    template_name = 'djangosaml2idp/error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exception = kwargs.get("exception")

        context.update({
            "exception_type": exception.__class__.__name__ if exception else None,
            "exception_msg": str(exception) if exception else None,
            "extra_message": kwargs.get("extra_message"),
        })
        return context
