import subprocess
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Drops and recreates the specified PostgreSQL database within Docker.'

    def handle(self, *args, **options):
        try:
            db_container = "lms_backend-db-1"
            db_user = "devuser"
            db_name = "devdb"

            subprocess.run([
                "docker", "exec", "-it", db_container, "psql", "-U", db_user, "-d", "postgres",
                "-c", f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}' AND pid <> pg_backend_pid();"
            ], check=True)

            subprocess.run([
                "docker", "exec", "-it", db_container, "psql", "-U", db_user, "-d", "postgres",
                "-c", f"DROP DATABASE IF EXISTS {db_name};"
            ], check=True)

            subprocess.run([
                "docker", "exec", "-it", db_container, "psql", "-U", db_user, "-d", "postgres",
                "-c", f"CREATE DATABASE {db_name};"
            ], check=True)

            self.stdout.write(self.style.SUCCESS(
                f"Successfully reset the '{db_name}' database."))
        except subprocess.CalledProcessError:
            raise CommandError("Failed to reset the database.")
