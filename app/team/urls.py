"""
URL mappings from the team app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from team import views

router = DefaultRouter()
router.register('', views.TeamViewSet, basename='team')

app_name = 'team'

urlpatterns = [
    path('', include(router.urls)),
]

