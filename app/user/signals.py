from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
import random
import string

def generate_temporary_password(length=12):
    """Generate a random temporary password."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(characters) for _ in range(length))

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Only send email when a new user is created
        # Generate a temporary password
        temp_password = generate_temporary_password()

        # Set the temporary password for the user
        instance.set_password(temp_password)
        instance.save()

        # Send the welcome email
        login_url = "https://dummy.link/to/login/"
        email_subject = "Welcome to Our App"
        email_body = (
            f"Hello {instance.name},\n\n"
            "You have been added to our system. Below are your temporary login details:\n\n"
            f"Email: {instance.email}\n"
            f"Temporary Password: {temp_password}\n\n"
            "Please use the following link to log in and update your password:\n"
            f"{login_url}\n\n"
            "If you have any questions, please contact our support team.\n\n"
            "Best regards,\n"
            "The Your App Team"
        )

        send_mail(
            email_subject,
            email_body,
            "do-not-reply@LMS.com",
            [instance.email],
            fail_silently=False,
        )
