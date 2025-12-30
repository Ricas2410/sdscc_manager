from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def area_districts(request, area_id):
    """Get districts for a specific area."""
    area = get_object_or_404(Area, id=area_id)
    districts = area.districts.filter(is_active=True).order_by('name')
    serializer = DistrictSerializer(districts, many=True)
    return Response({'districts': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def area_branches(request, area_id):
    """Get all branches for a specific area."""
    area = get_object_or_404(Area, id=area_id)
    branches = Branch.objects.filter(district__area=area, is_active=True).order_by('name')
    serializer = BranchSerializer(branches, many=True)
    return Response({'branches': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def district_branches(request, district_id):
    """Get branches for a specific district."""
    district = get_object_or_404(District, id=district_id)
    branches = district.branches.filter(is_active=True).order_by('name')
    serializer = BranchSerializer(branches, many=True)
    return Response({'branches': serializer.data})
