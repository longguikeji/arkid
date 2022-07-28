from arkid.core import event as core_event
from django.db.models.signals import post_save
from arkid.core.perm.permission_data import PermissionData
from arkid.core.models import(
    Permission, SystemPermission, App,
    User, Tenant, UserGroup,
)
from arkid.core.event import (
    CREATE_APP, CREATE_GROUP, DELETE_GROUP,
    DELETE_APP, APP_START, USER_REGISTER,
    SET_APP_OPENAPI_VERSION, UPDATE_APP_USER_API_PERMISSION,
    CREATE_GROUP_PERMISSION, DELETE_GROUP_PERMISSION, GROUP_REMOVE_USER,
    REMOVE_GROUP_PERMISSION_PERMISSION, UPDATE_GROUP_PERMISSION_PERMISSION,
    CREATE_PERMISSION, UPDATE_PERMISSION, DELETE_PERMISSION,
    ADD_USER_SYSTEM_PERMISSION, ADD_USER_APP_PERMISSION, GROUP_ADD_USER,
    REMOVE_USER_SYSTEM_PERMISSION, REMOVE_USER_APP_PERMISSION, OPEN_APP_PERMISSION,
    OPEN_SYSTEM_PERMISSION, CLOSE_SYSTEM_PERMISSION, CLOSE_APP_PERMISSION,
    UPDATE_ADMIN_ALL_PERMISSION, ADD_USER_MANY_PERMISSION, ADD_USERGROUP_MANY_PERMISSION,
    REMOVE_USERGROUP_SYSTEM_PERMISSION, REMOVE_USERGROUP_APP_PERMISSION,
    UPDATE_GROUP_PERMISSION, CREATE_TENANT,
)
import uuid

def user_saved(sender, instance: User, created: bool, **kwargs):
    if created:
        # print('检测到用户创建')
        user = instance
        tenant = user.tenant
        if tenant:
            tenant_id = str(tenant.id)
            user_id = str(user.id)
            pd = PermissionData()
            pd.update_single_user_system_permission(tenant_id, user_id)
            pd.update_tenant_use_app_by_user(tenant_id, user_id)


def tenant_saved(sender, instance: Tenant, created: bool, **kwargs):
    if created:
        # print('检测到租户创建')
        from arkid.common.bind_saas import bind_saas
        bind_saas(instance.id.hex)

        pd = PermissionData()
        pd.create_tenant_admin_permission(instance)


def usergroup_saved(sender, instance: UserGroup, created: bool, **kwargs):
    if created:
        # print('检测到用户分组创建')
        pd = PermissionData()
        pd.create_usergroup_permission(instance)

# def app_saved(sender, instance: App, created: bool, **kwargs):
#     if instance.entry_permission is None:
#         print('检测到应用创建')
#         app = instance
#         tenant = instance.tenant
#         permission = SystemPermission()
#         permission.name = app.name
#         permission.code = 'entry_{}'.format(uuid.uuid4())
#         permission.tenant = tenant
#         permission.category = 'entry'
#         permission.is_system = True
#         permission.save()
#         # 把应用增加一个权限
#         app.entry_permission = permission
#         app.save()
#         from arkid.core.tasks.tasks import update_arkid_all_user_permission
#         update_arkid_all_user_permission.delay(tenant.id)


class EventListener(object):
    '''
    处理事件回调
    '''
    def __init__(self):
        # core_event.listen_event(USER_REGISTER, self.register)
        core_event.listen_event(APP_START, self.app_start)
        core_event.listen_event(CREATE_GROUP, self.create_group)
        core_event.listen_event(DELETE_GROUP, self.delete_group)
        core_event.listen_event(CREATE_TENANT, self.create_tenant)
        core_event.listen_event(GROUP_ADD_USER, self.group_add_user)
        core_event.listen_event(GROUP_REMOVE_USER, self.group_remove_user)
        core_event.listen_event(CREATE_APP, self.create_app)
        core_event.listen_event(DELETE_APP, self.delete_app)
        core_event.listen_event(SET_APP_OPENAPI_VERSION, self.set_app_openapi_version)
        core_event.listen_event(UPDATE_APP_USER_API_PERMISSION, self.update_app_user_api_permission)
        core_event.listen_event(CREATE_GROUP_PERMISSION, self.create_group_permission)
        core_event.listen_event(DELETE_GROUP_PERMISSION, self.delete_group_permission)
        core_event.listen_event(UPDATE_GROUP_PERMISSION, self.edit_group_permission)
        core_event.listen_event(REMOVE_GROUP_PERMISSION_PERMISSION, self.remove_group_permission_permission)
        core_event.listen_event(UPDATE_GROUP_PERMISSION_PERMISSION, self.update_group_permission_permission)
        core_event.listen_event(CREATE_PERMISSION, self.create_permission)
        core_event.listen_event(UPDATE_PERMISSION, self.update_permission)
        core_event.listen_event(DELETE_PERMISSION, self.delete_permission)
        core_event.listen_event(ADD_USER_SYSTEM_PERMISSION, self.add_user_system_permission)
        core_event.listen_event(ADD_USER_MANY_PERMISSION, self.add_user_many_permission)
        core_event.listen_event(ADD_USERGROUP_MANY_PERMISSION, self.add_usergroup_many_permission)
        core_event.listen_event(UPDATE_ADMIN_ALL_PERMISSION, self.update_open_system_app_permission_admin)
        core_event.listen_event(ADD_USER_APP_PERMISSION, self.add_user_app_permission)
        core_event.listen_event(REMOVE_USER_SYSTEM_PERMISSION, self.remove_user_system_permission)
        core_event.listen_event(REMOVE_USER_APP_PERMISSION, self.remove_user_app_permission)
        core_event.listen_event(REMOVE_USERGROUP_SYSTEM_PERMISSION, self.remove_system_permission_to_usergroup)
        core_event.listen_event(REMOVE_USERGROUP_APP_PERMISSION, self.remove_app_permission_to_usergroup)
        core_event.listen_event(OPEN_APP_PERMISSION, self.update_open_app_permission_admin)
        core_event.listen_event(OPEN_SYSTEM_PERMISSION, self.update_open_system_permission_admin)
        core_event.listen_event(CLOSE_APP_PERMISSION, self.update_close_app_permission_user)
        core_event.listen_event(CLOSE_SYSTEM_PERMISSION, self.update_close_system_permission_user)

    # def register(self, event, **kwargs):
    #     from arkid.core.tasks.tasks import update_single_user_system_permission_and_app_permisssion
    #     user = event.data
    #     tenant = event.tenant
    #     update_single_user_system_permission_and_app_permisssion.delay(tenant.id, user.id)

    def create_tenant(self, event, **kwargs):
        tenant = event.tenant
        user = event.data
        from arkid.core.tasks.tasks import create_tenant_init_manager
        create_tenant_init_manager.delay(tenant.id, user.id)
        # permissiondata = PermissionData()
        # permissiondata.create_tenant_user_admin_permission(tenant, user)

    def app_start(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_system_permission
        update_system_permission.delay()

    def set_app_openapi_version(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_app_permission
        app = event.data
        tenant = event.tenant
        update_app_permission.delay(tenant.id, app.id)
    
    def update_app_user_api_permission(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_single_user_app_permission
        app = event.data
        # 把用户赋在app上给过来
        user = app.user
        tenant = event.tenant
        update_single_user_app_permission.delay(tenant.id, user.id, app.id)

    def create_group(self, event, **kwargs):
        group = event.data
        tenant = event.tenant
        systempermission = SystemPermission()
        systempermission.name = group.name
        systempermission.code = 'group_{}'.format(uuid.uuid4())
        systempermission.tenant = tenant
        systempermission.category = 'group'
        systempermission.is_system = True
        systempermission.operation_id = ''
        systempermission.describe = {}
        systempermission.save()
        # 同步分组权限
        group.permission = systempermission
        group.save()
        # 需要更新系统的全部用户权限
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True
    
    def delete_group(self, event, **kwargs):
        group = event.data
        tenant = event.tenant
        # 删除
        permission = group.permission
        permission.delete()
        # 分组权限清空
        group.permission = None
        group.save()
        # 需要更新系统的全部用户权限
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True
    
    def group_add_user(self, event, **kwargs):
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True

    def group_remove_user(self, event, **kwargs):
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True

    def create_app(self, event, **kwargs):
        app = event.data
        tenant = event.tenant
        permission = SystemPermission()
        permission.name = app.name
        permission.code = 'entry_{}'.format(uuid.uuid4())
        permission.tenant = tenant
        permission.category = 'entry'
        permission.is_system = True
        permission.save()
        # 把应用增加一个权限
        app.entry_permission = permission
        app.save()
        from arkid.core.tasks.tasks import update_arkid_all_user_permission
        update_arkid_all_user_permission.delay(tenant.id)
        return True
    
    def delete_app(self, event, **kwargs):
        app = event.data
        tenant = event.tenant
        permission = app.entry_permission
        if permission:
            permission.delete()
            from arkid.core.tasks.tasks import update_arkid_all_user_permission
            update_arkid_all_user_permission.delay()
        return True
    
    def create_group_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission, update_arkid_all_user_permission
        if isinstance(permission, SystemPermission):
            update_arkid_all_user_permission.delay(tenant.id)
        else:
            update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def edit_group_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission, update_arkid_all_user_permission
        if isinstance(permission, SystemPermission):
            update_arkid_all_user_permission.delay(tenant.id)
        else:
            update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def delete_group_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission, update_arkid_all_user_permission
        if isinstance(permission, SystemPermission):
            update_arkid_all_user_permission.delay(tenant.id)
        else:
            update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def remove_group_permission_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def update_open_system_permission_admin(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_open_system_permission_admin
        update_open_system_permission_admin.delay()
        return True

    def update_close_system_permission_user(self, event, **kwargs):
        items = event.data
        from arkid.core.tasks.tasks import update_close_system_permission_user
        update_close_system_permission_user.delay(items)
        return True

    def update_close_app_permission_user(self, event, **kwargs):
        items = event.data
        from arkid.core.tasks.tasks import update_close_app_permission_user
        update_close_app_permission_user.delay(items)
        return True

    def update_open_app_permission_admin(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_open_app_permission_admin
        update_open_app_permission_admin.delay()
        return True

    def update_open_system_app_permission_admin(self, event, **kwargs):
        from arkid.core.tasks.tasks import update_open_system_app_permission_admin
        update_open_system_app_permission_admin.delay()
        return True

    def update_group_permission_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission, update_arkid_all_user_permission
        if isinstance(permission, SystemPermission):
            update_arkid_all_user_permission.delay(tenant.id)
        else:
            update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def create_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def update_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def delete_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import update_only_user_app_permission
        update_only_user_app_permission.delay(tenant.id, permission.app.id)
        return True

    def add_user_system_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import add_system_permission_to_user, update_single_user_app_permission
        add_system_permission_to_user.delay(tenant.id, permission.user_id, permission.id)
        # if permission.category == 'entry' and permission.is_open and permission.tenant != tenant:
        #     app = App.valid_objects.filter(
        #         entry_permission=permission
        #     ).first()
        #     if app:
        #         config = app.config
        #         app_config = config.config
        #         if app_config.get('version') and app_config.get('openapi_uris'):
        #             # 如果给了入口权限，需要同步更新app权限
        #             update_single_user_app_permission.delay(tenant.id, permission.user_id, app.id)
        return True

    def add_user_many_permission(self, event, **kwars):
        permissions_dict = event.data
        from arkid.core.tasks.tasks import add_user_many_permission
        add_user_many_permission.delay(permissions_dict)

    def add_usergroup_many_permission(self, event, **kwars):
        permissions_dict = event.data
        from arkid.core.tasks.tasks import add_usergroup_many_permission
        add_usergroup_many_permission.delay(permissions_dict)

    def add_user_app_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import add_app_permission_to_user
        add_app_permission_to_user.delay(tenant.id, permission.app_id, permission.user_id, permission.id)
        return True

    def remove_user_system_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import remove_system_permission_to_user
        remove_system_permission_to_user.delay(tenant.id, permission.user_id, permission.id)
        return True

    def remove_user_app_permission(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import remove_app_permission_to_user
        remove_app_permission_to_user.delay(tenant.id, permission.app_id, permission.user_id, permission.id)
        return True

    def remove_system_permission_to_usergroup(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import remove_system_permission_to_usergroup
        remove_system_permission_to_usergroup.delay(tenant.id, permission.usergroup_id, permission.id)
        return True

    def remove_app_permission_to_usergroup(self, event, **kwargs):
        permission = event.data
        tenant = event.tenant
        from arkid.core.tasks.tasks import remove_app_permission_to_usergroup
        remove_app_permission_to_usergroup.delay(tenant.id, permission.app_id, permission.usergroup_id, permission.id)
        return True

EventListener()

post_save.connect(receiver=user_saved, sender=User)
post_save.connect(receiver=tenant_saved, sender=Tenant)
post_save.connect(receiver=usergroup_saved, sender=UserGroup)
# post_save.connect(receiver=app_saved, sender=App)