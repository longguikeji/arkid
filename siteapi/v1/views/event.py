'''
views about events
'''
import datetime

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from oneid_meta.models import User, Invitation


class InviteUserCreateAPIView(generics.CreateAPIView):
    '''
    invite user
    '''

    def post(self, request, username):    # pylint: disable=arguments-differ
        data = request.data if request.data else {}

        inviter = request.user
        invitee = User.valid_objects.filter(username=username).first()
        if not invitee:
            raise ValidationError({'invitee': ['this user not exists']})

        if invitee.is_settled:
            raise ValidationError({'invitee': ['this user has been settled']})

        # 之前的邀请即刻过期
        invitations = Invitation.valid_objects.filter(invitee=invitee, inviter=inviter)
        invitations.update(duration=datetime.timedelta(seconds=0))

        invitation = Invitation.active_objects.create(invitee=invitee, inviter=inviter)

        duration_minutes = data.get('duration_minutes', 0)
        if duration_minutes:
            invitation.duration = datetime.timedelta(minutes=duration_minutes)
            invitation.save()

        return Response({
            'uuid': invitation.uuid.hex,
            'inviter': inviter.username,
            'invitee': invitee.username,
            'key': invitation.key,
            'expired_time': invitation.expired_time,
        })
