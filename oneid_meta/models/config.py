# pylint: disable=too-many-lines
'''
schema for GlobalConfig
'''
import hashlib
from django.db import models
from django.contrib.sites.models import Site
from django.conf import settings
import jsonfield
from aliyunsdkcore.acs_exception.exceptions import ServerException

from common.django.model import BaseModel
from common.sms.aliyun.sms_manager import SMSAliyunManager
from common.Email.email_manager import EmailManager
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.constants import TOKEN_FROM_APPID_QR_APP_SECRET
from thirdparty_data_sdk.alipay_api.alipay_oauth_manager import AlipayOauthManager
from thirdparty_data_sdk.github_sdk.userinfo_manager import GithubUserInfoManager
from thirdparty_data_sdk.qq_sdk.qq_openid_sdk import QQInfoManager
from thirdparty_data_sdk.wechat_sdk.wechat_user_info_manager import WechatUserInfoManager
from thirdparty_data_sdk.work_wechat_sdk.user_info_manager import WorkWechatManager


class SingletonConfigMixin:
    '''
    单例配置
    '''
    @classmethod
    def get_current(cls):
        '''
        当前所用配置
        '''
        obj, _ = cls.valid_objects.get_or_create(site=Site.objects.get_current())
        return obj


class CompanyConfig(BaseModel, SingletonConfigMixin):
    '''
    公司相关信息
    '''
    site = models.OneToOneField(Site, related_name='company_config', on_delete=models.CASCADE)

    name_cn = models.CharField(max_length=255, blank=True, default="", verbose_name='中文简称')
    fullname_cn = models.CharField(max_length=255, blank=True, default="", verbose_name='中文全称')
    name_en = models.CharField(max_length=255, blank=True, default="", verbose_name='英文简称')
    fullname_en = models.CharField(max_length=255, blank=True, default="", verbose_name='英文全称')

    icon = models.CharField(max_length=1024, blank=True, default="", verbose_name='图标')
    address = models.CharField(max_length=255, blank=True, default="", verbose_name='办公地址')
    domain = models.CharField(max_length=255, blank=True, default="", verbose_name='公司主页')

    color = models.CharField(max_length=256, blank=True, default='', verbose_name='主题色值')

    def __str__(self):
        return f'Company[{self.id}]: {self.display_name}'    # pylint: disable=no-member

    @property
    def display_name(self):
        '''
        首页展示用的公司名称
        '''
        return self.fullname_cn


class DingConfig(BaseModel, SingletonConfigMixin):
    '''
    钉钉配置信息
    '''
    SYNC_CHOICES = (
        ('pull', '拉取'),
        ('push', '推送'),
        ('', '断开'),
    )
    site = models.OneToOneField(Site, related_name='ding_config', on_delete=models.CASCADE)
    sync_state = models.CharField(max_length=128,
                                  choices=SYNC_CHOICES,
                                  blank=False,
                                  default='pull',
                                  verbose_name='同步钉钉账户方向')

    app_key = models.CharField(max_length=255, blank=True, default="", verbose_name="APP KEY")
    app_secret = models.CharField(max_length=255, blank=True, default="", verbose_name="APP SECRET")
    app_valid = models.BooleanField(default=False, verbose_name='APP 配置是否正确')

    corp_id = models.CharField(max_length=255, blank=True, default="", verbose_name="CORP ID")
    corp_secret = models.CharField(max_length=255, blank=True, default="", verbose_name="CORP SECRET")
    corp_valid = models.BooleanField(default=False, verbose_name='Corp 配置是否正确')

    qr_app_id = models.CharField(max_length=255, blank=True, default="", verbose_name="QR APP ID")
    qr_app_secret = models.CharField(max_length=255, blank=True, default="", verbose_name="QR APP SECRET")
    qr_app_valid = models.BooleanField(default=False, verbose_name='扫码登录APP配置是否正确')

    def check_valid(self):
        '''
        检查配置是否有效
        '''
        accesser = AccessTokenManager(app_key=self.qr_app_id,\
            app_secret=self.qr_app_secret, token_version=TOKEN_FROM_APPID_QR_APP_SECRET)
        try:
            accesser.get_access_token()
            return True
        except ServerException as exce:
            print(exce)
            return False
        except RuntimeError:
            return True

    def __str__(self):
        return f'DingConfig[{self.id}]'    # pylint: disable=no-member


class AccountConfig(BaseModel, SingletonConfigMixin):
    '''
    账号相关配置信息
    '''
    site = models.OneToOneField(Site, related_name='account_config', on_delete=models.CASCADE)

    allow_email = models.BooleanField(default=False, blank=True, verbose_name='是否允许邮箱(注册、)登录、找回密码')
    allow_mobile = models.BooleanField(default=False, blank=True, verbose_name='是否允许手机(注册、)登录、找回密码')
    allow_register = models.BooleanField(default=False, blank=True, verbose_name='是否开放注册')
    allow_ding_qr = models.BooleanField(default=False, blank=True, verbose_name='是否开放钉钉扫码登录')
    allow_alipay_qr = models.BooleanField(default=False, blank=True, verbose_name='是否开放支付宝扫码登录')
    allow_work_wechat_qr = models.BooleanField(default=False, blank=True, verbose_name='是否开放企业微信扫码登录')
    allow_wechat_qr = models.BooleanField(default=False, blank=True, verbose_name='是否开放微信扫码登录')
    allow_qq_qr = models.BooleanField(default=False, blank=True, verbose_name='是否开放qq扫码登录')
    allow_github = models.BooleanField(default=False, blank=True, verbose_name='是否开放github账号登录')

    def __str__(self):
        return f'AccountConfig[{self.id}]'    # pylint: disable=no-member

    @property
    def support_email(self):
        '''
        是否支持邮箱登录、找回密码
        '''
        return self.allow_email and EmailConfig.get_current().is_valid

    @property
    def support_mobile(self):
        '''
        是否支持手机登录、找回密码
        '''
        return self.allow_mobile and SMSConfig.get_current().is_valid

    @property
    def support_email_register(self):
        '''
        是否支持邮箱注册
        '''
        return self.allow_register and self.support_email

    @property
    def support_mobile_register(self):
        '''
        是否支持手机注册
        '''
        return self.allow_register and self.support_mobile

    @property
    def support_ding_qr(self):
        '''
        是否支持钉钉扫码登录
        '''
        return self.allow_ding_qr and DingConfig.get_current().qr_app_valid

    @property
    def support_ding_qr_register(self):
        '''
        是否支持钉钉扫码注册
        '''
        return self.allow_register and self.support_ding_qr

    @property
    def support_alipay_qr(self):
        '''
        是否支持支付宝扫码登录
        '''
        return self.allow_alipay_qr and AlipayConfig.get_current().qr_app_valid

    @property
    def support_alipay_qr_register(self):
        '''
        是否支持支付宝扫码注册
        '''
        return self.allow_register and self.support_alipay_qr

    @property
    def support_qq_qr(self):
        '''
        是否支持qq扫码登录
        '''
        return self.allow_qq_qr and QQConfig.get_current().qr_app_valid

    @property
    def support_qq_qr_register(self):
        '''
        是否支持qq扫码注册
        '''
        return self.allow_register and self.support_qq_qr

    @property
    def support_work_wechat_qr(self):
        '''
        是否支持支付宝扫码登录
        '''
        return self.allow_work_wechat_qr and WorkWechatConfig.get_current().qr_app_valid

    @property
    def support_work_wechat_qr_register(self):
        '''
        是否支持支付宝扫码注册
        '''
        return self.allow_register and self.support_work_wechat_qr

    @property
    def support_wechat_qr(self):
        '''
        是否支持微信扫码登录
        '''
        return self.allow_wechat_qr and WechatConfig.get_current().qr_app_valid

    @property
    def support_wechat_qr_register(self):
        '''
        是否支持微信扫码注册
        '''
        return self.allow_register and self.support_wechat_qr

    @property
    def support_github(self):
        """
        是否支持github账户登录
        """
        return self.allow_github and GithubConfig.get_current().client_valid

    @property
    def support_github_register(self):
        """
        是否支持github账户注册
        """
        return self.allow_register and self.support_github


class SMSConfig(BaseModel, SingletonConfigMixin):
    '''
    短信相关配置
    '''
    VENDOR_CHOICES = (('aliyun', '阿里云'), )
    site = models.OneToOneField(Site, related_name='sms_config', on_delete=models.CASCADE)

    vendor = models.CharField(max_length=128, choices=VENDOR_CHOICES, default='aliyun', verbose_name='短信服务商')

    access_key = models.CharField(max_length=255, default="", blank=True, verbose_name='AccessKey')
    access_secret = models.CharField(max_length=255, default="", blank=True, verbose_name='AccessSecret')

    signature = models.CharField(max_length=64, default='', blank=True, verbose_name='签名')
    signature_i18n = models.CharField(max_length=64, default='', blank=True, verbose_name='国际-签名')

    template_code = models.CharField(max_length=255, default='', blank=True, verbose_name='验证码通用文案模板ID')
    template_register = models.CharField(max_length=255, default='', blank=True, verbose_name='注册文案模板ID')
    template_reset_pwd = models.CharField(max_length=255, default='', blank=True, verbose_name='重置密码文案模板ID')
    template_activate = models.CharField(max_length=255, default='', blank=True, verbose_name='用户激活文案模板ID')
    template_reset_mobile = models.CharField(max_length=255, default='', blank=True, verbose_name='用户重置手机文案模板ID')
    template_login = models.CharField(max_length=255, default='', blank=True, verbose_name='登录文案模板ID')

    template_code_i18n = models.CharField(max_length=255, default='', blank=True, verbose_name='国际-验证码通用文案模板ID')
    template_register_i18n = models.CharField(max_length=255, default='', blank=True, verbose_name='国际-注册文案模板ID')
    template_reset_pwd_i18n = models.CharField(max_length=255, default='', blank=True, verbose_name='国际-重置密码文案模板ID')
    template_activate_i18n = models.CharField(max_length=255, default='', blank=True, verbose_name='国际-用户激活文案模板ID')
    template_reset_mobile_i18n = models.CharField(max_length=255,
                                                  default='',
                                                  blank=True,
                                                  verbose_name='国际-用户重置手机文案模板ID')
    template_login_i18n = models.CharField(max_length=255, default='', blank=True, verbose_name='国际-登录文案模板ID')

    is_valid = models.BooleanField(default=False, blank=True, verbose_name='配置是否有效')

    def get_template_code(self, key="", i18n=False):
        '''
        get template code by key
        '''
        if i18n:
            return getattr(self, f"template_{key}_i18n")

        return getattr(self, f"template_{key}")

    def check_valid(self):
        '''
        检查配置是否有效
        '''
        smser = SMSAliyunManager(
            access_key=self.access_key,
            access_key_secret=self.access_secret,
        )
        try:
            smser.send_auth_code(
                mobile='.',
                vc_code='.',
                sign_name=self.signature,
                template_code=self.template_code,
            )
            return True
        except ServerException as exce:
            print(exce)
            return False
        except RuntimeError:
            return True

    @property
    def access_secret_encrypt(self):
        '''
        加密后的access_secret
        '''
        return self.encrypt(self.access_secret)

    @staticmethod
    def encrypt(value):
        '''
        对敏感数据加密
        '''
        hl = hashlib.md5()    # pylint: disable=invalid-name
        hl.update((settings.SECRET_KEY[:6] + value).encode('utf-8'))
        return hl.hexdigest()


class EmailConfig(BaseModel, SingletonConfigMixin):
    '''
    邮件相关配置
    '''
    site = models.OneToOneField(Site, related_name='email_config', on_delete=models.CASCADE)

    host = models.CharField(default='', blank=True, max_length=256, verbose_name='邮件服务地址')
    port = models.IntegerField(default=587, blank=True, verbose_name='邮件服务端口')
    access_key = models.CharField(default='', blank=True, max_length=512, verbose_name='邮箱账号')
    access_secret = models.CharField(default='', blank=True, max_length=512, verbose_name='邮箱密钥')
    nickname = models.CharField(default='ArkID', blank=True, max_length=128, verbose_name='邮件发送人落款')

    is_valid = models.BooleanField(default=False, blank=True, verbose_name='配置是否有效')

    def check_valid(self):
        '''
        检查配置是否有效
        '''
        emailer = EmailManager(
            user=self.access_key,
            pwd=self.access_secret,
            host=self.host,
            port=self.port,
            nickname=self.nickname,
        )
        try:
            emailer.connect()
            return True
        except Exception:    # pylint: disable=broad-except
            return False

    @property
    def access_secret_encrypt(self):
        '''
        加密后的access_secret
        '''
        return self.encrypt(self.access_secret)

    @staticmethod
    def encrypt(value):
        '''
        对敏感数据加密
        '''
        hl = hashlib.md5()    # pylint: disable=invalid-name
        hl.update((settings.SECRET_KEY[:6] + value).encode('utf-8'))
        return hl.hexdigest()


class CustomField(BaseModel):
    '''
    自定义字段
    '''

    SUBJECT_CHOICES = (
        ('user', '内部联系人'),    # '^[a-z]{1,16}$'
        ('extern_user', '外部联系人'),
    )

    name = models.CharField(max_length=128, verbose_name='字段名称')
    subject = models.CharField(choices=SUBJECT_CHOICES, default='user', max_length=128, verbose_name='字段分类')
    schema = jsonfield.JSONField(default={'type': 'string'}, verbose_name='字段定义')
    is_visible = models.BooleanField(default=True, verbose_name='是否展示')


class NativeField(BaseModel):
    '''
    原生字段
    '''
    SUBJECT_CHOICES = (
        ('user', '内部联系人'),    # '^[a-z]{1,16}$'
        ('extern_user', '外部联系人'),
    )
    name = models.CharField(max_length=128, verbose_name='字段名称')
    key = models.CharField(max_length=256, verbose_name='内部字段名')
    subject = models.CharField(choices=SUBJECT_CHOICES, default='user', max_length=128, verbose_name='字段分类')
    schema = jsonfield.JSONField(default={'type': 'string'}, verbose_name='字段定义')
    is_visible = models.BooleanField(default=True, verbose_name='是否展示')
    is_visible_editable = models.BooleanField(default=True, verbose_name='对于`是否展示`，是否可以修改')


class AlipayConfig(BaseModel, SingletonConfigMixin):
    '''
    支付宝配置信息
    '''
    site = models.OneToOneField(Site, related_name='alipay_config', on_delete=models.CASCADE)

    app_id = models.CharField(max_length=255, blank=True, default="", verbose_name="QR APP ID")
    app_private_key = models.CharField(max_length=2048, blank=True, default="", verbose_name="APP PVIVATE KEY")
    alipay_public_key = models.CharField(max_length=512, blank=True, default="", verbose_name="ALIPAY PUBLIC KEY")
    qr_app_valid = models.BooleanField(default=False, verbose_name='扫码登录APP配置是否正确')

    def check_valid(self):
        '''
        检查配置是否有效
        '''
        is_valid = AlipayOauthManager(app_id=self.app_id, app_private_key=self.app_private_key,\
            alipay_public_key=self.alipay_public_key).check_config_valid()
        return is_valid

    def __str__(self):
        return f'AlipayConfig[{self.id}]'    # pylint: disable=no-member


class WorkWechatConfig(BaseModel, SingletonConfigMixin):
    '''
    企业微信配置信息
    '''
    site = models.OneToOneField(Site, related_name='work_wechat_config', on_delete=models.CASCADE)

    corp_id = models.CharField(max_length=255, blank=True, default="", verbose_name="CORP ID")
    agent_id = models.CharField(max_length=64, blank=True, default="", verbose_name="AGENT ID")
    secret = models.CharField(max_length=255, blank=True, default="", verbose_name="SECRET")
    qr_app_valid = models.BooleanField(default=False, verbose_name='扫码登录APP配置是否正确')

    def check_valid(self):
        '''
        检查配置是否有效
        '''
        is_valid = WorkWechatManager(corp_id=self.corp_id, secret=self.secret).check_valid()
        return is_valid

    def __str__(self):
        return f'WorkWechatConfig[{self.id}]'    # pylint: disable=no-member


class WechatConfig(BaseModel, SingletonConfigMixin):
    '''
    企业微信配置信息
    '''
    site = models.OneToOneField(Site, related_name='wechat_config', on_delete=models.CASCADE)

    appid = models.CharField(max_length=255, blank=True, default="", verbose_name="APP ID")
    secret = models.CharField(max_length=255, blank=True, default="", verbose_name="APP SECRET")
    qr_app_valid = models.BooleanField(default=False, verbose_name='扫码登录APP配置是否正确')

    def check_valid(self):
        '''
        检查配置是否有效
        '''
        is_valid = WechatUserInfoManager(appid=self.appid,\
            secret=self.secret).check_valid()
        return is_valid

    def __str__(self):
        return f'WorkWechatConfig[{self.id}]'    # pylint: disable=no-member


class QQConfig(BaseModel, SingletonConfigMixin):
    '''
    qq配置信息
    '''
    site = models.OneToOneField(Site, related_name='qq_config', on_delete=models.CASCADE)

    app_id = models.CharField(max_length=255, blank=True, default="", verbose_name="APP ID")
    app_key = models.CharField(max_length=255, blank=True, default="", verbose_name="APP SECRET")
    qr_app_valid = models.BooleanField(default=False, verbose_name='扫码登录是否配置正确')

    def check_valid(self):
        '''
        检查配置是否有效
        '''
        is_valid = QQInfoManager(
            app_id=self.app_id,
            app_key=self.app_key,
        ).check_config_valid()
        return is_valid

    def __str__(self):
        return f'QQConfig[{self.id}]'    # pylint: disable=no-member


class StorageConfig(BaseModel, SingletonConfigMixin):
    '''
    文件存储方式
    '''
    site = models.OneToOneField(Site, related_name='storage_config', on_delete=models.CASCADE)

    method = models.CharField(max_length=225, blank=True, default='local', verbose_name='method')

    def __str__(self):
        return f'Method[{self.id}]: {self.display_name}'    # pylint: disable=no-member


class MinioConfig(BaseModel, SingletonConfigMixin):
    '''
    Minio配置信息
    '''
    site = models.OneToOneField(Site, related_name='minio_config', on_delete=models.CASCADE)

    end_point = models.CharField(max_length=225, blank=True, default='', verbose_name='END POINT')
    access_key = models.CharField(max_length=225, blank=True, default='', verbose_name='ACCESS KEY')
    secret_key = models.CharField(max_length=225, blank=True, default='', verbose_name='SECRET KEY')
    secure = models.BooleanField(max_length=225, blank=True, default=True, verbose_name='SECURE')
    location = models.CharField(max_length=225, blank=True, default='', verbose_name='LOCATION')
    bucket = models.CharField(max_length=225, blank=True, default='', verbose_name='BUCKET')

    def check_valid(self):    #pylint: disable=no-self-use
        '''
        检查配置是否有效
        '''
        return True

    def __str__(self):
        return f'Minio[{self.id}]: {self.display_name}'    # pylint: disable=no-member


class PasswordComplexityConfig(BaseModel, SingletonConfigMixin):
    """认证密码复杂度配置信息"""
    site = models.OneToOneField(Site, related_name='password_config', on_delete=models.CASCADE)

    min_length = models.IntegerField(default=0, blank=True, verbose_name="最小长度")
    min_upper = models.IntegerField(default=0, blank=True, verbose_name="大写字母限制")
    min_lower = models.IntegerField(default=0, blank=True, verbose_name="小写字母限制")
    min_letter = models.IntegerField(default=0, blank=True, verbose_name="字母限制")
    min_digit = models.IntegerField(default=0, blank=True, verbose_name="数字限制")
    min_special = models.IntegerField(default=0, blank=True, verbose_name="特殊字符限制")
    min_word = models.IntegerField(default=0, blank=True, verbose_name="单词限制")


class I18NMobileConfig(BaseModel):
    """
    国际手机号码接入配置
    """
    state = models.CharField(max_length=128, unique=True, verbose_name='号码归属区域')
    state_code = models.CharField(max_length=32, blank=False, null=False, unique=True, verbose_name='国家区号')
    number_length = models.IntegerField(null=True, default=None, verbose_name='号码固定长度')
    start_digital = jsonfield.JSONField(default=[], blank=True, verbose_name='首位数字限制集')


class GithubConfig(BaseModel, SingletonConfigMixin):
    """
    Github 配置信息
    """
    site = models.OneToOneField(Site, related_name='github_config', on_delete=models.CASCADE)

    client_id = models.CharField(max_length=255, blank=True, default="", verbose_name="Client ID")
    client_secret = models.CharField(max_length=255, blank=True, default="", verbose_name="Client Secret")
    client_valid = models.BooleanField(default=False, verbose_name='Client 配置是否正确')

    def check_valid(self):
        """
        检查配置是否有效
        """
        is_valid = GithubUserInfoManager(client_id=self.client_id, client_secret=self.client_secret).check_valid()
        return is_valid

    def __str__(self):
        return f'GithubConfig[{self.id}]'    # pylint: disable=no-member
