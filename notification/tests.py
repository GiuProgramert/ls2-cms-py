from django.test import TestCase
from unittest.mock import patch
from notification.utils import send_email
from io import StringIO
import sys


class SendEmailTestCase(TestCase):
    @patch("notification.utils.resend.Emails.send")
    def test_send_email_success(self, mock_send):
        # Preparar los parámetros de prueba
        to = "test@example.com"
        subject = "Test Email"
        html = "<strong>Test message</strong>"

        # Simular que el envío de correo fue exitoso
        mock_send.return_value = {"success": True}

        # Ejecutar la función que queremos testear
        response = send_email(to, subject, html)

        # Comprobar que se llamó a la función con los parámetros correctos
        mock_send.assert_called_once_with(
            {
                "from": "Acme <onboarding@resend.dev>",
                "to": [to],
                "subject": subject,
                "html": html,
            }
        )

        # Verificar que el retorno de la función es el esperado
        self.assertEqual(response, {"success": True})

    @patch("notification.utils.resend.Emails.send")
    def test_send_email_failure(self, mock_send):
        # Preparar los parámetros de prueba
        to = "test@example.com"
        subject = "Test Email"
        html = "<strong>Test message</strong>"

        # Simular un error durante el envío del correo
        mock_send.side_effect = Exception("Error al enviar correo")

        # Capturar la salida estándar (print)
        captured_output = StringIO()
        sys.stdout = captured_output

        # Ejecutar la función
        send_email(to, subject, html)

        # Restaurar sys.stdout
        sys.stdout = sys.__stdout__

        # Verificar que el mensaje de error haya sido impreso
        self.assertIn("No se pudo enviar el mail", captured_output.getvalue())
        self.assertIn("Error al enviar correo", captured_output.getvalue())
