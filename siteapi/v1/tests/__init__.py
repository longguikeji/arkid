'''
tests for siteapi
只测试API请求顺畅、数据格式无误。
更复杂的逻辑测试由executer复杂
'''
from unittest import mock
import datetime
import pytz

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

    now = datetime.datetime(2019, 1, 1, tzinfo=pytz.timezone('UTC'))
    now_str = '2019-01-01T08:00:00+08:00'
    mock_now = False

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
        if self.mock_now:
            self.now_patcher = mock.patch('django.utils.timezone.now')
            self.mock_now = self.now_patcher.start()
            self.mock_now.return_value = self.now

    def tearDown(self):
        if self.mock_now:
            self.now_patcher.stop()

    def init(self):
        '''
        pre-work: create necessary objs
        '''

    def assertEqualScoped(self, first, second, keys=None, msg=""):    # pylint: disable=invalid-name
        '''
        断言两个对象的局部是否相等
        目前仅限 dict 对象
        '''
        if keys is None:
            return self.assertEqual(first, second, msg)
        for key in keys:
            self.assertEqual(first[key], second[key], msg=f'[{key}]:' + msg)


class StatefulCase:
    '''
    test case with side-effect
    '''
    def __init__(self, state, update, reset):
        '''
        init
        '''
        self.state = state
        self.reset = reset
        self.update = update
        self.excepts = {}

    def reg(self, key, input, output_with_state):    # pylint: disable=redefined-builtin
        '''
        register input-output pair
        '''
        self.excepts[key] = (input, output_with_state)

    def get_input(self, key):
        '''
        get input data
        '''
        return self.excepts[key][0]

    def get_input_with_update(self, key):
        '''
        get input data with side-effect
        '''
        self.state = self.update('GET_INPUT', self.state)
        return self.excepts[key][0]

    def get_output(self, key):
        '''
        get output data
        '''
        return self.excepts[key][1](self.state)

    def get_output_with_update(self, key):
        '''
        get output data with side-effect
        '''
        self.state = self.update('GET_OUTPUT', self.state)
        return self.excepts[key][1](self.state)

    def reset_state(self):
        '''
        reset state
        '''
        self.state = self.reset()
