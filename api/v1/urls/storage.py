from django.urls import path
from api.v1.views.storage import UploadAPIView

urlpatterns = [
    path('upload/', UploadAPIView.as_view()),
]