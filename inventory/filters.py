from django_scim.filters import FilterQuery
from django_scim.utils import get_group_model
from django.contrib.auth import get_user_model

class GroupFilterQuery(FilterQuery):
    model_getter = get_group_model
    attr_map = {
        ('displayName', None, None): 'name',
        # ('members', None, None): 'members'
    }

class UserFilterQuery(FilterQuery):
    model_getter = get_user_model
    attr_map = {
        # attr, sub attr, uri
        ('externalId', None, None): 'scim_external_id',
        ('userName', None, None): 'username',
        ('name', 'familyName', None): 'last_name',
        ('familyName', None, None): 'last_name',
        ('name', 'givenName', None): 'first_name',
        ('givenName', None, None): 'first_name',
        ('active', None, None): 'is_active',
        ('nickName', None, None): 'nickname',
        ('title', None, None): 'job_title',
        ('emails', 'value', None): 'email',
        ('phoneNumbers', 'value', None): 'mobile',
    }