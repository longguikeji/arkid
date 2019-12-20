'''
test for file
'''
from django.urls import reverse
from rest_framework.status import HTTP_404_NOT_FOUND
from siteapi.v1.tests import TestCase


class FileTestCase(TestCase):
    '''
    测试文件存储
    '''
    def test_download_file(self):
        '''
        请求图片失败返回404 NOT FOUND
        '''
        client = self.client
        res = client.get(reverse('infra:download_file', args=('not_exist.png', )))
        self.assertEqual(res.status_code, HTTP_404_NOT_FOUND)
