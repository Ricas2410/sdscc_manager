from rest_framework import viewsets, permissions
from core.models import Area, District, Branch, Notification
from .serializers.core_serializers import (
    AreaSerializer, DistrictSerializer, BranchSerializer, NotificationSerializer
)

class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Area.objects.prefetch_related('districts__branches').all()
    serializer_class = AreaSerializer
    permission_classes = [permissions.IsAuthenticated]

class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.prefetch_related('branches').all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.IsAuthenticated]

class BranchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Branch.objects.select_related('district', 'pastor').all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
