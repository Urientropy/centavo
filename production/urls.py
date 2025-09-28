# production/urls.py

from django.urls import path
from .views import ProductionLogListCreateView

urlpatterns = [
    path('', ProductionLogListCreateView.as_view(), name='production-log-list-create'),
]