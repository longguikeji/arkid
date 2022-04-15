from django.http import HttpResponse, QueryDict

import json


class JSONMiddleware:
    """
    Process application/json requests data from GET and POST requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('CONTENT_TYPE') and 'application/json' in request.META.get('CONTENT_TYPE'):
            try:
                data = json.loads(request.body)

                q_data = QueryDict('', mutable=True)
                for key, value in data.items():
                    if isinstance(value, list):
                        for x in value:
                            q_data.update({key: x})
                    else:
                        q_data.update({key: value})

                request.POST = q_data

                return self.get_response(request)
            except json.JSONDecodeError:
                return HttpResponse("JSON Decode Error", status=400)

        return self.get_response(request)