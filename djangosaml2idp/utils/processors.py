import logging
from typing import Dict, Type
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from .NameIdBuilder import NameIdBuilder

logger = logging.getLogger(__name__)

User = get_user_model()


class BaseProcessor:
    """ Processor class is used to:
        - determine if a user has access to a client service of this IDP
        - construct the identity dictionary which is sent to the SP
        Subclass this to provide your own desired behaviour.
    """

    def __init__(self, entity_id: str):
        self._entity_id = entity_id

    def has_access(self, request) -> bool:
        """ Check if this user is allowed to use this IDP
        """
        return True

    def enable_multifactor(self, user) -> bool:
        """ Check if this user should use a second authentication system
        """
        return False

    def get_user_id(self, user, name_id_format: str, service_provider: ServiceProvider, idp_config) -> str:
        """ Get identifier for a user.
        """
        user_field_str = service_provider.nameid_field
        user_field = getattr(user, user_field_str)

        if callable(user_field):
            user_id = str(user_field())
        else:
            user_id = str(user_field)

        # returns in a real name_id format
        return NameIdBuilder.get_nameid(user_id, name_id_format, sp=service_provider, user=user)

    def create_identity(self, user, sp_attribute_mapping: Dict[str, str]) -> Dict[str, str]:
        """ Generate an identity dictionary of the user based on the
            given mapping of desired user attributes by the SP
        """
        results = {}
        for user_attr, out_attr in sp_attribute_mapping.items():
            if hasattr(user, user_attr):
                attr = getattr(user, user_attr)
                results[out_attr] = attr() if callable(attr) else attr
        return results


def validate_processor_path(processor_class_path: str) -> Type[BaseProcessor]:
    try:
        processor_cls = import_string(processor_class_path)
    except ImportError as e:
        msg = _("Failed to import processor class {}").format(
            processor_class_path)
        logger.error(msg, exc_info=True)
        raise ValidationError(msg) from e
    return processor_cls


def instantiate_processor(processor_cls: Type[BaseProcessor], entity_id: str) -> BaseProcessor:
    try:
        processor_instance = processor_cls(entity_id)  # type: ignore
    except Exception as e:
        msg = _("Failed to instantiate processor: {} - {}").format(processor_cls, e)
        logger.error(msg, exc_info=True)
        raise ImproperlyConfigured(msg) from e
    if not isinstance(processor_instance, BaseProcessor):
        raise ValidationError(
            '{} should be a subclass of djangosaml2idp.processors.BaseProcessor'.format(processor_cls))
    return processor_instance  # type: ignore
