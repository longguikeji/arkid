#!/usr/bin/env python3

from django_scim.adapters import SCIMUser,SCIMGroup
from django_scim import exceptions
from django.contrib.auth import get_user_model


class ArkidSCIMUser(SCIMUser):
    def delete(self):
        kwargs = {self.id_field: self.id}
        self.obj.__class__.objects.filter(**kwargs).delete()


class ArkidSCIMGroup(SCIMGroup):

    def delete(self):
        kwargs = {self.id_field: self.id}
        self.obj.__class__.objects.filter(**kwargs).delete()

    def handle_add(self, path, value, operation):
        """
        Handle add operations.
        """
        if path.first_path == ('members', None, None):
            members = value or []
            ids = [member.get('value') for member in members]
            kwargs = {
                f'{self.id_field}__in': ids
            }
            users = get_user_model().objects.filter(**kwargs)

            if len(ids) != users.count():
                raise exceptions.BadRequestError('Can not add a non-existent user to group')

            for user in users:
                self.obj.user_set.add(user)

        else:
            raise exceptions.NotImplementedError

    def handle_remove(self, path, value, operation):
        """
        Handle remove operations.
        """
        if path.first_path == ('members', None, None):
            members = value or []
            ids = [member.get('value') for member in members]
            kwargs = {
                f'{self.id_field}__in': ids
            }
            users = get_user_model().objects.filter(**kwargs)

            if len(ids) != users.count():
                raise exceptions.BadRequestError('Can not remove a non-existent user from group')

            for user in users:
                self.obj.user_set.remove(user)

        else:
            raise exceptions.NotImplementedError