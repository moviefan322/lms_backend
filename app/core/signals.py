from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Player, User
from django.utils.crypto import get_random_string

@receiver(post_save, sender=Player)
def create_user_for_player(sender, instance, created, **kwargs):
    """Create a User model and send a welcome email when a Player with an email is created."""
    if created and instance.email:
        if not User.objects.filter(email=instance.email).exists():
            temp_password = get_random_string(length=12)
            
            # Create the User
            user = User.objects.create(
                email=instance.email,
                name=instance.name,
                player_profile=instance
            )
            user.set_password(temp_password)
            user.save()

            try:
                send_mail(
                    "Welcome to Our App",
                    f"Hello {user.name},\n\n"
                    f"You have been added to our system.\n"
                    f"Please log in using the following credentials:\n\n"
                    f"Email: {user.email}\n"
                    f"Temporary Password: {temp_password}\n\n"
                    f"Please change your password after logging in.\n\n"
                    f"Best regards,\n"
                    f"The Team",
                    "your-email@example.com",
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error if email sending fails
                print(f"Error sending email to {user.email}: {e}")
