
from asyncio.log import logger
import base64
import copy
import json
import os
import re
from typing_extensions import Self
import urllib
from urllib.parse import unquote, urlencode
from django.conf import settings
from arkid.config import get_app_config
from arkid.core.api import GlobalAuth, operation
from arkid.core.event import Event, dispatch_event
from arkid.core.extension.auth_factor import AuthFactorExtension
from arkid.core.models import User,UserGroup
from arkid.core.token import refresh_token
from arkid.extension.models import TenantExtension, TenantExtensionConfig
from arkid.core.constants import *
from arkid.core import pages,actions, routers
from arkid.core.translation import gettext_default as _
from .schema import *
from .error import ErrorCode
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_TRANSIENT
from saml2.sigver import get_xmlsec_binary
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.mdstore import MetaDataFile
from saml2.xmldsig import SIG_RSA_SHA256,DIGEST_SHA256
from OpenSSL import crypto
from socket import gethostname
from saml2.config import SPConfig
from saml2.metadata import entity_descriptor
from saml2.client import Saml2Client
from saml2.saml import AuthnContextClassRef
from saml2.samlp import RequestedAuthnContext
from django.core.exceptions import ImproperlyConfigured
from django.http.response import FileResponse,HttpResponseRedirect,HttpResponse
from saml2.samlp import AuthnRequest, IDPEntry, IDPList, Scoping
from django.shortcuts import render
from django.template import TemplateDoesNotExist

from saml2.response import (
    RequestVersionTooLow,
    SignatureError, 
    StatusAuthnFailed, 
    StatusError,
    StatusNoAuthnContext,
    StatusRequestDenied,
    UnsolicitedResponse
)
from django.shortcuts import redirect

class SAML2AuthFactorExtension(AuthFactorExtension):
    
    def load(self):
        super().load()
        self.create_self_signed_cert()
        self.register_extension_api()
        self.register_extension_config_schema()
    
    def register_extension_api(self):
        self.sp_metadata_file_path = self.register_api(
            "/sp/metadata/",
            "GET",
            self.get_sp_metadata_file,
            tenant_path=True,
            auth=None
        )
        
        self.acs_path = self.register_api(
            "/sp/acs/",
            "POST",
            self.acs,
            tenant_path=True,
            auth=None
        )
        
        
        self.login_path = self.register_api(
            "/sp/sso/login/",
            "POST",
            self.sso_login,
            tenant_path=True,
            auth=None,
            response=LoginOut
        )
    
    def register_extension_config_schema(self):
        SAML2SPConfigSchema = create_extension_schema(
            "SAML2SPConfigSchema",
            __file__,
            [
                (
                    "sp_metadata_file",
                    Optional[str],
                    Field(
                        title=_("SP元数据文件"),
                        readonly=True,
                        default=get_app_config().get_frontend_host() + self.sp_metadata_file_path,
                        format="download",
                    )
                )
            ],
            base_schema=ConfigSchema
        )
        
        self.register_auth_factor_schema(
            SAML2SPConfigSchema,
            "saml2.0"
        )
    
    def authenticate(self, event, **kwargs):
        pass
    
    def check_auth_data(self, event, **kwargs):
        return super().check_auth_data(event, **kwargs)
    
    def create_auth_manage_page(self):
        return super().create_auth_manage_page()
    
    def create_login_page(self, event, config, config_data):
        self.save_idp_metadata(config)
        items = [
            {
                "type": "text",
                "name": "tips",
                "placeholder": "提示",
                "value": "根据您的设置，您需要使用企业账号登录。",
                "readonly": True
            },
            {
                "type": "hidden",
                "name": "config_id",
                "value": config.id.hex,
            }
        ]
        
        config_data[self.LOGIN]['forms'].append({
            'label': config.name,
            'items': items,
            'submit': {'label': "登录", 'title':config.name, 'http': {'url': self.login_path, 'method': "post"}}
        })

        return super().create_login_page(event, config, config_data)
    
    def save_idp_metadata(self, config):
        BASEDIR = os.path.join(
            os.path.dirname(__file__),
            "saml2_config"
        )
        idp_metadata_file_path = os.path.join(BASEDIR,f"{config.id.hex}_idp.xml")
        # 处理传入的metadata文件并写入存储
        
        metadata = config.config["idp_xmldata_file"]
        
        if metadata:
            xmldata_file = metadata.replace("data:text/xml;base64,", "")
            xmldata = base64.b64decode(xmldata_file)
            xmldata = xmldata.decode()
                
            with open(idp_metadata_file_path,"w") as f:
                f.write(xmldata)
                
            idp_metadatafile = MetaDataFile(attrc=None, filename=idp_metadata_file_path)
            idp_metadatafile.load()
            idp_entity = idp_metadatafile.entity[list(idp_metadatafile.keys())[0]]
            
            config.config["idp_entity_id"] = idp_entity["entity_id"]
        config.save()
    
    def create_other_page(self, event, config, config_data):
        return super().create_other_page(event, config, config_data)
    
    def create_password_page(self, event, config, config_data):
        return super().create_password_page(event, config, config_data)
    
    def create_register_page(self, event, config, config_data):
        return super().create_register_page(event, config, config_data)
    
    def fix_login_page(self, event, **kwargs):
        return super().fix_login_page(event, **kwargs)
    
    def register(self, event, **kwargs):
        return super().register(event, **kwargs)
    
    def reset_password(self, event, **kwargs):
        return super().reset_password(event, **kwargs)
    
    def get_saml_sp_config(self,tenant_id):
        """
        创建SAML_SP_CONFIG
        """
        
        BASE_DIR = os.path.dirname(__file__)
        
        saml2_confi_path = os.path.join(
            BASE_DIR,
            "saml2_config"
        )
        
        if not os.path.exists(saml2_confi_path):
            os.mkdir(saml2_confi_path)
        
        saml_sp_config = {
            'debug': False,
            'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
            'entityid': get_app_config().get_frontend_host() + self.sp_metadata_file_path.format(tenant_id=tenant_id),
            'description':'longguikeji SAML2 SP (aRKID V2.5)',
            'service': {
                'sp': {
                    'name': 'ARKID SAML2 SP',
                    'endpoints': {
                        'assertion_consumer_service': [
                            (get_app_config().get_frontend_host() + self.acs_path.format(tenant_id=tenant_id), BINDING_HTTP_POST)
                        ],
                    },
                    'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_TRANSIENT],
                    'authn_requests_signed': True,
                    'want_assertions_signed': True,
                    'allow_unsolicited': True,
                },
            },
            'attribute_map_dir': os.path.join(BASE_DIR, 'attribute_maps'),
            'metadata': {
                'local': [
                    os.path.join(
                        os.path.join(
                            BASE_DIR, 
                            'saml2_config'
                        ), 
                        f
                    ) for f in os.listdir(
                        BASE_DIR + '/saml2_config/'
                    ) if f.split('.')[-1] == 'xml'
                ],
            },
            # Signing
            'key_file': BASE_DIR + '/certificates/key.pem',
            'cert_file': BASE_DIR + '/certificates/cert.pem',
            # Encryption
            'encryption_keypairs': [{
                'key_file': BASE_DIR + '/certificates/key.pem',
                'cert_file': BASE_DIR + '/certificates/cert.pem',
            }],
            'valid_for': 365 * 24,
        }
        return saml_sp_config

    def create_self_signed_cert(self):
        '''
        生成自签名证书存放于相对路径下
        '''
        BASE_DIR = os.path.join(os.path.dirname(__file__),"certificates")
        self.cert_file_path = os.path.join(BASE_DIR,"cert.pem")
        self.key_file_path = os.path.join(BASE_DIR,"key.pem")
        
        if not os.path.exists(BASE_DIR):
            os.mkdir(BASE_DIR)    

        if not os.path.exists(self.cert_file_path) or not os.path.exists(self.key_file_path):
            self.clear_self_signed_cert()

            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 1024)
            cert = crypto.X509()
            cert.get_subject().C = "CN"
            cert.get_subject().CN = gethostname()
            cert.set_serial_number(1000)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.sign(k, 'sha1')

            with open(self.cert_file_path, "wb") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            with open(self.key_file_path, "wb") as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            
    def clear_self_signed_cert(self):
        """
        清理自签名文件
        """
        BASE_DIR = os.path.join(os.path.dirname(__file__),"certificates")
        file_name_prefix = f"{BASE_DIR}/"
        if os.path.exists(f"{file_name_prefix}cert.pem"):
            os.remove(f"{file_name_prefix}cert.pem")

        if os.path.exists(f"{file_name_prefix}key.pem"):
            os.remove(f"{file_name_prefix}key.pem")

    def metadata(self,tenant_id):
        
        saml_sp_config = self.get_saml_sp_config(tenant_id)
        
        sp_config = copy.deepcopy(saml_sp_config)
        
        conf = SPConfig()
        try:
            conf.load(sp_config)
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
     
    def get_sp_metadata_file(self,request,tenant_id):
        """获取metadata文件
        """
        response = FileResponse(self.metadata(tenant_id),filename='arkid_sp.xml',as_attachment=True)
        response['Content-Type'] = 'text/xml'
        return response
    
    def acs(self,request, tenant_id):
        """acs
        """
        conf = SPConfig()
        conf.load(self.get_saml_sp_config(tenant_id))

        client = Saml2Client(conf)

        _exception = None
        try:
            response = client.parse_authn_request_response(
                request.POST['SAMLResponse'],
                BINDING_HTTP_POST
            )
        except Exception as err:
            _exception = err
            logger.error(err)

        if _exception:
            return self.error(
                ErrorCode.ACS_FAILED
            )
        elif response is None:
            return self.error(
                ErrorCode.UNKOWN_ERROR
            )
            
        print(response.name_id.text)

        username = response.name_id.text
        
        user,created = User.active_objects.get_or_create(
            tenant=request.tenant,
            username=username
        )
        
        token = refresh_token(user)
        frontend_host = get_app_config().get_frontend_host()
        frontend_callback = f'{frontend_host}/third_part_callback'
        context = {"token": token}
        query_string = urlencode(context)
        url = f"{frontend_callback}?{query_string}"
        url = unquote(url)
        
        return HttpResponseRedirect(url)
        
        
    def sso_post(self,request):
        pass
    
    def sso_redirect(self,request):
        pass
    
    def sso_login(self,request, tenant_id):
        form_data = request.POST or json.loads(request.body)
        config_id = form_data["config_id"]
        config = TenantExtensionConfig.active_objects.get(id=config_id)
        sp_config = self.get_saml_sp_config(str(config.tenant.id))
        conf = SPConfig()
        conf.load(sp_config)
        
        selected_idp = config.config.get("idp_entity_id",None)
        
        if not selected_idp:
            return self.error(
                ErrorCode.NOT_AVAILABLE_SELECTED_IDP
            )
        
        binding = BINDING_HTTP_REDIRECT
        idp_meta = getattr(conf, 'metadata', {})
        supported_bindings = list(idp_meta.service(selected_idp, 'idpsso_descriptor', 'single_sign_on_service').keys())
        
        if binding not in supported_bindings:
           return self.error(
               ErrorCode.UNSUPPORTED_BINDING
           )
                
        client = Saml2Client(conf)
        sso_kwargs = {}

        # SSO options
        sign_requests = getattr(conf, '_sp_authn_requests_signed', False)
        if sign_requests:
            sso_kwargs["sigalg"] = getattr(
                conf, 
                '_sp_signing_algorithm',
                SIG_RSA_SHA256
            )
            sso_kwargs["digest_alg"] = getattr(
                conf,
                '_sp_digest_algorithm',
                DIGEST_SHA256
            )
        # pysaml needs a string otherwise: "cannot serialize True (type bool)"
        if getattr(conf, '_sp_force_authn', False):
            sso_kwargs['force_authn'] = "true"
        if getattr(conf, '_sp_allow_create', False):
            sso_kwargs['allow_create'] = "true"

        # custom nsprefixes
        sso_kwargs['nsprefix'] = self.get_namespace_prefixes()
        
        self.load_sso_kwargs_authn_context(conf, sso_kwargs)
        
        http_response = None

        try:
            session_id, result = client.prepare_for_authenticate(
                entityid=selected_idp, 
                relay_state=get_app_config().get_frontend_host(),
                binding=binding, 
                sign=sign_requests,
                **sso_kwargs
            )
        except TypeError as e:
            return self.error(
                ErrorCode.UNABLE_TO_KNOW_WITCH_IDP_TO_USE
            )
        else:
            http_response = self.get_location(result)


        return {
            "redirect":http_response
        }
        
    def get_namespace_prefixes(self):
        from saml2 import md, saml, samlp, xmlenc, xmldsig
        return {
            'saml': saml.NAMESPACE,
            'samlp': samlp.NAMESPACE,
            'md': md.NAMESPACE,
            'ds': xmldsig.NAMESPACE,
            'xenc': xmlenc.NAMESPACE
        }
        
    def load_sso_kwargs_authn_context(self, conf, sso_kwargs):
        # this would work when https://github.com/IdentityPython/pysaml2/pull/807
        ac = getattr(conf, '_sp_requested_authn_context', {})

        if ac:
            sso_kwargs["requested_authn_context"] = RequestedAuthnContext(
                    authn_context_class_ref=[
                        AuthnContextClassRef(ref) for ref in ac['authn_context_class_ref']
                    ],
                    comparison=ac.get('comparison', "minimum"),
                )
    
    def get_location(self, http_info):
        """Extract the redirect URL from a pysaml2 http_info object"""
        try:
            headers = dict(http_info['headers'])
            return headers['Location']
        except KeyError:
            return http_info['url']
        
    def add_idp_hinting(self, request, http_response) -> bool:
        idphin_param = getattr(settings, 'SAML2_IDPHINT_PARAM', 'idphint')
        urllib.parse.urlencode(request.GET)

        if idphin_param not in request.GET.keys():
            return False

        idphint = request.GET[idphin_param]
        # validation : TODO -> improve!
        if idphint[0:4] != 'http':
            logger.warning(
                f'Idp hinting: "{idphint}" doesn\'t contain a valid value.'
                'idphint paramenter ignored.'
            )
            return False

        if http_response.status_code in (302, 303):
            # redirect binding
            # urlp = urllib.parse.urlparse(http_response.url)
            new_url = self.add_param_in_url(http_response.url,
                                    idphin_param, idphint)
            return HttpResponseRedirect(new_url)

        elif http_response.status_code == 200:
            # post binding
            res = re.search(r'action="(?P<url>[a-z0-9\:\/\_\-\.]*)"',
                            http_response.content.decode(), re.I)
            if not res:
                return False
            orig_url = res.groupdict()['url']
            #
            new_url = self.add_param_in_url(orig_url, idphin_param, idphint)
            content = http_response.content.decode()\
                                .replace(orig_url, new_url)\
                                .encode()
            return HttpResponse(content)

        else:
            logger.warning(
                f'Idp hinting: cannot detect request type [{http_response.status_code}]'
            )
        return False
    
    def add_param_in_url(self, url: str, param_key: str, param_value: str):
        params = list(url.split('?'))
        params.append(f'{param_key}={param_value}')
        new_url = params[0] + '?' + ''.join(params[1:])
        return new_url

extension = SAML2AuthFactorExtension()
