"""
Custom Authentication Backend for SDSCC
Allows users to authenticate with either PIN or password
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class SDSCCBackend(BaseBackend):
    """
    Custom authentication backend that allows users to authenticate 
    with either their PIN or password.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with member_id and either PIN or password.
        The password field can contain either a PIN or actual password.
        """
        if username is None or password is None:
            return None
            
        try:
            user = User.objects.get(member_id=username.upper())
        except User.DoesNotExist:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # First try password authentication (Django's password hashing)
        if user.check_password(password):
            return user
            
        # Then try PIN authentication (stored as plain text)
        if user.pin == password:
            return user
            
        return None
    
    def get_user(self, user_id):
        """
        Retrieve user by primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
