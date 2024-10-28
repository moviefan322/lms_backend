from django.core.management.base import BaseCommand
import psycopg2
from django.db import connection

class Command(BaseCommand):
    help = "Resets the development database."

    def handle(self, *args, **options):
        db_name = connection.settings_dict['NAME']
        db_user = connection.settings_dict['USER']
        db_host = connection.settings_dict['HOST']
        db_port = connection.settings_dict['PORT']

        # Connect to the 'postgres' database with autocommit enabled
        conn = psycopg2.connect(
            dbname='postgres',
            user=db_user,
            password=connection.settings_dict['PASSWORD'],
            host=db_host,
            port=db_port,
        )
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        with conn.cursor() as cursor:
            # Terminate connections to the target database
            cursor.execute(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}' AND pid <> pg_backend_pid();"
            )

            # Drop and recreate the target database
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
            cursor.execute(f"CREATE DATABASE {db_name};")

        conn.close()

        self.stdout.write(self.style.SUCCESS(f"Successfully reset the '{db_name}' database."))
