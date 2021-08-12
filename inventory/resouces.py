#!/usr/bin/env python3

from import_export import resources
from .models import User
from .models import Group


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id',  # not null
            'username',  # unique
            'email',  # not null
            'mobile',  # not null
            'first_name',  # not null
            'last_name',  # not null
            'nickname',  # not null
            'country',  # not null
            'city',  # not null
            'job_title',  # not null
            # 'tenants',
        )
        exclude = (
            'is_superuser',  # not null
            'is_staff',  # not null
            'is_active',  # not null
            'date_joined',  # not null
            'uuid',  # not null
            'is_del',  # not null
            'updated',
            'created',
            'password',
            'last_login',
            'avatar',  # not null
        )

    def after_import_row(self, row, row_result, row_number, **kwargs):
        user_id = row_result.object_id
        user = User.active_objects.get(id=user_id)
        from tenant.models import Tenant
        tenant_id = kwargs.get('tenant_id')
        tenant = Tenant.active_objects.get(id=tenant_id)
        user.tenants.add(tenant)
        user.save()
        return super().after_import_row(row, row_result, row_number=row_number, **kwargs)


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group
        fields = (
            'id',  # not null
            'name',
            # 'tenant',
            'parent',
        )
        exclude = (
            'is_active',  # not null
            'uuid',  # not null
            'is_del',  # not null
            'updated',
            'created',
        )

    def after_import_instance(self, instance, new, row_number, **kwargs):
        from tenant.models import Tenant
        tenant_id = kwargs.get('tenant_id')
        instance.tenant_id = tenant_id 
        return super().after_import_instance(instance, new, row_number=row_number, **kwargs)
