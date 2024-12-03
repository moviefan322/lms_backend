from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, User

@receiver(post_save, sender=Player)
def create_user_for_player(sender, instance, created, **kwargs):
    """Create a User model when a Player with an email is created."""
    if created and instance.email:
        # Check if a User with this email already exists to avoid duplication
        if not User.objects.filter(email=instance.email).exists():
            User.objects.create(
                email=instance.email,
                name=instance.name,
                player_profile=instance
            )
