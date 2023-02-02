from .models import *
from .schema import *
from ninja import Query
from pydantic import Field
from arkid.core import extension
from typing import List, Optional
from arkid.core.constants import *
from arkid.core.api import operation
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.translation import gettext_default as _


UserCustomFieldSchema = extension.create_extension_schema(
    'UserCustomFieldSchema',
    __file__,
    fields=[]
)
UserGroupCustomFieldSchema = extension.create_extension_schema(
    'UserGroupCustomFieldSchema',
    __file__,
    fields=[]
)

class CustomFieldExtension(extension.Extension):

    CUSTOM_FIELD_EVENT = "CUSTOM_FIELDS"

    def load(self):
        super().load()
        self.register_extend_field(CustomUser, 'data', 'custom_fields')
        self.register_extend_field(CustomUserGroup, 'data', 'custom_fields')
        self.init_custom_field()
        self.register_extension_api()
        self.register_pages()

    def init_custom_field(self):
        '''
        初始化自定义字段
        '''
        from api.v1.schema.user import UserCreateIn,UserItemOut,UserUpdateIn,UserListItemOut
        from api.v1.schema.mine import ProfileSchemaOut, ProfileSchemaIn
        from api.v1.schema.user_group import UserGroupCreateIn, UserGroupDetailItemOut, UserGroupPullItemOut, UserGroupUpdateIn
        try:
            # 初始化用户自定义字段
            custom_fields = CustomField.valid_objects.filter(subject='user')
            temp_custom_fields = {}
            for custom_field in custom_fields:
                temp_custom_fields[str(custom_field.id)] = (Optional[str], Field(title=custom_field.name))
            self.register_extend_api(
                UserCustomFieldSchema,
                **temp_custom_fields
            )
            self.register_extend_api(
                UserCreateIn, UserItemOut, UserUpdateIn,
                ProfileSchemaOut, ProfileSchemaIn,
                custom_fields=(Optional[UserCustomFieldSchema],Field(title='自定义字段'))
            )
            # 初始化分组自定义字段
            custom_fields = CustomField.valid_objects.filter(subject='user_group')
            temp_custom_fields = {}
            for custom_field in custom_fields:
                temp_custom_fields[str(custom_field.id)] = (Optional[str], Field(title=custom_field.name))
            self.register_extend_api(
                UserGroupCustomFieldSchema,
                **temp_custom_fields
            )
            self.register_extend_api(
                UserGroupCreateIn, UserGroupDetailItemOut, UserGroupPullItemOut,
                UserGroupUpdateIn,
                custom_fields=(Optional[UserGroupCustomFieldSchema],Field(title='自定义字段'))
            )
        except Exception as e:
            print('第一次初始化没有自定义字段这个表')

    def register_extension_api(self):
        # 自定义字段增删改查
        self.register_api('/custom_fields/', 'GET', self.list_custom_fields, response=List[CustomFieldItemOut] , tenant_path=True)
        self.register_api('/custom_fields/', 'POST', self.create_custom_field, tenant_path=True)
        self.register_api('/custom_fields/{id}/', 'GET', self.get_custom_field, response=CustomFieldOut ,tenant_path=True)
        self.register_api('/custom_fields/{id}/', 'PUT', self.update_custom_field, tenant_path=True)
        self.register_api('/custom_fields/{id}/', 'DELETE', self.delete_custom_field, tenant_path=True)
    
    def register_pages(self):
        from .pages import user_page
        from .pages import group_page

    @operation(CustomFieldListOut, roles=[PLATFORM_ADMIN])
    @paginate(CustomPagination)
    def list_custom_fields(self, request, tenant_id:str, query_data: CustomFieldQueryIn=Query(...)):
        '''
        自定义字段列表
        '''
        subject = query_data.subject
        custom_fields = CustomField.valid_objects.filter(
            subject=subject
        ).order_by('created')
        return custom_fields

    @operation(roles=[PLATFORM_ADMIN])
    def create_custom_field(self, request, tenant_id:str, data:CustomFieldIn, subject:str='user'):
        '''
        创建自定义字段
        '''
        name = data.name
        custom_field = CustomField()
        custom_field.name = name
        custom_field.subject = subject
        custom_field.tenant = request.tenant
        custom_field.save()
        # 需要添加字段
        if custom_field.subject == 'user':
            self.register_extend_api(
                UserCustomFieldSchema,
                **{str(custom_field.id):(Optional[str], Field(title=custom_field.name))}
            )
        else:
            self.register_extend_api(
                UserGroupCustomFieldSchema,
                **{str(custom_field.id):(Optional[str], Field(title=custom_field.name))}
            )
        return self.success()

    @operation(roles=[PLATFORM_ADMIN])
    def get_custom_field(self, request, tenant_id:str, id:str):
        '''
        获取自定义字段
        '''
        custom_field = CustomField.valid_objects.filter(
            id=id
        ).first()
        return self.success(data=custom_field)

    @operation(roles=[PLATFORM_ADMIN])
    def update_custom_field(self, request, tenant_id:str, id:str, data:CustomFieldIn):
        '''
        修改自定义字段
        '''
        custom_field = CustomField.valid_objects.filter(
            id=id
        ).first()
        custom_field.name = data.name
        custom_field.save()
        if custom_field.subject == 'user':
            # 先移除字段
            self.unregister_extend_api(
                UserCustomFieldSchema,
                field_keys=[str(custom_field.id)]
            )
            # 在添加字段
            self.register_extend_api(
                UserCustomFieldSchema,
                **{str(custom_field.id):(Optional[str], Field(title=custom_field.name))}
            )
        else:
            # 先移除字段
            self.unregister_extend_api(
                UserGroupCustomFieldSchema,
                field_keys=[str(custom_field.id)]
            )
            # 在添加字段
            self.register_extend_api(
                UserGroupCustomFieldSchema,
                **{str(custom_field.id):(Optional[str], Field(title=custom_field.name))}
            )
        return self.success()

    @operation(roles=[PLATFORM_ADMIN])
    def delete_custom_field(self, request, tenant_id:str, id:str):
        '''
        删除自定义字段
        '''
        custom_field = CustomField.valid_objects.filter(
            id=id
        ).first()
        custom_field.delete()
        if custom_field.subject == 'user':
            self.unregister_extend_api(
                UserCustomFieldSchema,
                field_keys=[str(custom_field.id)]
            )
        else:
            self.unregister_extend_api(
                UserGroupCustomFieldSchema,
                field_keys=[str(custom_field.id)]
            )
        return self.success()

    
extension = CustomFieldExtension()