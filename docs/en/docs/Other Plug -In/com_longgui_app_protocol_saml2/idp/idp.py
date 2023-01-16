"""
SAML2.0 idp
"""
import copy
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from saml2.config import IdPConfig
from saml2.metadata import entity_descriptor
from saml2.server import Server
from .idpsettings import get_saml_idp_config


class IDP:
    """ Access point for the IDP Server instance
    """
    _server_instance: Server = None

    @classmethod
    def construct_metadata(cls, tenant_uuid, app_id, with_local_sp: bool = True) -> dict:  # pylint: disable=unused-argument
        """ Get the config including the metadata for all the configured service providers. """
        saml_idp_config = get_saml_idp_config(tenant_uuid, app_id)
        idp_config = copy.deepcopy(saml_idp_config)
        return idp_config

    @classmethod
    def load(cls, tenant_uuid, app_id, force_refresh: bool = False) -> Server:
        """ Instantiate a IDP Server instance based on the config defined in the SAML_IDP_CONFIG settings.
            Throws an ImproperlyConfigured exception if it could not do so for any reason.
        """
        if cls._server_instance is None or force_refresh:
            conf = IdPConfig()
            md = cls.construct_metadata(  # pylint: disable=invalid-name
                tenant_uuid,
                app_id
            )
            try:
                conf.load(md)
                cls._server_instance = Server(config=conf)
            except Exception as err:
                raise ImproperlyConfigured(  # pylint: disable=raise-missing-from
                    _(
                        'Could not instantiate an IDP based on the SAML_IDP_CONFIG settings and configured ServiceProviders: {}'
                    ).format(
                        str(err)
                    )
                )
        return cls._server_instance

    @classmethod
    def metadata(cls, tenant_uuid, app_id) -> str:
        """ Get the IDP metadata as a string. """
        conf = IdPConfig()
        try:
            conf.load(
                cls.construct_metadata(
                    tenant_uuid, 
                    app_id, 
                    with_local_sp=False
                )
            )
            metadata = entity_descriptor(conf)
        except Exception as err:
            raise ImproperlyConfigured( # pylint: disable=raise-missing-from
                _(
                    'Could not instantiate IDP metadata based on the SAML_IDP_CONFIG settings and configured ServiceProviders: {}'
                ).format(
                    str(err)
                )
            )
        return str(metadata)
