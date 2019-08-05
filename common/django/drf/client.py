import json

from rest_framework.test import APIClient as DRF_APIClient


class APIClient(DRF_APIClient):

    def json_post(self, path, data=None, follow=False, **extra):
        return self.post(
            path, data=json.dumps(data), follow=follow,
            content_type='application/json', **extra
        )

    def json_put(self, path, data=None, follow=False, **extra):
        return self.put(
            path, data=json.dumps(data), follow=follow,
            content_type='application/json', **extra
        )

    def json_patch(self, path, data=None, follow=False, **extra):
        return self.patch(
            path, data=json.dumps(data), follow=follow,
            content_type='application/json', **extra
        )
