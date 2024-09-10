from django.test import TestCase
from unittest.mock import patch
from notification.utils import send_email
from io import StringIO
import sys


class SendEmailTestCase(TestCase):
    """
    Casos de prueba para la función `send_email` de notification.utils.
    """

    @patch("notification.utils.resend.Emails.send")
    def test_send_email_success(self, mock_send):
        """
        Test para verificar el envío exitoso de un correo electrónico.

        Este test simula que el envío del correo es exitoso y verifica que la función `send_email`
        llama correctamente a la API con los parámetros esperados y que el valor retornado es el correcto.
        """
        to = "test@example.com"
        subject = "Test Email"
        html = "<strong>Test message</strong>"

        mock_send.return_value = {"success": True}
        response = send_email(to, subject, html)

        mock_send.assert_called_once_with(
            {
                "from": "Acme <onboarding@resend.dev>",
                "to": [to],
                "subject": subject,
                "html": html,
            }
        )
        self.assertEqual(response, {"success": True})

    @patch("notification.utils.resend.Emails.send")
    def test_send_email_failure(self, mock_send):
        """
        Test para verificar el comportamiento ante el fallo en el envío de un correo electrónico.

        Simula un error en el envío y captura la salida estándar para verificar que
        se imprimen los mensajes de error adecuados.
        """
        to = "test@example.com"
        subject = "Test Email"
        html = "<strong>Test message</strong>"

        mock_send.side_effect = Exception("Error al enviar correo")

        captured_output = StringIO()
        sys.stdout = captured_output

        send_email(to, subject, html)

        sys.stdout = sys.__stdout__

        self.assertIn("No se pudo enviar el mail", captured_output.getvalue())
        self.assertIn("Error al enviar correo", captured_output.getvalue())
