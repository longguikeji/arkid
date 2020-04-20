'''
schema of events
'''
import json
import base64
import datetime

from django.utils import timezone
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken

from common.django.model import BaseModel, IgnoreDeletedManager

KEY = Fernet(base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32]))


class InvitationActiveManager(IgnoreDeletedManager):
    '''
    ignore expired
    '''
    def get_queryset(self):
        '''
        filter && compare expired
        '''
        queryset = super().get_queryset().filter(
        # created__gte=timezone.now() - models.F('duration'),
            inviter__is_del=False,
            inviter__is_active=True,
            invitee__is_del=False,
            invitee__is_active=True,
        )
        return queryset


class Invitation(BaseModel):
    '''
    注册邀请

    过期或接受邀请后进入invalid状态
    '''
    inviter = models.ForeignKey('oneid_meta.User',
                                related_name='inviter',
                                verbose_name='发起邀请者',
                                on_delete=models.CASCADE)
    invitee = models.ForeignKey('oneid_meta.User',
                                related_name='invitee',
                                verbose_name='被邀请者',
                                on_delete=models.CASCADE)
    org = models.ForeignKey('oneid_meta.Org', on_delete=models.CASCADE, null=True, verbose_name='组织')
    duration = models.DurationField(default=datetime.timedelta(days=1), verbose_name='有效时长')
    is_accepted = models.BooleanField(default=False, verbose_name='是否确认接受邀请')

    active_objects = InvitationActiveManager()

    @property
    def expired_time(self):
        '''
        过期时间
        '''
        return self.duration + self.created

    @property
    def is_expired(self):
        '''
        是否过期
        '''
        return self.expired_time < timezone.now()

    @property
    def key(self):
        '''
        :rtype: string
        '''
        payload = {
            'uuid': self.uuid.hex,    # pylint: disable=no-member
            'company': 'singleton',
            'invitee_mobile': self.invitee.mobile,    # pylint: disable=no-member
            'timestamp': self.created.strftime('%Y%m%d%H%M%s'),    # pylint: disable=no-member
        }
        return KEY.encrypt(json.dumps(payload).encode()).decode('utf-8')

    @classmethod
    def parse(cls, key):
        '''
        解析key以获取邀请记录
        '''
        try:
            raw_paylod = KEY.decrypt(key.encode()).decode('utf-8')
        except InvalidToken:
            return None

        try:
            paylod = json.loads(raw_paylod)
        except json.JSONDecodeError:
            return None

        return cls.active_objects.filter(
            invitee__mobile=paylod.get('invitee_mobile', ''),
            uuid=paylod.get('uuid', ''),
        ).first()
