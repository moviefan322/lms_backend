"""
URL mappings from the league app.
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from league import views

router = DefaultRouter()
router.register('league', views.LeagueViewSet, basename='league')

app_name = 'league'

urlpatterns = [
    path('', include(router.urls)),
]