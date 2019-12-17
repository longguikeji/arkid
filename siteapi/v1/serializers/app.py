'''
serializers for APP
'''

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
    '''
    Serializer for OIDCAPP
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = OIDCAPP

        fields = ()


class SAMLAPPSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for SAMLAPP
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = SAMLAPP

        fields = ()


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
    oidc_app = OIDCAPPSerializer(many=False, required=False)
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
            "oidc_app",
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

        if oidc_app_data:
            pass

        if saml_app_data:
            pass

        return app

    # TODO: support update name of app
    def update(self, instance, validated_data):    # pylint:disable=too-many-statements,too-many-branches
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
        saml_app_data = validated_data.pop('saml_app', None)

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

        if saml_app_data:
            pass

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
            "oidc_app",
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
            "oidc_app",
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
