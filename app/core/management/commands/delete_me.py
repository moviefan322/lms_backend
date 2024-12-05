from django.core.management.base import BaseCommand
from core.models import Player, User


class Command(BaseCommand):
    help = "Create a player with an email"

    def handle(self, *args, **kwargs):
        email = "philipscottneumann0@gmail.com"

        Player.objects.filter(email=email).delete()
        User.objects.filter(email=email).delete()

        print("Deleted player and user with email")
