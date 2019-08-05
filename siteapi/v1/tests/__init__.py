'''
tests for siteapi
只测试API请求顺畅、数据格式无误。
更复杂的逻辑测试由executer复杂
'''
from django.test import TestCase as django_TestCase
from django.conf import settings
from django.urls import reverse

from oneid_meta.models import User, UserPerm, Perm
from common.django.drf.client import APIClient
from executer.RDB import RDBExecuter
from executer.core import cli_factory


class TestCase(django_TestCase):
    '''
    base TestCase
    '''

    client = None
    maxDiff = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anonymous = APIClient()
        self.user = User.valid_objects.get(username='admin')

    @staticmethod
    def gen_client(token):
        '''
        gen client by token
        '''
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        return client

    def login(self, username, password):
        '''
        gen test client as logined user
        '''
        token = self.anonymous.post(reverse('siteapi:user_login'), data={
            'username': username,
            'password': password,
        }).json()['token']
        return self.gen_client(token)

    def login_as(self, user):
        '''
        gen test client from user
        '''
        return self.gen_client(user.token)

    def setUp(self):
        '''
        pre-work
        '''
        self.init()
        self.client = self.login_as(self.user)

    def init(self):
        '''
        pre-work: create necessary objs
        '''
