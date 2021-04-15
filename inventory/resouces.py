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
            'tenants',
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

    def before_import_row(self, row, row_number=None, **kwargs):
        """
        Override to add additional logic. Does nothing by default.
        """
        # row['tenants'] = kwargs.get('tenant_id', None)
        tenant_id = kwargs.get('tenant_id', None)
        row['tenants'] = tenant_id
        super().before_import_row(row, row_number, **kwargs)


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group
        fields = (
            'id',  # not null
            'name',
            'tenant',
        )
        exclude = (
            'is_active',  # not null
            'uuid',  # not null
            'is_del',  # not null
            'updated',
            'created',
        )

    def before_import_row(self, row, row_number=None, **kwargs):
        """
        Override to add additional logic. Does nothing by default.
        """
        # row['tenants'] = kwargs.get('tenant_id', None)
        tenant_id = kwargs.get('tenant_id', None)
        row['tenant'] = tenant_id
        super().before_import_row(row, row_number, **kwargs)
