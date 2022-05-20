from django.db import models
import decimal
import datetime
import uuid


class IgnoreDeletedManager(models.Manager):

    def get_queryset(self):
        return super(IgnoreDeletedManager, self).get_queryset().filter(is_del=False)


class ValidManager(IgnoreDeletedManager):

    pass


class ActiveManager(IgnoreDeletedManager):

    def get_queryset(self):
        qs = super(ActiveManager, self).get_queryset().filter(is_active=True)
        return qs


class BaseModel(models.Model):

    class Meta:
        abstract = True
    
    id = models.UUIDField(verbose_name='ID', default=uuid.uuid4, editable=True, unique=True, primary_key=True)

    is_del = models.BooleanField(default=False, verbose_name='是否删除')
    is_active = models.BooleanField(default=True, verbose_name='是否可用')
    updated = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='更新时间')
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='创建时间')

    objects = models.Manager()
    valid_objects = ValidManager()
    active_objects = ActiveManager()

    def delete(self, *args, **kwargs):
        self.is_del = True
        self.save()

    def kill(self, *args, **kwargs):
        super(BaseModel, self).delete()

    def online(self, *args, **kwargs):
        self.is_active = True
        self.save()

    def offline(self, *args, **kwargs):
        self.is_active = False
        self.save()

    @property
    def uuid_hex(self):
        return self.uuid.hex
