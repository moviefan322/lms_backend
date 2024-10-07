from django.urls import path, include
from rest_framework.routers import DefaultRouter
from league import views

router = DefaultRouter()
router.register('leagues', views.LeagueViewSet, basename='league')
router.register(r'leagues/(?P<league_id>\d+)/seasons',
                views.SeasonViewSet, basename='season')
router.register(
    r'leagues/(?P<league_id>\d+)/seasons/(?P<season_id>\d+)/schedule',
    views.ScheduleViewSet,
    basename='schedule'
)
router.register(
    r'leagues/(?P<league_id>\d+)/schedules/(?P<schedule_id>\d+)/matchnights',
    views.MatchNightViewSet,
    basename='matchnight'
)

app_name = 'league'

urlpatterns = [
    path('', include(router.urls)),

    # # MatchNight URLs
    # path('leagues/<int:league_id>/seasons/<int:season_id>/matchnights/',
    #      views.MatchNightListCreateView.as_view(), name='matchnight-list'),
    # path('leagues/<int:league_id>/seasons/<int:season_id>/matchnights/<int:matchnight_id>/',
    #      views.MatchNightDetailView.as_view(), name='matchnight-detail'),

    # # Matches standalone within season
    # path('leagues/<int:league_id>/seasons/<int:season_id>/matches/',
    #      views.MatchListCreateView.as_view(), name='match-list'),
    # path('leagues/<int:league_id>/seasons/<int:season_id>/matches/<int:match_id>/',
    #      views.MatchDetailView.as_view(), name='match-detail'),
]
