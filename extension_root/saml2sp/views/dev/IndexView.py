from django.views import View
from django.shortcuts import render


class IndexView(View):
    """
    SAML2.0  SP默认页面
    """
    def get(self, request):    # pylint: disable=no-self-use
        return render(request, 'smal2sp/dev/index.html', context={})