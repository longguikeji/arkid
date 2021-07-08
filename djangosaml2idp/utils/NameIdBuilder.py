import hashlib
import logging

from django.conf import settings
from django.utils.translation import gettext as _
from saml2.saml import (NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_ENCRYPTED,
                        NAMEID_FORMAT_ENTITY, NAMEID_FORMAT_KERBEROS,
                        NAMEID_FORMAT_PERSISTENT, NAMEID_FORMAT_TRANSIENT,
                        NAMEID_FORMAT_UNSPECIFIED,
                        NAMEID_FORMAT_WINDOWSDOMAINQUALIFIEDNAME,
                        NAMEID_FORMAT_X509SUBJECTNAME)

logger = logging.getLogger(__name__)

class NameIdBuilder:
    """ Processor with methods to retrieve nameID standard format
        see: https://wiki.shibboleth.net/confluence/display/CONCEPT/NameIdentifiers
    """

    format_mappings = {
        NAMEID_FORMAT_UNSPECIFIED: 'get_nameid_unspecified',
        NAMEID_FORMAT_TRANSIENT: 'get_nameid_transient',
        NAMEID_FORMAT_PERSISTENT: 'get_nameid_persistent',
        NAMEID_FORMAT_EMAILADDRESS: 'get_nameid_email',
        # TODO: need to be implemented
        NAMEID_FORMAT_X509SUBJECTNAME: None,
        NAMEID_FORMAT_WINDOWSDOMAINQUALIFIEDNAME: None,
        NAMEID_FORMAT_KERBEROS: None,
        NAMEID_FORMAT_ENTITY: None,
        NAMEID_FORMAT_ENCRYPTED: None
    }

    @classmethod
    def _get_nameid_opaque(cls, user_id: str, salt: bytes = b'', *args, **kwargs) -> str:
        """ Returns opaque salted unique identifiers
        """
        salted_value = user_id.encode() + salt
        opaque = hashlib.sha256(salted_value)
        return opaque.hexdigest()

    @classmethod
    def get_nameid_persistent(cls, user_id: str, sp: ServiceProvider, user: settings.AUTH_USER_MODEL, *args, **kwargs) -> str:
        """ Get PersistentID in TransientID format
            see: http://software.internet2.edu/eduperson/internet2-mace-dir-eduperson-201602.html#eduPersonTargetedID
        """
        return str(PersistentId.objects.get_or_create(sp=sp, user=user)[0].persistent_id)

    @classmethod
    def get_nameid_email(cls, user_id: str, user: settings.AUTH_USER_MODEL = None, **kwargs) -> str:
        if '@' not in user_id:
            raise Exception(f"user_id {user_id} does not contain the '@' symbol, so is not a valid NameID Email address format.")
        return user_id

    @classmethod
    def get_nameid_transient(cls, user_id: str, **kwargs) -> str:
        """ This would return EPPN
        """
        raise NotImplementedError('Not implemented yet')

    @classmethod
    def get_nameid_unspecified(cls, user_id: str, **kwargs) -> str:
        """ returns user_id as is
        """
        return user_id

    @classmethod
    def get_nameid(cls, user_id: str, nameid_format: str, **kwargs) -> str:
        method = cls.format_mappings.get(nameid_format)
        if not method:
            raise NotImplementedError(f'{nameid_format} has not been mapped in NameIdBuilder.format_mappings')
        if not hasattr(cls, method):
            raise NotImplementedError(f'{nameid_format} has not been implemented NameIdBuilder methods')
        name_id = getattr(cls, method)(user_id, **kwargs)
        return name_id