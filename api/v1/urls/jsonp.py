from ..views.jsonp import JsonpView
from django.urls import path

urlpatterns = [
    path('jsonp/', JsonpView.as_view()),
]