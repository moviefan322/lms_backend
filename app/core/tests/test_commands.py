"""
Test custom Django management commands
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test Commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready"""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError"""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])


    @patch("django.core.mail.send_mail")
    def test_send_invitation_emails_failure(self, mock_send_mail):
        """Test failure when sending invitation emails."""
        mock_send_mail.side_effect = Exception("Email delivery failed")

        with self.assertRaises(Exception) as context:
            call_command("send_email_test")

        self.assertEqual(str(context.exception), "Email delivery failed")

        mock_send_mail.assert_called_once_with(
            "Welcome to Our App",
            "You have been added to our system.",
            "your-email@example.com",
            "philipscottneumann0@gmail.com",
            fail_silently=False,
        )

