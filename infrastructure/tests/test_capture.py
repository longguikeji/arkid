'''
tests for captcha
'''
# pylint: disable=missing-docstring

from unittest import mock

from django.urls import reverse

from siteapi.v1.tests import TestCase


class CaptchaTestCase(TestCase):
    def test_get_captcha(self):
        res = self.anonymous.get(reverse('infra:captcha'))
        self.assertIn('captcha_key', res.json())
        self.assertIn('captcha_img', res.json())

    @mock.patch('infrastructure.views.captcha_img.check_captcha')
    def test_check_captcha(self, mock_check_captcha):
        mock_check_captcha.return_value = True
        res = self.anonymous.post(reverse('infra:captcha'), data={'captcha': 'captcha', 'captcha_key': 'captcha_key'})
        self.assertEqual(res.status_code, 200)

        mock_check_captcha.return_value = False
        res = self.anonymous.post(reverse('infra:captcha'), data={'captcha': 'captcha', 'captcha_key': 'captcha_key'})
        self.assertEqual(res.status_code, 400)
