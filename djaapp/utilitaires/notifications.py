"""
Utilitaires pour envoi de notifications (email, SMS, WhatsApp).
"""

import os
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText


# Configuration (à mettre dans config.py plus tard)
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMERO = os.environ.get("TWILIO_PHONE_NUMBER")

SMTP_SERVEUR = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_MDP = os.environ.get("SMTP_PASSWORD")


def envoyer_sms(telephone, message):
    """
    Envoie un SMS via Twilio.
    """
    if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMERO]):
        print(f"SMS simulé vers {telephone}: {message}")
        return True

    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_NUMERO,
            to=telephone
        )
        return True
    except Exception as e:
        print(f"Erreur envoi SMS: {e}")
        return False


def envoyer_email(destinataire, sujet, message):
    """
    Envoie un email via SMTP.
    """
    if not all([SMTP_EMAIL, SMTP_MDP]):
        print(f"Email simulé vers {destinataire}: {sujet} - {message}")
        return True

    try:
        msg = MIMEText(message)
        msg['Subject'] = sujet
        msg['From'] = SMTP_EMAIL
        msg['To'] = destinataire

        serveur = smtplib.SMTP(SMTP_SERVEUR, SMTP_PORT)
        serveur.starttls()
        serveur.login(SMTP_EMAIL, SMTP_MDP)
        serveur.sendmail(SMTP_EMAIL, destinataire, msg.as_string())
        serveur.quit()
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False


def envoyer_notification(id_destinataire, type_notif, message):
    """
    Envoie une notification selon le type (SMS/Email).
    """
    # Placeholder: récupérer info contact du destinataire
    # Pour l'instant, simuler
    if type_notif in ["commande", "alerte"]:
        # envoyer_sms("+2250700000000", message)
        # envoyer_email("test@example.com", f"Notification {type_notif}", message)
        pass
