import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load email configuration from environment variables
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ["SMTP_USERNAME"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
DEFAULT_FROM = os.environ.get("DEFAULT_FROM", "CMS PY <cmspyls2@gmail.com>")


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
        # Create MIMEMultipart message
        msg = MIMEMultipart()
        msg['From'] = DEFAULT_FROM
        msg['To'] = to
        msg['Subject'] = subject

        # Attach HTML content
        msg.attach(MIMEText(html, 'html'))

        # Create SMTP session
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Send email
            server.send_message(msg)

        return {"status": "success", "message": "Email sent successfully"}
    except Exception as error:
        print("Failed to send email")
        print(error)
        raise {"status": "error", "message": str(error)}