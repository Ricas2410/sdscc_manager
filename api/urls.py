from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.core_views import AreaViewSet, DistrictViewSet, BranchViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'areas', AreaViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'branches', BranchViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
