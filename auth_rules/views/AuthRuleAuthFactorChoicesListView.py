from common.paginator import DefaultListPaginator
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..serializers import ChoiceSerializer

class AuthRuleAuthFactorChoicesListView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    pagination_class = DefaultListPaginator
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        return []