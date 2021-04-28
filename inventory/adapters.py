#!/usr/bin/env python3

from django_scim.adapters import SCIMUser


class ArkidSCIMUser(SCIMUser):
    def delete(self):
        kwargs = {self.id_field: self.id}
        self.obj.__class__.objects.filter(**kwargs).delete()
