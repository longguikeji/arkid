'''
LDAP数据操作

- User

-- Object class: 2.16.840.1.113730.3.2.2
  Short name: inetOrgPerson
  Description: RFC2798: Internet Organizational Person
  Type: Structural
  Superior: organizationalPerson
  May contain attributes:
    audio, businessCategory, carLicense, departmentNumber,
    displayName, employeeNumber, employeeType, givenName, homePhone, homePostalAddress,
    initials, jpegPhoto, labeledURI, mail, manager, mobile, o, pager, photo, roomNumber,
    secretary, uid, userCertificate, x500uniqueIdentifier, preferredLanguage,
    userSMIMECertificate, userPKCS12

-- Object class: 1.3.6.1.1.1.2.0
  Short name: posixAccount
  Description: Abstraction of an account with POSIX attributes
  Type: Auxiliary
  Superior: top
  Must contain attributes: cn, uid, uidNumber, gidNumber, homeDirectory
  May contain attributes: userPassword, loginShell, gecos, description

-- Object class: 1.3.6.1.1.1.2.1
  Short name: shadowAccount
  Description: Additional attributes for shadow passwords
  Type: Auxiliary
  Superior: top
  Must contain attributes: uid
  May contain attributes:
    userPassword, shadowLastChange, shadowMin, shadowMax,
    shadowWarning, shadowInactive, shadowExpire, shadowFlag, description

-- Object class: 1.3.6.1.4.1.24552.500.1.1.2.0
  Short name: ldapPublicKey
  Description: MANDATORY: OpenSSH LPK objectclass
  Type: Auxiliary
  Superior: top
  May contain attributes: sshPublicKey, uid

- Group & Dept

-- Object class: 2.5.6.9
  Short name: groupOfNames
  Description: RFC2256: a group of names (DNs)
  Type: Structural
  Superior: top
  Must contain attributes: member, cn
  May contain attributes: businessCategory, seeAlso, owner, ou, o, description
  OidInfo: ('2.5.6.9', 'OBJECT_CLASS', 'groupOfNames', 'RFC4519')
'''
from ldap3 import Server, MODIFY_ADD, MODIFY_DELETE
from ldap3.core.exceptions import LDAPNoSuchObjectResult, LDAPNotAllowedOnNotLeafResult
from django.conf import settings

from executer.utils.operation import list_diff
from executer.utils.password import encrypt_password
from executer.LDAP.client import Connection
from executer.core import Executer


class LDAPExecuter(Executer):
    '''
    LDAP数据操作接口
    '''

    user_object_class = ['inetOrgPerson', 'shadowAccount', 'posixAccount', 'ldapPublicKey']
    group_object_class = 'groupOfNames'
    dept_object_class = 'groupOfNames'

    def __init__(self, server='', base='', user='', password=''):
        self.base = base if base else settings.LDAP_BASE
        self.dept_base = 'ou=dept,{}'.format(self.base)
        self.group_base = 'ou=group,{}'.format(self.base)
        self.people_base = 'ou=people,{}'.format(self.base)
        self.server = Server(server if server else settings.LDAP_SERVER)
        self.conn = Connection(
            self.server,
            user=user if user else settings.LDAP_USER,
            password=password if password else settings.LDAP_PASSWORD,
            auto_bind=True,
            raise_exceptions=True,
        )

        self.group_placeholder = ''
        self.dept_placeholder = ''

    def create_user(self, user_info):
        '''
        创建用户
        '''
        attributes = {
            'uid': user_info['username'],
            'cn': user_info['username'],
            'sn': user_info['username'],
            'mail': user_info.get('email', ''),
            'mobile': user_info.get('mobile', ''),
            'displayName': user_info.get('name', ''),
            'employeeNumber': user_info.get('employee_number', ''),
        }
        posix_user = user_info.get('posix_user', None)
        if not posix_user:
            posix_user = {}
        attributes.update({
            'uidNumber': posix_user.get('uid', 500),
            'gidNumber': posix_user.get('gid', 500),
            'homeDirectory': posix_user.get('home', '.'),
            'sshPublicKey': posix_user.get('sshPublicKey', '')
        })

        dn = 'uid={},{}'.format(attributes['uid'], self.people_base)
        self.conn.add(
            dn,
            self.user_object_class,
            attributes,
        )
        return dn

    def update_user(self, user, user_info):
        '''
        更新用户
        '''
        dn = user.dn
        attributes = {
            'mail': user_info.get('email', ''),
            'mobile': user_info.get('mobile', ''),
            'displayName': user_info.get('name', ''),
            'employeeNumber': user_info.get('employee_number', '')
        }
        posix_user = user_info.get('posix_user', None)
        if posix_user:
            attributes.update({
                'uidNumber': posix_user.get('uid', ''),
                'gidNumber': posix_user.get('gid', ''),
                'homeDirectory': posix_user.get('home', ''),
                'sshPublicKey': posix_user.get('sshPublicKey', '')
            })

        self.conn.patch(dn, attributes)
        return dn

    def set_user_password(self, user, plaintext):
        '''
        更新用户密码
        '''
        dn = user.dn
        self.conn.patch(dn, {'userPassword': encrypt_password(plaintext, settings.PASSWORD_ENCRYPTION)})

    def delete_users(self, users):
        '''
        删除用户
        '''
        for user in users:
            user_dn = user.dn
            for dept_dn in self.conn.get_depts(user.dn):
                self.conn.delete_member(dept_dn, [user_dn])

            for group_dn in self.conn.get_depts(user.dn):
                self.conn.delete_member(group_dn, [user_dn])

            self.conn.delete(user_dn)

    def create_dept(self, dept_info, org):
        '''
        创建部门
        '''
        attributes = {
            'cn': dept_info.get('uid'),
            'description': dept_info.get('name'),
            'member': [self.dept_placeholder],
        }
        dn = 'cn={},{}'.format(attributes['cn'], self.dept_base)
        self.conn.add(dn, self.dept_object_class, attributes, native=True)
        return dn

    def update_dept(self, dept, dept_info):
        '''
        修改部门信息[description]
        '''
        dn = dept.dn
        description = dept_info.get('description', '')
        if description:
            self.conn.modify_override(dn, 'description', description)
        return dn

    def delete_dept(self, dept):
        '''
        删除部门
        '''
        self.conn.search(self.dept_base,
                         '(|(cn={})(objectClass={}))'.format(dept.uid, self.dept_object_class),
                         attributes='member')
        entries = self.conn.entries
        if entries:
            entry = entries[0]
            member = entry.entry_attributes_as_dict['member']
            if len(member) > 1 or (len(member) == 1 and member != [self.dept_placeholder]):
                raise LDAPNotAllowedOnNotLeafResult
            self.conn.delete(entry.entry_dn)

    def add_dept_to_dept(self, dept, parent_dept):
        '''
        将一个新部门加入到另一个部门作为其子部门
        '''
        dept_dn = 'cn={},{}'.format(dept.uid, self.dept_base)
        parent_dept_dn = parent_dept.dn
        self.conn.modify_dn(dept_dn, 'cn={}'.format(dept.uid), new_superior=parent_dept_dn)
        return 'cn={},{}'.format(dept.uid, parent_dept_dn)

    def move_dept_to_dept(self, dept, parent_dept):
        '''
        将一个已有部门移到另一个部门作为其子部门
        '''

        self.conn.search(self.dept_base, '(cn={})'.format(dept.uid))
        entries = self.conn.entries
        if not entries:
            raise LDAPNoSuchObjectResult

        dept_dn = entries[0].entry_dn

        self.conn.search(self.dept_base, '(cn={})'.format(parent_dept.uid))
        entries = self.conn.entries
        if not entries:
            raise LDAPNoSuchObjectResult

        parent_dept_dn = entries[0].entry_dn

        self.conn.modify_dn(dept_dn, 'cn={}'.format(dept.uid), new_superior=parent_dept_dn)

        return 'cn={},{}'.format(dept.uid, parent_dept.dn)

    def move_group_to_group(self, group, parent_group):
        '''
        将一个已有组移到另一个组作为其子组
        '''

        self.conn.search(self.group_base, '(cn={})'.format(group.uid))
        entries = self.conn.entries
        if not entries:
            raise LDAPNoSuchObjectResult

        group_dn = entries[0].entry_dn

        self.conn.search(self.group_base, '(cn={})'.format(parent_group.uid))
        entries = self.conn.entries
        if not entries:
            raise LDAPNoSuchObjectResult

        parent_group_dn = entries[0].entry_dn

        self.conn.modify_dn(group_dn, 'cn={}'.format(group.uid), new_superior=parent_group_dn)

        return 'cn={},{}'.format(group.uid, parent_group.dn)

    def create_group(self, group_info, org):
        '''
        创建组
        '''
        attributes = {
            'cn': group_info.get('uid'),
            'description': group_info.get('name'),
            'member': [self.group_placeholder],
        }
        dn = 'cn={},{}'.format(attributes['cn'], self.group_base)
        self.conn.add(dn, self.group_object_class, attributes, native=True)
        return dn

    def update_group(self, group, group_info):
        '''
        修改组信息[description]
        '''
        return self.update_dept(group, group_info)

    def delete_group(self, group):
        '''
        删除组
        '''
        self.conn.search(self.group_base,
                         '(|(cn={})(objectClass={}))'.format(group.uid, self.group_object_class),
                         attributes='member')
        entries = self.conn.entries
        if entries:
            entry = entries[0]
            member = entry.entry_attributes_as_dict['member']
            if len(member) > 1 or (len(member) == 1 and member != [self.group_placeholder]):
                raise LDAPNotAllowedOnNotLeafResult
            self.conn.delete(entry.entry_dn)

    def create_app_group(self, app_group_info, org):
        """
        暂时无需与LDAP对接
        """

    def update_app_group(self, app_group, app_group_info):
        """
        暂时无需与LDAP对接
        """

    def delete_app_group(self, app_group):
        """
        暂时无需与LDAP对接
        """

    def add_users_to_dept(self, users, dept):
        '''
        将一批用户添加到一个部门
        因无法递归查询，只能在父部门中也保存子部门的成员，便于查询
        递归操作（加入一个部门随即加入其父部门）由脚本定时刷新
        对外暴露的用法和RDB中一致
        '''
        user_dns = []
        dept_dn = dept.dn
        for user in users:
            user_dn = user.dn
            if dept_dn not in self.conn.get_depts(user_dn):
                user_dns.append(user_dn)
        self.conn.add_member(dept_dn, user_dns)

    def add_user_to_depts(self, user, depts):
        '''
        将一个用户添加到一批部门
        类似于add_users_to_dept
        '''
        add_dept_dns = list_diff([dept.dn for dept in depts], self.conn.get_depts(user.dn))['>']
        for dn in add_dept_dns:
            self.conn.add_member(dn, [user.dn])

    def delete_users_from_dept(self, users, dept):
        '''
        将一批用户从一个部门删除
        '''
        user_dns = []
        dept_dn = dept.dn
        for user in users:
            user_dn = user.dn
            if dept_dn in self.conn.get_depts(user_dn):
                user_dns.append(user_dn)
        self.conn.delete_member(dept_dn, user_dns)

    def delete_user_from_depts(self, user, depts):
        '''
        将一个用户从一个部门删除
        '''
        user_dn = user.dn
        delete_dept_dns = list_diff(self.conn.get_depts(user.dn), [dept.dn for dept in depts])['=']
        for dept_dn in delete_dept_dns:
            self.conn.delete_member(dept_dn, [user_dn])

    def add_group_to_group(self, group, parent_group):
        '''
        将一个新组加入到另一个组作为其子组
        '''
        group_dn = 'cn={},{}'.format(group.uid, self.group_base)
        parent_group_dn = parent_group.dn
        self.conn.modify_dn(group_dn, 'cn={}'.format(group.uid), new_superior=parent_group_dn)
        return 'cn={},{}'.format(group.uid, parent_group_dn)

    def add_appgroup_to_appgroup(self, app_group, parent_app_group):
        """
        暂时无需与钉钉对接
        """

    def move_appgroup_to_appgroup(self, app_group, parent_app_group):
        """
        暂时无需与钉钉对接
        """

    def sort_appgroups_in_appgroup(self, app_groups, parent_app_group):
        """
        暂时无需与钉钉对接
        """

    def add_users_to_group(self, users, group):
        '''
        将一批用户添加到一个组
        '''
        user_dns = []
        group_dn = group.dn
        for user in users:
            user_dn = user.dn
            if group_dn not in self.conn.get_groups(user_dn):
                user_dns.append(user_dn)
        self.conn.add_member(group_dn, user_dns)

    def add_user_to_groups(self, user, groups):
        '''
        将一个用户添加到一批组
        '''
        add_group_dns = list_diff([group.dn for group in groups], self.conn.get_groups(user.dn))['>']
        for dn in add_group_dns:
            self.conn.add_member(dn, [user.dn])

    def delete_users_from_group(self, users, group):
        '''
        将一批用户从一个组删除
        '''
        user_dns = []
        group_dn = group.dn
        for user in users:
            user_dn = user.dn
            if group_dn in self.conn.get_groups(user_dn):
                user_dns.append(user_dn)
        self.conn.delete_member(group_dn, user_dns)

    def delete_user_from_groups(self, user, groups):
        '''
        将一个用户从一批组删除
        '''
        user_dn = user.dn
        delete_group_dns = list_diff(self.conn.get_groups(user.dn), [group.dn for group in groups])['=']
        for group_dn in delete_group_dns:
            self.conn.delete_member(group_dn, [user_dn])

    def sort_groups_in_group(self, groups, parent_group):
        '''
        调整一批组在父组中的排序
        LDAP中无需维护顺序
        '''

    def sort_depts_in_dept(self, depts, parent_dept):
        '''
        调整一批部门在父部门中的排序
        LDAP中无需维护顺序
        '''

    def sort_users_in_dept(self, users, dept):
        '''
        调整一批人在部门中的排序
        LDAP中无需维护
        '''

    def sort_users_in_group(self, users, group):
        '''
        调整一批人在组中的排序
        LDAP中无需维护
        '''

    def add_apps_to_appgroup(self, apps, app_group):
        """
        将一批应用添加至一个应用分组
        LDAP中无需维护
        """

    def sort_apps_in_appgroup(self, apps, app_group):
        """
        调整一批应用在应用分组中的排序
        LDAP中无需维护
        """

    def delete_apps_from_appgroup(self, apps, app_group):
        """
        从应用分组中删除一批应用
        LDAP中无需维护
        """
