from django.urls import path, include
from rest_framework.routers import DefaultRouter
from league import views
from team.views import TeamViewSet, TeamPlayerViewSet

router = DefaultRouter()
router.register('', views.LeagueViewSet, basename='league')
router.register(r'(?P<league_id>\d+)/seasons',
                views.SeasonViewSet, basename='season')
router.register(
    r'(?P<league_id>\d+)/seasons/(?P<season_id>\d+)/teamseasons',
    views.TeamSeasonViewSet,
    basename='teamseason')
router.register(
    r'(?P<league_id>\d+)/seasons/(?P<season_id>\d+)/'
    r'teamseasons/(?P<teamseason_id>\d+)/teamplayers',
    TeamPlayerViewSet,
    basename='teamplayer'
)
router.register(
    r'(?P<league_id>\d+)/schedules/(?P<schedule_id>\d+)/matchnights',
    views.MatchNightViewSet,
    basename='matchnight'
)
router.register(
    r'(?P<league_id>\d+)/seasons/(?P<season_id>\d+)/matches',
    views.MatchViewSet,
    basename='match'
)
router.register(
    r'(?P<league_id>\d+)/seasons/(?P<season_id>\d+)/games',
    views.GameViewSet,
    basename='game'
)
router.register(r'(?P<league_id>\d+)/teams',
                TeamViewSet, basename='team')

router.register(r'(?P<league_id>\d+)/seasons/(?P<season_id>\d+)/schedule',
                views.ScheduleViewSet, basename='schedule')

app_name = 'league'

urlpatterns = [
    path('', include(router.urls)),
    path('schedule/<int:schedule_id>/generate/',
         views.GenerateScheduleView.as_view(), name='generate-schedule'),
]
