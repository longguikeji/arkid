import json
import ldap3
from ldap3 import Server, Connection

from arkid.common.logger import logger


class LdapAuth:
    def __init__(self, **settings):
        self.host = settings['host']
        self.port = settings['port']
        self.use_tls = settings['use_tls']
        self.bind_dn = settings['bind_dn']
        self.bind_password = settings['bind_password']
        self.user_search_base = settings['user_search_base']
        self.user_object_class = settings['user_object_class']
        self.username_attr = settings['username_attr']
        self.connect_timeout = settings.get('connect_timeout')
        self.receive_timeout = settings.get('receive_timeout')

    def get_connection(self):
        server = Server(
            host=self.host,
            port=self.port,
            use_ssl=self.use_tls,
            # get_info=ldap3.NONE,
            connect_timeout=self.connect_timeout,
        )
        conn = Connection(
            server,
            user=self.bind_dn,
            password=self.bind_password,
            auto_bind=True,
            # raise_exceptions=False,
            receive_timeout=self.receive_timeout,
        )
        return conn

    def get_user_from_ldap(self, conn, username):
        search_base = self.user_search_base
        search_filter = f'(&(objectclass={self.user_object_class})({self.username_attr}={username}))'
        res = conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=ldap3.SUBTREE,
                attributes=ldap3.ALL_ATTRIBUTES,
                size_limit=1,
        )
        if res:
            entries = json.loads(conn.response_to_json())['entries']
            if entries:
                result = entries[0]
                return result

        return None

    def authenticate(self, username, password):
        try:
            conn = self.get_connection()
            ldap_user = self.get_user_from_ldap(conn, username)
            if not ldap_user:
                return None, 'User does not exist in ldap'
            dn = ldap_user['dn']
            if not conn.rebind(dn, password):
                return None, 'Wrong password'
            conn.unbind()
            return ldap_user['attributes'], None
        except Exception as e:
            logger.warning('LDAP connection error: %s' % str(e))
            return None, 'LDAP connect failed'
