'''
test saml api
'''
import os
from django.urls import reverse
from siteapi.v1.tests import TestCase
from oneid_meta.models import Perm
from djangosaml2idp.scripts.idpinit import run

BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

APP_3 = {
    'name': '8089',
    'remark': 'test_remark',
    'allow_any_user': True,
    'oauth_app': {},
    'ldap_app': {},
    'http_app': {},
    'saml_app': {
        'entity_id': 'http://localhost:8089/sp.xml',
        'acs': 'http://localhost:8089/acs/post',
        'sls': 'http://localhost:8089/slo/redirect',
    },
}

MAX_PERM_ID = 2

PERM_DATA = {
    'perm_id': MAX_PERM_ID + 1,
    'uid': 'app_app1_access',
    'name': '登录',
    'remark': '',
    'scope': 'app1',
    'action': 'denglu',
    'subject': 'app',
}


class SAMLTestCase(TestCase):
    '''
    测试SAML相关接口
    '''
    def setUp(self):
        super().setUp()
        for perm in Perm.valid_objects.all():
            perm.kill()
        run()

    def tearDown(self):
        if os.path.exists(BASEDIR + '/djangosaml2idp/saml2_config/idp_metadata.xml'):
            os.remove(BASEDIR + '/djangosaml2idp/saml2_config/idp_metadata.xml')
        if os.path.exists(BASEDIR + '/djangosaml2idp/certificates/mycert.pem'):
            os.remove(BASEDIR + '/djangosaml2idp/certificates/mycert.pem')
        if os.path.exists(BASEDIR + '/djangosaml2idp/certificates/mykey.pem'):
            os.remove(BASEDIR + '/djangosaml2idp/certificates/mykey.pem')

    def test_create_samlapp_by_xml(self):
        '''通过元数据上传文件
        '''
        with open(BASEDIR + '/djangosaml2idp/tests/sp_metadata_8087.xml', 'rb') as f:
            res = self.client.post(reverse('siteapi:app_list'), data={'name': 'abc', 'metafile': f})
            self.assertEqual(res.status_code, 201)

    def test_metadata(self):
        '''
        测试获取元数据接口
        '''
        res = self.client.get(reverse('djangosaml2idp:saml2_idp_metadata'))
        res = res.status_code
        self.assertEqual(res, 200)

    def test_download_metadata(self):
        '''
        测试下载元数据
        '''
        res = self.client.get(reverse('djangosaml2idp:saml2_idp_download_metadata'))
        res = res.status_code
        self.assertEqual(res, 200)

    def test_saml_request(self):
        '''
        测试SAML请求
        '''

        client = self.client
        res = client.post(reverse('siteapi:user_login'), data={'username': 'admin', 'password': 'admin'}, follows=True)
        cookie = res.cookies['spauthn']

        res2 = client.post(reverse('djangosaml2idp:saml_login_post'), data={'SAMLRequest': 'nVZbk6I6EH6fX2Gxj5TDTR2l1tkKBBAVFBQdfEMIiCIoiaD%2B%2BoM6V3fO1p7z2J3%2B%2BvJ1Op2fv47bpFagHMdZ2qW4R5b69fzwM8WsCA5kldpof0CY1CqrFIuVuksd8lTMPBxXordFWCS%2BOAHGUOQfWXGXZyTzs4R6B3B%2FBngYo5xUsT8QfJdaEbITGaYsy8dSeMzyiOFZlmXYDlMZBTiOflA18IaUsxQftiifoLyIfeTYw3cHSeZ7ySrDRGyz7Tbj%2BZjZVRJVg1VNceqRa9G%2FGTfYSzTsbRMG44zJURDnyK9gOuxScVDfkWZnMeqEYNRnydyTg%2BoE4wPSU0y8lHQpnuU6dY6vs80p2xIbbZFrL6ja%2BJUcKU6DOI3%2BTMzyZoTF3nQ6ro9HkylVm721qTKgnqsmceI1bl5Ts3zrkT97vGiq5MOrqYhSEpMT9fw9U3j3WDH9k%2FkIcQnHi5M4qlg75KimB13qXeKoj2MU6GmY3WTZS7M0rjzH5yvXBiKrLKiBJMrymKy2%2F9JpjuHYS6fr6OjXfa6R%2FqCYu%2Fh%2F6enLncmxV8crj3tzZqMQ5Sj1Uc2x9S7149vO3kynuZfiC3P4Tv5vGaC0QEm2Q0EdvxXylszfe%2FyeHea7NGEcVRf9%2F3D1maebl5mXHNBzukhyfnsYHMJsfnKm7Fnbb4zU7sOk0b3l8Nn6pnnn%2BVW%2BvyXvTb2BCpOmBelJgNqUCSdNL5Y0ntn07Ul70ghKp8edoaDBhhnOWucF2OyPNA0WChsUqrR2iE4%2FzOlRc%2Bl2joTXDB8kaHmagZHnpe0F2S1KFrZm65YweiG7kHfsQdSxzDbsyUuVb4Klt%2BplDxLnvrhJUdirRWN6sC06gAiWQzvsLKMiVdr0QHFOY2%2BQn6LuR0mfSriWNUCnjxpfmmwHesT7kOTL6xVWw0HQs6Hr8mgqy8DTZdmS%2B%2F2tOeMVh1lBYErRZr%2FaxFqnZCVgYRVAaWVYuJQtF84sS1PK%2Fnq5VoYG2GiAcxQZlLLLN47yGfSlyJxJwDfA1jx8wgwguMOU9xjjhrGVEpZuf5At9FXhm8DaSGp0wQKkluxxNFVOBtSPBjROJlS9SlfJF53yrjM05ZNfd3qXi36fi%2FRbLtl9%2FsN7DHjFKFMw%2FsyXbCnzK1bXQgOwmjzZaxN9KUBLqbh0AGhoJoCyFFsDKbKgOuarM3ozV4YnHGvbWQ93XJuOHV2FLYgPyZbj3LmgkvK4ZGKzmew5vyqxsXWaajy3XOEwQbI3nnfW62mPDon9FLOL3ZBkZS9q0nt3eGbR7CkaIamlDEdas4wzl0ZPHO5t4hZvSpYE%2FR048VIeDquN4yzXHBEiZCqM77zoxzUW%2BgJ9NAKtKCvaLCDd1ySX15okMDR763Ky2Xfw3AoBGjaRqiTceqFlG2EfHZ2tu4Eec7Bh01C0mdT2hy8NtperBVnsOsSaruStHrW4Ug85BvdLq9fQClYbC0dhlkOtX%2BC1Gk0iLgT%2B01lj92k0CkrVrp6aPXYX8KWkSz81xmd3z5kFHCilsF%2B2e8l4GBTbch3kc6JCyO2T9XLh3gbofiI%2BtLepYb5M1NeZe75%2BV8xqvelwnCWxf6reuiQr5RxVrrpU6CUYUf9jR%2B4u%2BxaTalW%2BvrBfP0XPD%2F8A', 'RelayState': 'WuebuDYolP1rpg9t'}, cookie={'spauthn': cookie})    # pylint: disable=line-too-long
        self.assertEqual(res2.status_code, 302)

        res3 = client.post(reverse('djangosaml2idp:saml_login_post'), data={'SAMLRequest': 'nVZbk6I6EH6fX2Gxj5TDTR2l1tkKBBAVFBQdfEMIiCIoiaD%2B%2BoM6V3fO1p7z2J3%2B%2BvJ1Op2fv47bpFagHMdZ2qW4R5b69fzwM8WsCA5kldpof0CY1CqrFIuVuksd8lTMPBxXordFWCS%2BOAHGUOQfWXGXZyTzs4R6B3B%2FBngYo5xUsT8QfJdaEbITGaYsy8dSeMzyiOFZlmXYDlMZBTiOflA18IaUsxQftiifoLyIfeTYw3cHSeZ7ySrDRGyz7Tbj%2BZjZVRJVg1VNceqRa9G%2FGTfYSzTsbRMG44zJURDnyK9gOuxScVDfkWZnMeqEYNRnydyTg%2BoE4wPSU0y8lHQpnuU6dY6vs80p2xIbbZFrL6ja%2BJUcKU6DOI3%2BTMzyZoTF3nQ6ro9HkylVm721qTKgnqsmceI1bl5Ts3zrkT97vGiq5MOrqYhSEpMT9fw9U3j3WDH9k%2FkIcQnHi5M4qlg75KimB13qXeKoj2MU6GmY3WTZS7M0rjzH5yvXBiKrLKiBJMrymKy2%2F9JpjuHYS6fr6OjXfa6R%2FqCYu%2Fh%2F6enLncmxV8crj3tzZqMQ5Sj1Uc2x9S7149vO3kynuZfiC3P4Tv5vGaC0QEm2Q0EdvxXylszfe%2FyeHea7NGEcVRf9%2F3D1maebl5mXHNBzukhyfnsYHMJsfnKm7Fnbb4zU7sOk0b3l8Nn6pnnn%2BVW%2BvyXvTb2BCpOmBelJgNqUCSdNL5Y0ntn07Ul70ghKp8edoaDBhhnOWucF2OyPNA0WChsUqrR2iE4%2FzOlRc%2Bl2joTXDB8kaHmagZHnpe0F2S1KFrZm65YweiG7kHfsQdSxzDbsyUuVb4Klt%2BplDxLnvrhJUdirRWN6sC06gAiWQzvsLKMiVdr0QHFOY2%2BQn6LuR0mfSriWNUCnjxpfmmwHesT7kOTL6xVWw0HQs6Hr8mgqy8DTZdmS%2B%2F2tOeMVh1lBYErRZr%2FaxFqnZCVgYRVAaWVYuJQtF84sS1PK%2Fnq5VoYG2GiAcxQZlLLLN47yGfSlyJxJwDfA1jx8wgwguMOU9xjjhrGVEpZuf5At9FXhm8DaSGp0wQKkluxxNFVOBtSPBjROJlS9SlfJF53yrjM05ZNfd3qXi36fi%2FRbLtl9%2FsN7DHjFKFMw%2FsyXbCnzK1bXQgOwmjzZaxN9KUBLqbh0AGhoJoCyFFsDKbKgOuarM3ozV4YnHGvbWQ93XJuOHV2FLYgPyZbj3LmgkvK4ZGKzmew5vyqxsXWaajy3XOEwQbI3nnfW62mPDon9FLOL3ZBkZS9q0nt3eGbR7CkaIamlDEdas4wzl0ZPHO5t4hZvSpYE%2FR048VIeDquN4yzXHBEiZCqM77zoxzUW%2BgJ9NAKtKCvaLCDd1ySX15okMDR763Ky2Xfw3AoBGjaRqiTceqFlG2EfHZ2tu4Eec7Bh01C0mdT2hy8NtperBVnsOsSaruStHrW4Ug85BvdLq9fQClYbC0dhlkOtX%2BC1Gk0iLgT%2B01lj92k0CkrVrp6aPXYX8KWkSz81xmd3z5kFHCilsF%2B2e8l4GBTbch3kc6JCyO2T9XLh3gbofiI%2BtLepYb5M1NeZe75%2BV8xqvelwnCWxf6reuiQr5RxVrrpU6CUYUf9jR%2B4u%2BxaTalW%2BvrBfP0XPD%2F8A', 'RelayState': 'WuebuDYolP1rpg9t'})    # pylint: disable=line-too-long
        self.assertEqual(res3.status_code, 302)

    def test_script(self):
        '''
        测试初始化文件创建
        '''
        metadata_made = os.path.exists(BASEDIR + '/djangosaml2idp/saml2_config/idp_metadata.xml')
        cert_made = os.path.exists(BASEDIR + '/djangosaml2idp/certificates/mycert.pem')
        key_made = os.path.exists(BASEDIR + '/djangosaml2idp/certificates/mykey.pem')
        self.assertEqual(True, metadata_made)
        self.assertEqual(True, cert_made)
        self.assertEqual(True, key_made)
