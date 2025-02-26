from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import UserInfo

@receiver(user_signed_up)
def assign_role_on_social_signup(request, user, **kwargs):
    """Assign a user role when signing up via Google Auth."""
    if not UserInfo.objects.filter(user=user).exists():
        UserInfo.objects.create(user=user, role="customer") 
