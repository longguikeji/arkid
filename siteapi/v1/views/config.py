'''
config global
'''

from django.contrib.sites.models import Site
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from siteapi.v1.serializers.config import (
    ConfigSerializer,
    OrgConfigSerializer,
    MetaConfigSerializer,
    AlterAdminSerializer,
    CustomFieldSerailizer,
    NativeFieldSerializer,
    StorageConfigSerializer,
)
from siteapi.v1.serializers.user import UserSerializer
from siteapi.v1.views.org import validity_check

from oneid.permissions import IsAdminUser, CustomPerm, IsOrgOwnerOf
from oneid_meta.models import User, CustomField, NativeField

from executer.log.rdb import LOG_CLI


class ConfigAPIView(generics.RetrieveUpdateAPIView):
    """
    全局基本配置 [GET], [PATCH]
    管理员可见
    """

    serializer_class = ConfigSerializer

    permission_classes = [IsAuthenticated & (IsAdminUser | CustomPerm('system_config_write'))]

    def get_object(self):
        """
        get current site
        """
        site = Site.objects.get_current()
        site.refresh_from_db()
        return site

    def perform_update(self, serializer):
        super().perform_update(serializer)    # pylint: disable=no-member
        LOG_CLI().update_config()


class OrgConfigAPIView(generics.RetrieveUpdateAPIView):
    """
    组织基本配置 [GET], [PATCH]
    组织创建者可见
    """

    serializer_class = OrgConfigSerializer

    def get_permissions(self):
        '''
        读写权限
        '''
        self.org = validity_check(self.kwargs['oid'])
        permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | CustomPerm(f'{self.org.oid}_config_write'))]
        return [perm() for perm in permission_classes]

    def get_object(self):
        """
        get current site
        """
        return self.org

    def perform_update(self, serializer):
        super().perform_update(serializer)    # pylint: disable=no-member
        LOG_CLI().update_org_config(self.get_object())


class MetaConfigAPIView(generics.RetrieveAPIView):
    '''
    基本配置
    所用用户可见
    '''

    permission_classes = []
    authentication_classes = []

    serializer_class = MetaConfigSerializer

    def get_object(self):
        """
        get current site
        """
        site = Site.objects.get_current()
        site.refresh_from_db()
        return site


class AdminAPIView(generics.RetrieveUpdateAPIView):
    '''
    主管理员获取，更新
    '''
    permission_classes = [IsAuthenticated & IsAdminUser]
    serializer_class = AlterAdminSerializer

    def get_object(self):
        '''
        filter the boss
        '''
        admins = User.valid_objects.filter(is_boss=True)
        if admins.count() > 1:
            raise AssertionError("there more than one super manager: {}".format(admin.username for admin in admins))
        if admins.count() == 0:
            admin = User.create_user('manager', 'manager')
            admin.is_boss = True
            admin.name = "请尽快修改密码或更改主管理员"
            admin.save()
        else:
            admin = admins.first()
        return admin

    def get_serializer_class(self):
        '''
        get admin detail info
        '''
        if self.request.method == 'GET':
            return UserSerializer
        return AlterAdminSerializer


class CustomFieldListCreateAPIView(generics.ListCreateAPIView):
    '''
    自定义字段，不分页
    '''
    serializer_class = CustomFieldSerailizer

    def get_permissions(self):
        '''
        readonly for employee
        '''
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        '''
        filter the fields
        '''
        return CustomField.valid_objects.filter(subject=self.kwargs['field_subject'])

    def perform_create(self, serializer):
        '''
        save with field_subject
        '''
        serializer.save(subject=self.kwargs['field_subject'])


class CustomFieldDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    '''
    某自定义字段
    '''
    serializer_class = CustomFieldSerailizer

    def get_permissions(self):
        '''
        readonly for employee
        '''
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_object(self):
        '''
        filter the field
        '''
        field = CustomField.valid_objects.filter(uuid=self.kwargs['uuid'], subject=self.kwargs['field_subject']).first()
        if not field:
            raise NotFound
        return field


class NativeFieldListAPIView(generics.ListAPIView):
    '''
    原生字段，不分页
    '''
    serializer_class = NativeFieldSerializer

    def get_permissions(self):
        '''
        readonly for employee
        '''
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        '''
        filter the fields
        '''
        return NativeField.valid_objects.filter(subject=self.kwargs['field_subject']).order_by('name')


class NativeFieldDetailAPIView(generics.RetrieveUpdateAPIView):
    '''
    某原生字段
    '''
    serializer_class = NativeFieldSerializer

    def get_permissions(self):
        '''
        readonly for employee
        '''
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_object(self):
        '''
        filter the field
        '''
        field = NativeField.valid_objects.filter(uuid=self.kwargs['uuid'], subject=self.kwargs['field_subject']).first()
        if not field:
            raise NotFound
        return field


class StorageConfigAPIView(generics.RetrieveUpdateAPIView):
    '''
    文件存储方式
    '''
    serializer_class = StorageConfigSerializer
    permission_classes = [IsAuthenticated & (IsAdminUser | CustomPerm('system_config_write'))]

    def get_object(self):
        """
        get storage site
        """
        site = Site.objects.get_current()
        return site
