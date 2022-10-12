from tests import TestCase

class TestUploadApi(TestCase):

    def test_upload(self):
        '''
        上传文件
        '''
        url = '/api/v1/tenant/{}/upload/'.format(self.tenant.id)
        # body = {
        #     "file":"din",
        # }
        # resp = self.client.post(url, body ,content_type='application/json')
        # self.assertEqual(resp.status_code, 200, resp.content.decode())