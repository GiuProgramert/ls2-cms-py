from django.test import TestCase
from unittest import TestCase, mock
from unittest.mock import patch
from notification.utils import send_email
from io import StringIO
import sys


class SendEmailTestCase(TestCase):
    """
    Casos de prueba para la función `send_email` de notification.utils.
    """

    @mock.patch('smtplib.SMTP.sendmail')  # Mock the sendmail method
    def test_send_email_success(self, mock_sendmail):
        """
        Test to verify successful email sending using send_message.
        """
        # Mock sendmail to simulate successful sending
        mock_sendmail.return_value = True

        # Call the send_email function
        response = send_email("test@example.com", "Test Subject", "<p>Test HTML content</p>")

        # Assert the response is successful
        self.assertEqual(response['status'], 'success')

        # Ensure sendmail was called once (through send_message)
        mock_sendmail.assert_called_once()

        # Additional debug information
        print(f"sendmail call count: {mock_sendmail.call_count}")


    @mock.patch('smtplib.SMTP.sendmail')  # Mock the sendmail method
    def test_send_email_failure(self, mock_sendmail):
        """
        Test to verify email sending failure.
        """
        # Simulate an exception being raised when sendmail is called
        mock_sendmail.side_effect = Exception("SMTP Error")

        # Expect an exception to be raised and check the message content
        with self.assertRaises(Exception) as context:
            send_email("test@example.com", "Test Subject", "<p>Test HTML content</p>")

        # Check that the raised exception contains the correct message
        self.assertIn("SMTP Error", str(context.exception))

        # Ensure sendmail was called once before the exception occurred
        mock_sendmail.assert_called_once()