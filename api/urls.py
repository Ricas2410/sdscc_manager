from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.core_views import (
    AreaViewSet, DistrictViewSet, BranchViewSet, NotificationViewSet,
    area_districts, area_branches, district_branches
)

router = DefaultRouter()
router.register(r'areas', AreaViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('areas/<uuid:area_id>/districts/', area_districts, name='area_districts'),
    path('areas/<uuid:area_id>/branches/', area_branches, name='area_branches'),
    path('districts/<uuid:district_id>/branches/', district_branches, name='district_branches'),
]
