'''
检查是否有权限等
'''
from django.conf import settings


class BaseProcessor:
    """ Processor class is used to determine if a user has access to a client service of this IDP
        and to construct the identity dictionary which is sent to the SP
    """

    def __init__(self, entity_id):
        self._entity_id = entity_id

    def has_access(self, request):    # pylint: disable=no-self-use
        """
        TODO Check if this user is allowed to use this IDP
        """
        user = request.user
        return True

    def enable_multifactor(self, user):    # pylint: disable=unused-argument, no-self-use
        """ Check if this user should use a second authentication system
        """
        return False

    def get_user_id(self, user):    # pylint: disable=no-self-use
        """ Get identifier for a user. Take the one defined in settings.SAML_IDP_DJANGO_USERNAME_FIELD first, if not set
            use the USERNAME_FIELD property which is set on the user Model. This defaults to the user.username field.
        """
        user_field = getattr(settings, 'SAML_IDP_DJANGO_USERNAME_FIELD', None) or \
            getattr(user, 'USERNAME_FIELD', 'username')
        return str(getattr(user, user_field))

    def create_identity(self, user, sp_mapping, **extra_config):    # pylint: disable=no-self-use, unused-argument
        """ Generate an identity dictionary of the user based on the given mapping of desired user attributes by the SP
        """
        ret = {
            out_attr: getattr(user, user_attr)
            for user_attr, out_attr in sp_mapping.items() if hasattr(user, user_attr)
        }

        ret.update(extra_config)
        return ret
