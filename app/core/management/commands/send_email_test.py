from django.core.management.base import BaseCommand
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Send invitation emails"

    def handle(self, *args, **kwargs):
        recipient = "philipscottneumann0@gmail.com"
        try:
            send_mail(
                "Welcome to Our App",
                "You have been added to our system.",
                "your-email@example.com",
                recipient,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("Invitation emails sent!"))
        except Exception as e:
            self.stderr.write(f"Error sending email to {recipient}: {e}")
            raise
