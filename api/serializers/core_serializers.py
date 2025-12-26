from rest_framework import serializers
from core.models import Area, District, Branch, Notification
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'member_id', 'first_name', 'last_name', 'role', 'branch')

class BranchSerializer(serializers.ModelSerializer):
    pastor = UserSerializer(read_only=True)
    
    class Meta:
        model = Branch
        fields = ('id', 'name', 'code', 'district', 'pastor', 'member_count')

class DistrictSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)
    
    class Meta:
        model = District
        fields = ('id', 'name', 'code', 'area', 'branches')

class AreaSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)
    
    class Meta:
        model = Area
        fields = ('id', 'name', 'code', 'districts')

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'notification_type', 'is_read', 'created_at')
