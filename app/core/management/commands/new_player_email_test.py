from django.core.management.base import BaseCommand
from core.models import Player, User


class Command(BaseCommand):
    help = "Create a player with an email"

    def handle(self, *args, **kwargs):
        email = "philipscottneumann0@gmail.com"
        name = "Philip Neumann"

        Player.objects.filter(email=email).delete()
        User.objects.filter(email=email).delete()

        _, created = Player.objects.get_or_create(
            email=email, defaults={"name": name})

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Player created with email: {email}"))
        else:
            self.stdout.write(self.style.WARNING(
                f"Player with email {email} already exists."))
