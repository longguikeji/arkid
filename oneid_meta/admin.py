# pylint: disable=missing-docstring

from django.contrib import admin

from executer.core import CLI
from oneid_meta.models import (
    User,
    DingUser,
    PosixUser,
    Dept,
    DingDept,
    DeptMember,
    Group,
    DingGroup,
    ManagerGroup,
    GroupMember,
    APP,
    OAuthAPP,
    Perm,
    GroupPerm,
    DeptPerm,
    UserPerm,
    CustomField,
    NativeField,
    CustomUser,
    Invitation,
    ContactsConfig,
)


class UserAdmin(admin.ModelAdmin):

    exclude = ('django_user', )

    def save_model(self, request, obj, form, change):
        '''
        在原保存数据基础上增加密码同步
        仅在编辑时进行，仅同步密码字段
        输入明文密码即可，与密文不同即会被视为明文
        '''
        if change:
            ciphertext_pwd = User.valid_objects.get(id=obj.id).password
            new_pwd = request.POST.get('password')

            super(UserAdmin, self).save_model(request, obj, form, change)
            if ciphertext_pwd != new_pwd:
                CLI().set_user_password(obj, new_pwd)

        super(UserAdmin, self).save_model(request, obj, form, change)


class DingUserAdmin(admin.ModelAdmin):
    pass


class PosixUserAdmin(admin.ModelAdmin):
    pass


class DeptAdmin(admin.ModelAdmin):
    pass


class DingDeptAdmin(admin.ModelAdmin):
    pass


class DeptMemberAdmin(admin.ModelAdmin):
    pass


class GroupAdmin(admin.ModelAdmin):
    pass


class DingGroupAdmin(admin.ModelAdmin):
    pass


class ManagerGroupAdmin(admin.ModelAdmin):
    pass


class GroupMemberAdmin(admin.ModelAdmin):
    pass


class APPAdmin(admin.ModelAdmin):
    pass


class OAuthAPPAdmin(admin.ModelAdmin):
    pass


class PermAdmin(admin.ModelAdmin):
    pass


class GroupPermAdmin(admin.ModelAdmin):
    pass


class DeptPermAdmin(admin.ModelAdmin):
    pass


class UserPermAdmin(admin.ModelAdmin):
    pass


class CustomFieldAdmin(admin.ModelAdmin):
    pass


class CustomUserAdmin(admin.ModelAdmin):
    pass


class NativeFieldAdmin(admin.ModelAdmin):
    pass


class InvitationAdmin(admin.ModelAdmin):
    pass


class ContactsConfigAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(DingUser, DingUserAdmin)
admin.site.register(PosixUser, PosixUserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(DingDept, DingDeptAdmin)
admin.site.register(DeptMember, DeptMemberAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(DingGroup, DingGroupAdmin)
admin.site.register(ManagerGroup, ManagerGroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)
admin.site.register(APP, APPAdmin)
admin.site.register(OAuthAPP, OAuthAPPAdmin)
admin.site.register(Perm, PermAdmin)
admin.site.register(GroupPerm, GroupPermAdmin)
admin.site.register(DeptPerm, DeptPermAdmin)
admin.site.register(UserPerm, UserPermAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomField, CustomFieldAdmin)
admin.site.register(NativeField, NativeFieldAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(ContactsConfig, ContactsConfigAdmin)
