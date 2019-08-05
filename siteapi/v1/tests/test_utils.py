'''
tests for utils
'''
# pylint: disable=missing-docstring

from siteapi.v1.tests import TestCase
from siteapi.v1.views.utils import gen_uid, data_masking
from oneid_meta.models import Perm


class UtilsTestCase(TestCase):
    def test_gen_uid(self):
        uid = gen_uid('测试ab1')
        self.assertEqual('ceshiab1', uid)

        uid = gen_uid('测试', prefix='pre', suffix='suf')
        self.assertEqual('preceshisuf', uid)

        uid = gen_uid('测试', cls=Perm)
        self.assertEqual('ceshi', uid)

        Perm.valid_objects.create(uid=uid)
        uid = gen_uid('测试', cls=Perm)
        self.assertEqual('ceshi1', uid)

        uid = gen_uid('用 户', cls=Perm)
        self.assertEqual('yonghu', uid)

        uid = gen_uid('f用 abc1 户', cls=Perm)
        self.assertEqual('fyongabc1hu', uid)

        uid = gen_uid('a用 abc1 (户）', cls=Perm)
        self.assertEqual('ayongabc1hu', uid)

        uid = gen_uid('A', cls=Perm)
        self.assertEqual('a', uid)


class DataMaskingTestCase(TestCase):
    def test_data_masking(self):
        content = '"as",{"password":"sas", "as":"s"}, [{"secret":"secret","token":"token","access_secret":"password"}]'
        expect = '"as",{"password":"******", "as":"s"}, [{"secret":"******","token":"******","access_secret":"******"}]'
        self.assertEqual(expect, data_masking(content))
