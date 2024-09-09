import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]


def send_email(to, subject, html):
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
