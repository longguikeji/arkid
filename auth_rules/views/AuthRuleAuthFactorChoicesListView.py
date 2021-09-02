from rest_framework import generics

class AuthRuleAuthFactorChoicesListView(generics.ListAPIView):

    def get_queryset(self):
        return super().get_queryset()