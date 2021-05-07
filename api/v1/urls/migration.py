from django.urls import path
from api.v1.views.migration import MigrationAPIView

urlpatterns = [
    path('migration/', MigrationAPIView.as_view()),
]
