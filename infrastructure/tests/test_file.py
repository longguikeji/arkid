'''
test for file
'''
from django.urls import reverse
from siteapi.v1.tests import TestCase


class BugTestCase(TestCase):
    '''bug修复测试
    '''
    def test_download_file(self):
        '''请求图片失败返回404
        '''
        res = self.client.get(reverse('infra:download_file', args=('fjdkslaf.png', )))
        self.assertEqual(res.status_code, 404)
