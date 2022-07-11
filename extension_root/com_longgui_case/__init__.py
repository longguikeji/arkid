from arkid.core import extension 
from arkid.core.translation import gettext_default as _
from arkid.core.models import User
from .models import CaseUser
from typing import List, Optional
from pydantic import Field

UserSchema = extension.create_extension_schema(
    'UserSchema',
    __file__,
    fields=[
        ('username', str, Field()),
        ('nickname', Optional[str], Field(title=_('nickname','昵称'))),
    ]
)

class CaseExtension(extension.Extension):
    
    def load(self):
        super().load()
        self.register_extend_field(CaseUser, 'nickname')
        from api.v1.schema.user import UserCreateIn,UserItemOut,UserUpdateIn,UserListItemOut
        from api.v1.schema.mine import ProfileSchemaOut, ProfileSchemaIn
        self.register_extend_api(
            UserCreateIn, UserItemOut, UserUpdateIn,
            UserListItemOut, ProfileSchemaOut, ProfileSchemaIn,
            nickname=str
        )
        
        self.register_api('/test/', 'POST', self.post_handler, tenant_path=True)
        self.register_api('/test/', 'GET', self.get_handler, response=List[UserSchema], tenant_path=True)

    def post_handler(self, request, tenant_id:str, data:UserSchema):
        tenant = request.tenant
        user = User()
        user.tenant = tenant
        user.username = data.username
        user.nickname = data.nickname
        user.save()

    def get_handler(self, request, tenant_id:str):
        users = User.expand_objects.filter(tenant=request.tenant).all()
        return list(users)
    
extension = CaseExtension()