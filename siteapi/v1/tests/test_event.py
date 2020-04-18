'''
tests for api about events
'''
# pylint: disable=missing-docstring

from unittest import mock
from datetime import timedelta
from django.urls import reverse

from ....siteapi.v1.tests import TestCase
from ....oneid_meta.models import User, Invitation


class InvitationTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.inviter = self.user
        self.invitee = User.objects.create(username='invitee',
                                           password='',
                                           mobile='18812341234',
                                           private_email='a@b.cn')

    def test_invite_user(self):
        res = self.client.json_post(reverse('siteapi:invite_user', args=(self.invitee.username, )))
        self.assertEqual(res.status_code, 200)
        self.assertIn('key', res.json())

        key = res.json().get('key')
        self.assertIsNotNone(Invitation.parse(key))

        res = self.client.json_post(reverse('siteapi:invite_user', args=(self.invitee.username, )),
                                    data={
                                        'duration_minutes': 60 * 24 * 10,
                                    })
        self.assertEqual(res.status_code, 200)
        invitation = Invitation.active_objects.order_by('-id').first()
        self.assertEqual(invitation.duration, timedelta(minutes=60 * 24 * 10))

    def test_invite_key(self):
        key_1 = self.client.json_post(reverse('siteapi:invite_user', args=(self.invitee.username, ))).json()['key']
        key_2 = self.client.json_post(reverse('siteapi:invite_user', args=(self.invitee.username, ))).json()['key']
        res = self.anonymous.json_post(reverse('siteapi:invitation_key_auth'),
                                       data={
                                           'key': key_1,
                                           'mobile': self.invitee.mobile
                                       })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json(), {'key': ['expired']})

        res = self.anonymous.json_post(reverse('siteapi:invitation_key_auth'),
                                       data={
                                           'key': key_2,
                                           'mobile': self.invitee.mobile
                                       })
        self.assertEqual(res.status_code, 200)

    @mock.patch('siteapi.v1.serializers.ucenter.UserActivateSMSClaimSerializer.check_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.UserActivateSMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.UserActivateEmailClaimSerializer.check_email_token')
    @mock.patch('siteapi.v1.serializers.ucenter.UserActivateEmailClaimSerializer.clear_email_token')
    def test_profile_email(self, mock_clear_email_token, mock_check_email_token, mock_clear_sms_token,
                           mock_check_sms_token):
        mock_check_email_token.return_value = {'email': 'a@b.cn'}
        mock_clear_email_token.return_value = True
        mock_check_sms_token.return_value = {'mobile': '18812341234'}
        mock_clear_sms_token.return_value = True

        invitation = Invitation.objects.create(inviter=self.inviter, invitee=self.invitee)
        res = self.anonymous.get(reverse('siteapi:ucenter_profile_invited'), data={'key': invitation.key})
        self.assertEqual(res.status_code, 200)
        self.assertIn('mobile', res.json())
        self.assertIn('private_email', res.json())

        res = self.anonymous.json_patch(reverse('siteapi:ucenter_profile_invited'),
                                        data={
                                            'key': invitation.key,
                                            'sms_token': 'sms_token',
                                            'password': 'pwd',
                                            'username': 'new'
                                        })
        self.assertEqual(res.status_code, 200)

        self.login('new', 'pwd')    # 登陆一次后 ，is_settled: False -> TRue
        res = self.anonymous.json_patch(reverse('siteapi:ucenter_profile_invited'),
                                        data={
                                            'key': invitation.key,
                                            'email_token': 'email_token',
                                            'password': 'pwd_2',
                                            'username': 'new_2'
                                        })
        self.assertEqual(res.status_code, 401)

    @mock.patch('siteapi.v1.serializers.ucenter.UserActivateSMSClaimSerializer.check_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.UserActivateSMSClaimSerializer.clear_sms_token')
    @mock.patch('siteapi.v1.serializers.ucenter.UserActivateEmailClaimSerializer.check_email_token')
    @mock.patch('siteapi.v1.serializers.ucenter.UserActivateEmailClaimSerializer.clear_email_token')
    def test_profile_sms(self, mock_clear_email_token, mock_check_email_token, mock_clear_sms_token,
                         mock_check_sms_token):
        mock_check_email_token.return_value = {'email': 'a@b.cn'}
        mock_clear_email_token.return_value = True
        mock_check_sms_token.return_value = {'mobile': '18812341234'}
        mock_clear_sms_token.return_value = True

        invitation = Invitation.objects.create(inviter=self.inviter, invitee=self.invitee)
        res = self.anonymous.get(reverse('siteapi:ucenter_profile_invited'), data={'key': invitation.key})
        self.assertEqual(res.status_code, 200)
        self.assertIn('mobile', res.json())
        self.assertIn('private_email', res.json())

        res = self.anonymous.json_patch(reverse('siteapi:ucenter_profile_invited'),
                                        data={
                                            'key': invitation.key,
                                            'email_token': 'email_token',
                                            'password': 'pwd',
                                            'username': 'new'
                                        })
        self.assertEqual(res.status_code, 200)
        invitee = User.objects.get(username='new')
        self.assertTrue(invitee.check_password('pwd'))
