"""
URL mappings from the player app.
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from player import views

router = DefaultRouter()
router.register('', views.PlayerViewSet, basename='player')

app_name = 'player'

urlpatterns = [
    path('', include(router.urls)),
]
