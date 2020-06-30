from django.db import models
from django.core.exceptions import ObjectDoesNotExist
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

    uuid = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)

    is_del = models.BooleanField(default=False, verbose_name='是否删除')
    is_active = models.BooleanField(default=True, verbose_name='是否可用')
    updated = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='更新时间')
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='创建时间')

    objects = models.Manager()
    obs = IgnoreDeletedManager()
    valid_objects = ValidManager()
    active_objects = ActiveManager()

    def delete(self, *args, **kwargs):
        self.is_del = True
        super().save()

    def kill(self, *args, **kwargs):
        super(BaseModel, self).delete()

    def online(self, *args, **kwargs):
        self.is_active = True
        self.save()

    def offline(self, *args, **kwargs):
        self.is_active = False
        self.save()

    @classmethod
    def get_from_pks(cls, pks, pk_name='id', raise_exception=False, **kwargs):
        objects = []
        for pk in pks:
            kwargs.update({pk_name: pk})
            try:
                obj = cls.valid_objects.get(**kwargs)
                objects.append(obj)
            except ObjectDoesNotExist:
                if raise_exception:
                    raise ObjectDoesNotExist(pk)
        return objects


class BaseOrderedModel(BaseModel):
    class Meta:
        abstract = True

    order_no = models.IntegerField(default=0, verbose_name='排序号')

    @staticmethod
    def sort_as(objs):
        """
        给定一批对象，按给定顺序，对该批对象进行重排。范围外对象不受影响
        [a.1, b.2, c.3, d.4, e.5]
        objs = [d, b]
        -> [a.1, d.2, c.3, b.4, e.5]
        return [d.2, b.4]
        :param list objs:
        """
        order_numbers = sorted([obj.order_no for obj in objs])
        for order_number, obj in zip(order_numbers, objs):
            obj.order_no = order_number
            obj.save()
        return objs

    @classmethod
    def get_max_order_no(cls, **filters):
        """
        返回最大order_no
        """
        res = cls.valid_objects.filter(**filters).aggregate(models.Max('order_no'))
        if res['order_no__max'] is not None:
            return res['order_no__max']
        return -1
