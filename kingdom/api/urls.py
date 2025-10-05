from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'kingdom_api'

router = DefaultRouter()
router.register(r'kingdoms', views.KingdomViewSet)
router.register(r'kings', views.KingViewSet)
router.register(r'citizens', views.CitizenViewSet)
router.register(r'tests', views.TestViewSet)
router.register(r'test-attempts', views.TestAttemptViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('citizens/<uuid:citizen_id>/enroll/', views.enroll_citizen, name='enroll_citizen'),
    path('dashboard/', views.dashboard_data, name='dashboard_data'),
]
