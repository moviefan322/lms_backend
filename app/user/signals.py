from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Only send email when a new user is created
        send_mail(
            "Welcome to Our App",
            f"Hello {instance.username} \
                ,\n\nYou have been added to our system. \
                Please log in to complete your registration.",
            "your-email@example.com",
            [instance.email],
            fail_silently=False,
        )
