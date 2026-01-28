"""
URL configuration for monitoring app
"""
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from .views import DWLRStationViewSet, WaterLevelViewSet, GroundwaterResourceViewSet, api_info

router = DefaultRouter()
router.register(r'stations', DWLRStationViewSet, basename='station')
router.register(r'water-levels', WaterLevelViewSet, basename='waterlevel')
router.register(r'resources', GroundwaterResourceViewSet, basename='resource')

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('api/info/', api_info, name='api_info'),
    path('api/', include(router.urls)),
]
