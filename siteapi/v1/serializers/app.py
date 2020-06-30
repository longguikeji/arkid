'''
serializers for APP
'''
import os
import copy
import uuid
from six import text_type
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.config import SPConfig
from saml2.metadata import entity_descriptor
from saml2.entity_category.edugain import COC
from saml2.saml import NAME_FORMAT_URI
from saml2.sigver import CertificateError
try:
    from saml2.sigver import get_xmlsec_binary
except ImportError:
    get_xmlsec_binary = None
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from common.django.drf.serializer import DynamicFieldsModelSerializer
from oneid_meta.models import (
    APP,
    OAuthAPP,
    OIDCAPP,
    SAMLAPP,
    LDAPAPP,
    HTTPAPP,
    Dept,
    User,
)
from siteapi.v1.views.utils import gen_uid
from siteapi.v1.serializers.perm import PermWithOwnerSerializer
# pylint: disable=too-many-lines

if get_xmlsec_binary:
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin", "/usr/local/bin"])    # pylint: disable=invalid-name
else:
    xmlsec_path = '/usr/local/bin/xmlsec1'    # pylint: disable=invalid-name
BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class OAuthAPPSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for OAuthAPP
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = OAuthAPP

        fields = (
            'client_id',
            'client_secret',
            'redirect_uris',
            'client_type',
            'authorization_grant_type',
            'more_detail',
        )

        read_only_fields = (
            'client_id',
            'client_secret',
            'more_detail',
        )


class OIDCAPPSerializer(DynamicFieldsModelSerializer):
    '''Serializer for OIDCAPP
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = OIDCAPP

        fields = (
            'client_id',
            'client_secret',
            'redirect_uris',
            'client_type',
            'response_type',
            'more_detail',
        )

        read_only_fields = (
            'client_id',
            'client_secret',
            'more_detail',
        )


class SAMLAPPSerializer(DynamicFieldsModelSerializer):
    '''Serializer for SAMLAPP
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = SAMLAPP

        fields = (
            'entity_id',
            'acs',
            'sls',
            'cert',
            'xmldata',
            'more_detail',
        )

    def gen_xml(self, filename, entity_id, acs, sls):    # pylint: disable=no-self-use
        '''将SAMLAPP配置写入指定路径xml文件
        '''
        conf = SPConfig()
        endpointconfig = {
            "entityid": entity_id,
            'entity_category': [COC],
            "description": "extra SP setup",
            "service": {
                "sp": {
                    "want_response_signed": False,
                    "authn_requests_signed": True,
                    "logout_requests_signed": True,
                    "endpoints": {
                        "assertion_consumer_service": [(acs, BINDING_HTTP_POST)],
                        "single_logout_service": [
                            (sls, BINDING_HTTP_REDIRECT),
                            (sls.replace('redirect', 'post'), BINDING_HTTP_POST),
                        ],
                    }
                },
            },
            "key_file": BASEDIR + "/djangosaml2idp/certificates/mykey.pem",    # 随便放一个私钥，并不知道SP私钥
            "cert_file": BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename,
            "xmlsec_binary": xmlsec_path,
            "metadata": {
                "local": [BASEDIR + '/djangosaml2idp/saml2_config/idp_metadata.xml']
            },
            "name_form": NAME_FORMAT_URI,
        }
        conf.load(copy.deepcopy(endpointconfig))
        meta_data = entity_descriptor(conf)
        content = text_type(meta_data).encode('utf-8')
        with open(BASEDIR + '/djangosaml2idp/saml2_config/%s.xml' % filename, 'wb+') as f:
            f.write(content)

    def create(self, validated_data):
        filename = uuid.uuid4()
        app = validated_data['app']
        xmldata = validated_data.get('xmldata', '')
        entity_id = validated_data.get('entity_id', '')
        cert = validated_data.get('cert', '')
        acs = validated_data.get('acs', '')
        sls = validated_data.get('sls', '')

        if xmldata not in ['', None]:
            with open(BASEDIR + '/djangosaml2idp/saml2_config/%s.xml' % filename, 'w+') as f:
                f.write(xmldata)
        else:
            self.dump_cert(filename, cert)
            try:
                self.gen_xml(filename=filename, entity_id=entity_id, acs=acs, sls=sls)
            except CertificateError:
                raise ValidationError({'msg': 'perm incorrect'})

        if os.path.exists(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename):
            os.remove(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename)

        saml_app = SAMLAPP.objects.create(app=app, xmldata=xmldata, entity_id=entity_id,\
            acs=acs, sls=sls, cert=cert)
        saml_app.save()
        saml_app.refresh_from_db()
        return saml_app

    def update(self, instance, validated_data):
        saml_app = instance
        filename = uuid.uuid4()
        xmldata = validated_data.get('xmldata', '')
        cert = validated_data.get('cert', '')
        entity_id = validated_data.get('entity_id', '')
        acs = validated_data.get('ace', '')
        sls = validated_data.get('sls', '')
        kwargs = {}

        if entity_id != '':
            kwargs['entity_id'] = entity_id
        if acs != '':
            kwargs['acs'] = acs
        if sls != '':
            kwargs['sls'] = sls
        if cert != '':
            kwargs['cert'] = cert
        if xmldata != '':
            with open(BASEDIR + '/djangosaml2idp/saml2_config/%s.xml' % filename, 'w+') as f:
                f.write(xmldata)
        else:
            self.dump_cert(filename, cert)
            self.gen_xml(filename=filename, entity_id=entity_id, acs=acs, sls=sls)
            with open(BASEDIR + '/djangosaml2idp/saml2_config/%s.xml' % filename, 'rb') as f:
                xmldata = f.read()
        kwargs['xmldata'] = xmldata
        saml_app.__dict__.update(**kwargs)
        saml_app.save()
        saml_app.refresh_from_db()
        return saml_app

    def dump_cert(self, filename, cert):    # pylint: disable=no-self-use
        '''存储SP方公钥,以备生成元数据文件时用
        '''
        with open(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename, 'w+') as f:
            f.write(cert)


class LDAPAPPSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for LDAP APP
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = LDAPAPP

        fields = ('more_detail', )
        read_only_fields = ('more_detail', )


class HTTPAPPSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for HTTP APP
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = HTTPAPP

        fields = ('more_detail', )
        read_only_fields = ('more_detail', )


class APPPublicSerializer(DynamicFieldsModelSerializer):
    '''
    public serializer for APP
    '''
    app_id = serializers.IntegerField(source='id', read_only=True)
    uid = serializers.CharField(required=False, help_text='默认情况下根据`name`生成')

    class Meta:    # pylint: disable=missing-docstring
        model = APP

        fields = (
            "app_id",
            "uid",
            "name",
            "index",
            "logo",
            "remark",
            'auth_protocols',
        )


class APPSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for APP
    '''
    app_id = serializers.IntegerField(source='id', read_only=True)
    oauth_app = OAuthAPPSerializer(many=False, required=False, allow_null=True)
    http_app = HTTPAPPSerializer(many=False, required=False, allow_null=True)
    ldap_app = LDAPAPPSerializer(many=False, required=False, allow_null=True)
    # oidc_app = OIDCAPPSerializer(many=False, required=False, allow_null=True)
    saml_app = SAMLAPPSerializer(many=False, required=False, allow_null=True)

    uid = serializers.CharField(required=False, help_text='默认情况下根据`name`生成')

    class Meta:    # pylint: disable=missing-docstring
        model = APP

        fields = (
            "app_id",
            "uid",
            "name",
            "index",
            "logo",
            "remark",
            "oauth_app",
            "ldap_app",
            "http_app",
        # "oidc_app",
            "saml_app",
            "allow_any_user",
            'auth_protocols',
        )

    def validate_uid(self, value):
        '''
        校验uid唯一
        '''
        exclude = {'pk': self.instance.pk} if self.instance else {}
        if self.Meta.model.valid_objects.filter(uid=value).exclude(**exclude).exists():
            raise ValidationError(['this value has be used'])
        return value

    def create(self, validated_data):
        '''
        create app
        create oauth_app if provided
        create oidc_app if provided
        create http_app if provided
        create saml_app if provided
        '''
        if 'uid' not in validated_data:
            validated_data['uid'] = gen_uid(validated_data['name'], cls=self.Meta.model)

        oauth_app_data = validated_data.pop('oauth_app', None)
        oidc_app_data = validated_data.pop('oidc_app', None)
        saml_app_data = validated_data.pop('saml_app', None)
        ldap_app_data = validated_data.pop('ldap_app', None)
        http_app_data = validated_data.pop('http_app', None)

        app = APP.objects.create(**validated_data)

        if oauth_app_data is not None:
            oauth_app_serializer = OAuthAPPSerializer(data=oauth_app_data)
            oauth_app_serializer.is_valid(raise_exception=True)
            oauth_app_serializer.save(app=app, name=app.name)

        if ldap_app_data is not None:
            serializer = LDAPAPPSerializer(data=ldap_app_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(app=app)

        if http_app_data is not None:
            serializer = HTTPAPPSerializer(data=http_app_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(app=app)

        if oidc_app_data is not None:
            oidc_app_serializer = OIDCAPPSerializer(data=oidc_app_data)
            oidc_app_serializer.is_valid(raise_exception=True)
            oidc_app_serializer.save(app=app, name=app.name)

        if saml_app_data is not None:
            saml_app_data['app'] = app
            serializer = SAMLAPPSerializer(data=saml_app_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(app=app)
        return app

    # TODO: support update name of app
    def update(self, instance, validated_data):    # pylint: disable=too-many-branches, too-many-statements
        '''
        update app
        update/create oauth_app if provided
        update/create oidc_app if provided
        update/create saml_app if provided
        '''
        app = instance
        if not app.editable:
            raise MethodNotAllowed('MODIFY protected APP')
        oidc_app_data = validated_data.pop('oidc_app', None)
        uid = validated_data.pop('uid', '')
        if uid and uid != app.uid:
            raise ValidationError({'uid': ['this field is immutable']})

        if 'oauth_app' in validated_data:
            oauth_app_data = validated_data.pop('oauth_app')
            if oauth_app_data is None:
                if hasattr(app, 'oauth_app'):
                    instance = app.oauth_app
                    instance.delete()
            else:
                if hasattr(app, 'oauth_app'):
                    serializer = OAuthAPPSerializer(app.oauth_app, data=oauth_app_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer = OAuthAPPSerializer(data=oauth_app_data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(app=app)

        if 'ldap_app' in validated_data:
            data = validated_data.pop('ldap_app')
            if data is None:
                if hasattr(app, 'ldap_app'):
                    instance = app.ldap_app
                    instance.delete()
            else:
                if hasattr(app, 'ldap_app'):
                    serializer = LDAPAPPSerializer(app.ldap_app, data=data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer = LDAPAPPSerializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(app=app)

        if 'http_app' in validated_data:
            data = validated_data.pop('http_app')
            if data is None:
                if hasattr(app, 'http_app'):
                    instance = app.http_app
                    instance.delete()
            else:
                if hasattr(app, 'http_app'):
                    serializer = HTTPAPPSerializer(app.http_app, data=data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer = HTTPAPPSerializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(app=app)

        if oidc_app_data:
            pass

        if 'saml_app' in validated_data:
            data = validated_data.pop('saml_app')
            if data is None:
                if hasattr(app, 'saml_app'):
                    instance = app.saml_app
                    instance.delete()
            else:
                if hasattr(app, 'saml_app'):
                    serializer = SAMLAPPSerializer(app.saml_app, data=data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    serializer = SAMLAPPSerializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(app=app)
        app.__dict__.update(validated_data)
        app.save()
        app.refresh_from_db()
        return app


class APPWithAccessSerializer(APPSerializer):
    '''
    Serializer for APP with access perm
    '''
    access_perm = PermWithOwnerSerializer(required=False, read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = APP

        fields = (
            "app_id",
            "uid",
            "name",
            "logo",
            "remark",
            "oauth_app",
        # "oidc_app",
            "saml_app",
            "ldap_app",
            "http_app",
            "index",
            "allow_any_user",
            'access_perm',
            'auth_protocols',
        )


class APPWithAccessOwnerSerializer(APPWithAccessSerializer):
    '''
    Serializer for APP with access perm
    '''

    access_result = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring
        model = APP

        fields = (
            "app_id",
            "uid",
            "name",
            "logo",
            "remark",
            "oauth_app",
        # "oidc_app",
            "saml_app",
            "ldap_app",
            "http_app",
            "index",
            "allow_any_user",
            'access_perm',
            'auth_protocols',
            'access_result',
        )

    def get_access_result(self, instance):
        '''
        某个节点或人，有无访问该应用的权限
        '''
        request = self.context['request']
        owner = None
        node_uid = request.query_params.get('node_uid', '')
        if node_uid:
            node, _ = Dept.retrieve_node(node_uid)
            if not node:
                raise ValidationError({'node_uid': ['not found']})
            owner = node
        user_uid = request.query_params.get('user_uid', '')
        if user_uid:
            user = User.valid_objects.filter(username=user_uid).first()
            if not user:
                raise ValidationError({'user_uid': ['not found']})
            owner = user
        return {
            'node_uid': node_uid,
            'user_uid': user_uid,
            'value': owner.owner_perm_cls.get(perm=instance.access_perm, owner=owner).value if owner else False,
        }


class APPListSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for APPs
    """
    apps = APPSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = APP

        fields = ('apps', )
