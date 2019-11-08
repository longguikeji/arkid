'''
ldap init model
'''
from django.db import models


class LDAPOCMappings(models.Model):
    '''
    LDAP objectClass 与 数据库表 之间的映射
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        db_table = 'ldap_oc_mappings'

    name = models.CharField(max_length=128)
    keytbl = models.CharField(max_length=128)
    keycol = models.CharField(max_length=128)
    create_proc = models.CharField(max_length=512, default='', blank=True, null=True)
    delete_proc = models.CharField(max_length=512, default='', blank=True, null=True)
    expect_return = models.IntegerField()

    objects = models.Manager()

    def __str__(self):
        return '{}: {}'.format(self.name, self.keytbl)


class LDAPAttrMapping(models.Model):
    '''
    LDAP objectAttr 与 数据库字段之间的映射
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        db_table = 'ldap_attr_mappings'

    oc_map = models.ForeignKey(LDAPOCMappings, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    sel_expr = models.CharField(max_length=512)
    from_tbls = models.CharField(max_length=512)
    join_where = models.CharField(max_length=512, default='', blank=True, null=True)
    create_proc = models.CharField(max_length=512, default='', blank=True, null=True)
    delete_proc = models.CharField(max_length=512, default='', blank=True, null=True)
    param_order = models.IntegerField()
    expect_return = models.IntegerField()

    objects = models.Manager()

    def __str__(self):
        return '{}: {}'.format(self.oc_map.name, self.name)


class LDAPEntry(models.Model):
    '''
    LDAP 记录
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        db_table = 'raw_ldap_entries'

    SUBJECT_CHOICES = (
        (0, 'others'),
        (1, 'user'),
        (2, 'dept'),
        (3, 'group'),
    )

    dn = models.CharField(max_length=256)    # unique
    oc_map = models.ForeignKey(LDAPOCMappings, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT)
    keyval = models.IntegerField(default=1)
    subject = models.IntegerField(choices=SUBJECT_CHOICES, default=0)
    tag = models.IntegerField(default=0, blank=True, null=True)    # 刷新批次

    objects = models.Manager()

    def __str__(self):
        return self.dn


class LDAPEntryObjectclasses(models.Model):
    '''
    LDAP entry 与 数据库记录之间的映射
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        db_table = 'ldap_entry_objclasses'

    entry = models.ForeignKey(LDAPEntry, on_delete=models.CASCADE)
    oc_name = models.CharField(max_length=128)

    objects = models.Manager()


class Organization(models.Model):
    '''
    对应LDAP Organization
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        db_table = 'organization'

    name = models.CharField(max_length=128)
    o = models.CharField(max_length=128)

    objects = models.Manager()


class OrganizationUnit(models.Model):
    '''
    对应LDAP ou
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        db_table = 'organization_unit'

    name = models.CharField(max_length=128)
    ou = models.CharField(max_length=128)

    objects = models.Manager()


class DomainComponent(models.Model):
    '''
    对应LDAP domainComponent
    '''
    class Meta:    # pylint: disable=missing-class-docstring
        db_table = 'domain_component'

    name = models.CharField(max_length=128)
    dc = models.CharField(max_length=128)

    objects = models.Manager()
