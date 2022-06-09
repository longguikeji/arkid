"""
SAML2.0 sp
"""
import copy
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from saml2.config import SPConfig
from saml2.metadata import entity_descriptor
from saml2.server import Server
from djangosaml2sp.spsettings import get_saml_sp_config
from djangosaml2sp.certs import create_self_signed_cert


class SP:
    """ Access point for the SP Server instance
    """
    _server_instance: Server = None

    @classmethod
    def construct_metadata(cls, tenant_uuid, with_local_sp: bool = True) -> dict:  # pylint: disable=unused-argument
        """ Get the config including the metadata for all the configured service providers. """
        saml_sp_config = get_saml_sp_config(tenant_uuid)
        sp_config = copy.deepcopy(saml_sp_config)
        return sp_config

    @classmethod
    def load(cls, tenant_uuid, force_refresh: bool = False) -> Server:
        """ Instantiate a SP Server instance based on the config defined in the SAML_SP_CONFIG settings.
            Throws an ImproperlyConfigured exception if it could not do so for any reason.
        """
        if cls._server_instance is None or force_refresh:
            conf = SPConfig()
            md = cls.construct_metadata(  # pylint: disable=invalid-name
                tenant_uuid
            )
            try:
                conf.load(md)
                cls._server_instance = Server(config=conf)
            except Exception as err:
                raise ImproperlyConfigured(  # pylint: disable=raise-missing-from
                    _(
                        'Could not instantiate an SP based on the SAML_SP_CONFIG settings and configured ServiceProviders: {}'
                    ).format(
                        str(err)
                    )
                )
        return cls._server_instance

    @classmethod
    def metadata(cls, tenant_uuid) -> str:
        """ Get the SP metadata as a string. """
        create_self_signed_cert(tenant_uuid)

        conf = SPConfig()
        try:
            conf.load(cls.construct_metadata(
                tenant_uuid, with_local_sp=False))
            metadata = entity_descriptor(conf)
        except Exception as err:
            raise ImproperlyConfigured(  # pylint: disable=raise-missing-from
                _(
                    'Could not instantiate SP metadata based on the SAML_SP_CONFIG settings and configured ServiceProviders: {}'
                ).format(
                    str(err)
                )
            )
        return str(metadata)
