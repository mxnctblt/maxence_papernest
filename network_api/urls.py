from django.urls import path
from .views import network_coverage

urlpatterns = [
    path('', network_coverage, name='network_coverage'),
]