'''
LDAP client
'''

from ldap3 import MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE
from ldap3 import BASE
from ldap3.core.exceptions import LDAPNoSuchObjectResult, LDAPExceptionError
from ldap3 import Connection as LDAPConnection
from django.conf import settings

from executer.utils.operation import list_diff

FILTER_ALL = '(objectClass=*)'
ATTRIBUTE_ALL = '*'


class Connection(LDAPConnection):
    '''
    LDAP Client
    '''
    def get_entry_by_dn(self, dn, raise_exception=False, attributes=ATTRIBUTE_ALL):
        '''
        根据dn进行查询
        :rtype: ldap3.abstract.entry.Entry

        :param str or list attribuets:ATTRIBUTE_ALL 不包括memberOf
        '''
        res = self.search(
            search_base=dn,
            search_filter=FILTER_ALL,
            attributes=attributes,
            search_scope=BASE,
        )
        if res:
            return self.entries[0]
        if raise_exception:
            raise LDAPNoSuchObjectResult
        return None

    def add(self, dn, object_class=None, attributes=None, controls=None, native=False):    # pylint: disable=arguments-differ
        '''
        默认在原基础上删除空值项
        :param bool native: 是否调用原生add
        '''
        if not native and isinstance(attributes, dict):
            for key in list(attributes):
                val = attributes[key]
                if val in ('', None):
                    del attributes[key]

        return super(Connection, self).add(dn, object_class, attributes, controls)

    def patch(self, dn, info):
        '''
        为一批属性做更新
        若属性值为空，不处理
        否则进行重置
        '''
        _info = {}
        for key, val in info.items():
            if val:
                _info.update({key: [(MODIFY_REPLACE, val)]})
        return self.modify(dn, _info)

    def modify_add(self, dn, attribute, vals):
        '''
        为指定属性增加一批值
        :param str dn:
        :param str attribute:
        :param list vals:
        '''
        if vals:
            return self.modify(dn, {attribute: [(MODIFY_ADD, vals)]})

    def modify_delete(self, dn, attribute, vals):
        '''
        为指定属性删除一批值
        :param str dn:
        :param str attribute:
        :param list vals:
        '''
        if vals:
            return self.modify(dn, {attribute: [(MODIFY_DELETE, vals)]})

    def modify_override(self, dn, attribute, vals):
        '''
        为指定属性重写一批值
        :param str dn:
        :param str attribute:
        :param list vals:
        '''
        return self.modify(dn, {attribute: [(MODIFY_REPLACE, vals)]})

    def modify_soft_override(self, dn, attribute, vals):
        '''
        为指定属性重写一批值
        根据差异多删少补
        当总数据量较大而具体差异较小时适合采用该方法
        :param str dn:
        :param str attribute:
        :param list vals:
        '''
        if vals:
            exist = self.get_vals(dn, attribute)
            vals_diff = list_diff(vals, exist)
            add_vals = vals_diff['>']
            delete_vals = vals_diff['<']
            self.modify_add(dn, attribute, add_vals)
            self.modify_delete(dn, attribute, delete_vals)
        else:
            self.modify_override(dn, attribute, '')

    def add_member(self, dn, member_dns):
        '''
        为指定entry（groupOfNames）添加一批成员
        :param str dn:
        :param list member_dns:
        '''
        return self.modify_add(dn=dn, attribute='member', vals=member_dns)

    def delete_member(self, dn, member_dns):
        '''
        为指定entry（groupOfNames）删除一批成员
        :param str dn:
        :param list member_dns:
        '''
        return self.modify_delete(dn, attribute='member', vals=member_dns)

    def force_delete(self, dn):
        '''
        删除给定entry，必然成功
        若下属包含子节点会自动先删子节点
        仅用于测试
        '''
        self.search(dn, FILTER_ALL)
        dns = [entry.entry_dn for entry in self.entries]
        reverse_dns = sorted(map(lambda _dn: _dn[::-1], dns), reverse=True)
        for _dn in reverse_dns:
            self.delete(_dn[::-1])

    def get_all_dns(self):
        '''
        返回所有dn
        仅用于测试
        '''
        self.search(settings.LDAP_BASE, FILTER_ALL, attributes=ATTRIBUTE_ALL)
        return [entry.entry_dn for entry in self.entries]

    def get_vals(self, dn, attribute, default=None):
        '''
        读取属性
        '''
        if default is None:
            default = []
        entry = self.get_entry_by_dn(dn)
        return entry.entry_attributes_as_dict.get(attribute, default)

    def get_members(self, dn, member_attribute='member'):
        '''
        读取成员,针对组、部门
        '''
        return list(filter(lambda x: x, self.get_vals(dn, member_attribute)))

    def get_groups(self, user_dn):
        '''
        查看用户属于哪些组
        `组`指oneid中的group，而非LDAP中的group
        oneid.group + oneid.dept = LDAP.group
        '''
        entry = self.get_entry_by_dn(user_dn, attributes='memberOf')
        groups = entry.entry_attributes_as_dict.get('memberOf', [])
        return list(filter(lambda dn: 'ou=group' in dn, groups))

    def get_depts(self, user_dn):
        '''
        查看用户属于哪些部门
        '''
        entry = self.get_entry_by_dn(user_dn, attributes='memberOf')
        depts = entry.entry_attributes_as_dict.get('memberOf', [])
        return list(filter(lambda dn: 'ou=dept' in dn, depts))

    def authenticate(self, user_dn, password):
        '''
        校验账号、密码
        '''
        try:
            LDAPConnection(self.server, user=user_dn, password=password, auto_bind=True)
            return True
        except LDAPExceptionError:
            return False

        return False
