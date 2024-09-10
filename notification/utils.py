import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]


def send_email(to, subject, html):
    """
    Función para enviar un correo electrónico utilizando la API de Resend.

    Esta función toma como parámetros el destinatario, el asunto y el contenido HTML del correo,
    construye los parámetros necesarios y los envía utilizando la biblioteca Resend.

    Parámetros:
        to (str): Dirección de correo del destinatario.
        subject (str): Asunto del correo.
        html (str): Contenido en formato HTML del correo.

    Retorna:
        email (dict): Respuesta de la API de Resend al intentar enviar el correo.

    Excepciones:
        En caso de error, se captura la excepción y se imprime un mensaje de error.
    """
    try:
        params: resend.Emails.SendParams = {
            "from": "Acme <onboarding@resend.dev>",
            "to": [to],
            "subject": subject,
            "html": html,
        }
        email = resend.Emails.send(params)
        return email
    except Exception as Error:
        print("No se pudo enviar el mail")
        print(Error)
