'''
测试bug修改
'''
import os
from django.urls import reverse
from rest_framework.test import APIClient
from siteapi.v1.tests import TestCase

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDBCase(TestCase):
    '''测试bug修改结果
    '''
    def test_query_userlist(self):
        '''从test.sql数据中模糊搜索用户列表名称包含"一",预期为6个
        '''
        client = APIClient()
        res = client.post(reverse('siteapi:user_login'), data={'username': 'admin', 'password': 'admin'})
        token = res.json()['token']
        client.credentials(HTTP_AUTHORIZATION='token ' + token)
        res = client.get(reverse('siteapi:user_list'), data={'keyword': '一'})
        user_list = res.json()['results']
        expect_count = 6
        self.assertEqual(expect_count, len(user_list))
