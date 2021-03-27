# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from twisted.application import service
from twisted.internet.endpoints import serverFromString
from twisted.internet.protocol import ServerFactory
from twisted.python.components import registerAdapter
from twisted.internet import reactor

from twisted.python import log
from ldaptor.inmemory import fromLDIFFile
from ldaptor.interfaces import IConnectedLDAPEntry
from ldaptor.protocols.ldap.ldapserver import LDAPServer
from io import BytesIO
import sys

from ldaptor import interfaces
from ldaptor.protocols.ldap import distinguishedname, ldaperrors
from ldaptor.protocols import pureldap

from tenant.models import Tenant
from inventory.models import User
from django.conf import settings


class Tree(object):
    def __init__(self):
        self.f = BytesIO(self.ldif())
        d = fromLDIFFile(self.f)
        d.addCallback(self.ldifRead)

    def ldifRead(self, result):
        self.f.close()
        self.db = result

    def ldif(self):
        SLAPD_DOMAIN = 'ou=people,' + settings.SLAPD_DOMAIN

        ldif = ""
        last_entry = ""
        for dc in reversed(SLAPD_DOMAIN.split(',')):
            if last_entry:
                last_entry = ','.join(
                    [
                        dc,
                        last_entry
                    ]
                )
            else:
                last_entry = dc

            entry = '\n'.join(
                [
                    u'dn: {}'.format(last_entry),
                    u'dc: {}'.format(dc.split('=')[1]),
                    u'objectClass: dcObject',                    
                    u'\n',
                ]
            )
            ldif += entry

#             ldif += """
# dn: cn=admin,{}
# cn: admin
# mail: admin@django.server.fr
# objectclass: top
# objectclass: person
# objectClass: inetOrgPerson
# gn: admin
# sn: admin
# userPassword: secret

# """.format(last_entry)
        
        tenant: Tenant
        for tenant in Tenant.active_objects.filter():
            user_data = '\n'.join(
                [
                    '',
                    u'dn: dc={},{}'.format(tenant.uuid, settings.SLAPD_DOMAIN),
                    u'displayName: {}'.format(tenant.name),
                    u'objectclass: top',
                    '',
                ]
            )
            ldif += user_data            

        # user: User
        # for user in User.active_objects.filter():
        #     user_data = '\n'.join(
        #         [
        #             '',
        #             u'dn: cn={},ou=people,{}'.format(user.email, settings.SLAPD_DOMAIN),
        #             u'cn: {}'.format(user.email),
        #             u'gn: {}'.format(user.first_name),
        #             u'displayName: {}'.format(user.fullname),
        #             u'mail: {}'.format(user.email),
        #             u'objectclass: top',
        #             u'objectclass: person',
        #             u'objectClass: inetOrgPerson',
        #             u'sn: {}'.format(user.last_name),
        #             u'userPassword: secret',
        #             '',
        #         ]
        #     )
        #     ldif += user_data

        ldif += '\n'
        return ldif.encode('utf-8')


class CustomLDAPServer(LDAPServer):

    def handle_LDAPBindRequest(self, request, controls, reply):
        if request.version != 3:
            raise ldaperrors.LDAPProtocolError(
                'Version %u not supported' % request.version)

        self.checkControls(controls)

        if request.dn == '':
            # anonymous bind
            self.boundUser = None
            return pureldap.LDAPBindResponse(resultCode=0)
        else:
            dn = distinguishedname.DistinguishedName(request.dn)
            root = interfaces.IConnectedLDAPEntry(self.factory)
            d = root.lookup(dn)

            def _no_entry(fail):
                fail.trap(ldaperrors.LDAPNoSuchObject)
                return None
            d.addErrback(_no_entry)

            def _got_entry(entry, auth):
                if entry is None:
                    raise ldaperrors.LDAPInvalidCredentials

                from django.contrib.auth import authenticate
                username = entry.get('cn').copy().pop()
                password = auth

                username = str(username, 'utf-8')
                password = str(password, 'utf-8')

                print('>>>>',  username, password)

                if not(username == 'admin' and password == settings.SLAPD_PASSWORD):
                    user = authenticate(
                        username=username,
                        password=password
                    )
                    if user is None:
                        print('>>><<<xxx')
                        raise ldaperrors.LDAPInvalidCredentials

                entry.get('userPassword').clear()
                entry.get('userPassword').update([auth])

                d = entry.bind(auth)

                def _cb(entry):
                    self.boundUser = entry
                    msg = pureldap.LDAPBindResponse(
                        resultCode=ldaperrors.Success.resultCode,
                        matchedDN=str(entry.dn))
                    return msg

                d.addCallback(_cb)
                return d

            d.addCallback(_got_entry, request.auth)
            return d


class LDAPServerFactory(ServerFactory):
    protocol = CustomLDAPServer

    def __init__(self, root):
        self.root = root

    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.debug = self.debug
        proto.factory = self
        return proto

    # @property
    # def root(self):
    #     tree = Tree()
    #     myroot = tree.db
    #     return myroot


class Command(BaseCommand):
    """
    """
    help = 'Starts the LDAP server'

    def handle(self, *args, **options):
        log.startLogging(sys.stderr)
        # We initialize our tree
        tree = Tree()
        # When the LDAP Server protocol wants to manipulate the DIT, it invokes
        # `root = interfaces.IConnectedLDAPEntry(self.factory)` to get the root
        # of the DIT.  The factory that creates the protocol must therefore
        # be adapted to the IConnectedLDAPEntry interface.
        registerAdapter(
            lambda x: x.root,
            LDAPServerFactory,
            IConnectedLDAPEntry
        )
        factory = LDAPServerFactory(tree.db)
        factory.debug = True
        application = service.Application("arkid-ldap-server")
        _ = service.IServiceCollection(application)
        server_endpoint_str = "tcp:{0}".format(settings.LDAP_PORT)
        e = serverFromString(reactor, server_endpoint_str)
        _ = e.listen(factory)
        reactor.run()
