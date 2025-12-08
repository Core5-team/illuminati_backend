from django.urls import path
from .views import HealthView

urlpatterns = [
    path("api/health/", HealthView.as_view(), name="health"),
]
