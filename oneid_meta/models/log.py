'''
schema of log
'''
import uuid
from collections import OrderedDict

from django.db import models


class RequestAccessLog(models.Model):
    '''
    请求基本信息
    '''

    ip = models.CharField(max_length=64, blank=True, null=True, default='', verbose_name='IP地址')

    agent = models.CharField(max_length=512, blank=True, null=True, default='', verbose_name='HTTP_USER_AGENT')

    url = models.TextField(blank=True, null=True, default='', verbose_name='完整请求路径')

    method = models.CharField(max_length=16, blank=True, null=True, default='', verbose_name='REQUEST_METHOD')

    @classmethod
    def parse(cls, request):
        '''
        解析request
        '''
        return cls.objects.create(
            ip='36.110.106.42',    # TODO: get real IP
            agent=request.META.get('HTTP_USER_AGENT', ''),
            url=request.get_full_path(),
            method=request.META.get('REQUEST_METHOD', ''),
        )


class RequestDataClientLog(models.Model):
    '''
    请求内容，定期删除
    '''
    content = models.TextField(blank=True, null=True, default='', verbose_name='请求内容')
    content_type = models.TextField(blank=True, null=True, default='', verbose_name='内容类型')

    @classmethod
    def parse(cls, request):
        '''
        解析request
        '''
        from siteapi.v1.views.utils import data_masking
        content = data_masking(request.body.decode('utf-8'))
        return cls.objects.create(
            content=content,
            content_type=request.content_type,
        )


class Log(models.Model):
    '''
    操作日志，会呈现给用户(管理员) 永久保存
    '''

    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='创建时间')

    user = models.ForeignKey('oneid_meta.User', blank=True, null=True, verbose_name='操作者', on_delete=models.CASCADE)

    subject = models.CharField(max_length=128, default='', blank=False, null=False, verbose_name='类型')

    summary = models.CharField(max_length=512, default='', blank=False, null=False, verbose_name='事件信息')

    access = models.ForeignKey(RequestAccessLog, blank=True, null=True, on_delete=models.SET_NULL)

    data = models.ForeignKey(RequestDataClientLog, blank=True, null=True, on_delete=models.SET_NULL)

    org = models.ForeignKey('oneid_meta.Org', blank=True, null=True, on_delete=models.SET_NULL)

    objects = models.Manager()

    SUBJECT_CHOICES = OrderedDict({
    # 个人
        'ucenter_login': '登录',
        'ucenter_reset_pwd': '重置密码',
        'ucenter_register': '注册',
        'ucenter_activate': '激活',

    # 管理员

    ## 配置
        'config': '系统配置',

    ## 用户
        'user_create': '创建用户',
        'user_update': '修改用户信息',
        'user_delete': '删除用户',

    ## 部门
        'dept_create': '创建部门',
        'dept_update': '修改部门信息',
        'dept_delete': '删除部门',
        'dept_move': '移动部门',
        'dept_member': '部门成员调整',

    ## 组
        'group_create': '创建组',
        'group_update': '修改组信息',
        'group_delete': '删除组',
        'group_move': '移动组',
        'group_member': '组成员调整',

    ## 应用
        'app_create': '创建应用',
        'app_update': '修改应用信息',
        'app_delete': '删除应用',

    ## 权限
        'perm_create': '创建权限',
        'perm_delete': '删除权限',
        'perm_assign': '配置权限',
    })

    @property
    def detail(self):
        '''
        detail for display
        '''
        return f'''
IP: {self.access.ip if self.access else ''}
Agent: {self.access.agent if self.access else ''}
URL: {self.access.url if self.access else ''}
Method: {self.access.method if self.access else ''}
DATA: {self.data.content if self.data else ''}
'''

    @property
    def subject_verbose(self):
        '''
        日志类型，用于展示
        '''
        if self.subject in self.SUBJECT_CHOICES:
            return self.SUBJECT_CHOICES[self.subject]
        return '其他'
