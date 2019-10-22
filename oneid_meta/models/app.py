'''
schema of APPs
'''
from urllib.parse import urlparse

from django.db import models
from django.db.utils import IntegrityError
from django.conf import settings

from oauth2_provider.models import Application as OAuthApplication
from common.django.model import BaseModel
from oneid_meta.models import Perm


class APP(BaseModel):
    '''
    应用，受保护的资源
    会自动创建一条uid为 {uid}_access的Perm
    '''

    uid = models.CharField(max_length=255, blank=False, verbose_name='APP唯一标识')
    name = models.CharField(max_length=255, blank=True, default='', verbose_name='权限名称')
    remark = models.TextField(blank=True, default='', verbose_name='详细介绍')
    editable = models.BooleanField(default=True, verbose_name='是否可编辑、删除')
    allow_any_user = models.BooleanField(default=False, verbose_name='任何OneID用户都可以访问')    # 不包括匿名用户

    logo = models.TextField(default='', blank=True, null=True, verbose_name='LOGO')
    index = models.CharField(max_length=512, blank=True, null=True, default='', verbose_name='应用首页')

    def __str__(self):
        return f'APP: {self.uid}({self.name})'

    def save(self, *args, **kwargs):    # pylint: disable=arguments-differ
        if APP.valid_objects.filter(uid=self.uid).exclude(pk=self.pk).exists():
            msg = "UNIQUE constraint failed: " \
                "oneid_meta.APP UniqueConstraint(fields=['uid'], condition=Q(is_del='False')"
            raise IntegrityError(msg)

        super(APP, self).save(*args, **kwargs)

    @property
    def sso_apps(self):
        '''
        return sso aaps(clients): OAuthAPP, OIDCAPP, SAMLAPP
        :rtype: generator
        '''
        # pylint: disable=no-member
        if hasattr(self, 'oauth_app'):
            yield self.oauth_app
        if hasattr(self, 'oidc_app'):
            yield self.oidc_app
        if hasattr(self, 'saml_app'):
            yield self.saml_app
        if hasattr(self, 'ldap_app'):
            yield self.ldap_app
        if hasattr(self, 'http_app'):
            yield self.http_app

    @property
    def auth_protocols(self):
        '''
        支持的协议名称，展示用
        '''
        if hasattr(self, 'oauth_app'):
            yield "OAuth 2.0"
        if hasattr(self, 'oidc_app'):
            yield "OpenID Connect"
        if hasattr(self, 'saml_app'):
            yield "SAML"
        if hasattr(self, 'ldap_app'):
            yield "LDAP"
        if hasattr(self, 'http_app'):
            yield "HTTP"

    def delete(self, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        app 软删除
        sso app 硬删除
        perm 硬删除
        userperm,groupperm,deptperm 随perm联级删除
        '''
        if self.uid == 'oneid':
            raise Exception("can't delete oneid self")
        for sso_app in self.sso_apps:
            sso_app.delete()

        for perm in Perm.valid_objects.filter(subject='app', scope=self.uid):
            perm.delete()

        super().delete()

    @property
    def default_perm(self):
        '''
        默认权限，自动创建
        '''
        return self.access_perm

    @property
    def access_perm(self):
        '''
        访问权限
        '''
        kwargs = {
            'subject': 'app',
            'scope': self.uid,
            'action': 'access',
        }
        perm = Perm.valid_objects.filter(**kwargs).first()
        if perm:
            return perm

        kwargs.update(default_value=self.allow_any_user)
        return Perm.valid_objects.create(**kwargs)

    def is_accessable(self, obj):
        '''
        对某对象是否可访问
        '''
        return obj.owner_perm_cls.valid_objects.filter(subject='app', scope=self.uid, action='access',
                                                       value=True).exist()

    def under_manage(self, user):
        '''
        判断是否在某人管理之下
        '''
        if user.is_admin:
            return True
        for manager_group in user.manager_groups:
            if self.uid in manager_group.apps:
                return True
        return False

    def is_visible_to_manager(self, user):
        '''
        对管理员是否可见
        '''
        return self.under_manage(user)


class OAuthAPP(OAuthApplication):
    '''
    OAuth2.0 client
    '''
    class Meta:    # pylint: disable=missing-docstring
        proxy = True


class LDAPAPP(BaseModel):
    '''
    ldap
    '''

    app = models.OneToOneField('oneid_meta.APP',
                               related_name="ldap_app",
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        super().kill()

    @property
    def more_detail(self):
        '''
        LDAP 相关信息，用于展示
        '''
        domain = urlparse(settings.BASE_URL).netloc
        public_addr = domain if domain else settings.PUBLIC_IP

        return [
            {
                'name': '内网地址',
                'key': 'internal_addr',
                'value': f'{settings.LDAP_SERVER}, {settings.LDAPS_SERVER}',
            },
            {
                'name': '外网地址',    # TODO
                'key': 'intra_addr',
                'value': 'ldap://{addr}, ldaps://{addr}'.format(addr=public_addr),
            },
            {
                'name': '管理员账号(bind_dn)',
                'key': 'bind_dn',
                'value': settings.LDAP_USER,
            },
            {
                'name': '管理员密码(password)',
                'key': 'password',
                'value': settings.LDAP_PASSWORD,
            },
            {
                'name': '基本目录(base_dn)',
                'key': 'base_dn',
                'value': settings.LDAP_BASE,
            },
            {
                'name': '人员目录(user_base_dn)',
                'key': 'user_base_dn',
                'value': settings.LDAP_USER_BASE,
            },
            {
                'name': '部门目录(dept_base_dn)',
                'key': 'dept_base_dn',
                'value': settings.LDAP_DEPT_BASE,
            },
            {
                'name': '组目录(group_base_dn)',
                'key': 'group_base_dn',
                'value': settings.LDAP_GROUP_BASE,
            },
            {
                'name': '人员唯一标识',
                'key': 'uid_name',
                'value': 'uid',
            }
        ]


class HTTPAPP(BaseModel):
    '''
    http
    '''
    app = models.OneToOneField('oneid_meta.APP',
                               related_name="http_app",
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        super().kill()

    @property
    def more_detail(self):
        '''
        http 接口相关信息，用于展示
        '''
        return [{
            'name': '认证地址',
            'key': 'auth_url',
            'value': settings.BASE_URL + '/siteapi/v1/auth/token/',
        }, {
            'name': '认证参数',
            'key': 'auth_params',
            'value': '{"username": "${username}", "password": "${password}"}'
        }, {
            'name': '详细内容以及更多接口支持',
            'key': 'api_docs',
            'value': 'https://oneid1.docs.apiary.io/',
        }]


class OIDCAPP():
    '''
    OIDC client
    TODO
    '''
    class Meta:    # pylint: disable=missing-docstring
        abstract = True


class SAMLAPP():
    '''
    SMAL client
    TODO
    '''
    class Meta:    # pylint: disable=missing-docstring
        abstract = True
