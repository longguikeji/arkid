"""
statistics
"""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from oneid.permissions import IsAdminUser
from oneid_meta.models import User
from oneid.statistics import UserStatistics


class UserStatisticView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated & IsAdminUser]

    def get(self, request):
        """
        get user active statistic
        """

        total_count = User.valid_objects.count()
        res = {'total_count': total_count, 'active_count': UserStatistics.get_active_count()}
        return Response(data=res)
