from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification, Branch
from accounts.models import UserProfile
import logging

User = get_user_model()
logger = logging.getLogger('core')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"Created profile for user {instance.member_id}")

@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance,
            title="Welcome to SDSCC",
            message=f"Welcome {instance.first_name}! Your account has been successfully created.",
            notification_type='info'
        )

@receiver(pre_delete, sender=Branch)
def prevent_branch_deletion_with_members(sender, instance, **kwargs):
    """Prevent deleting a branch if it has active members."""
    if instance.members.filter(is_active=True).exists():
        raise ValueError(f"Cannot delete branch '{instance.name}' because it has active members.")
