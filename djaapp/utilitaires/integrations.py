"""
Utilitaires pour intégrations externes (WhatsApp, Mobile Money, etc.).
"""

import os
import requests


def partager_boutique_whatsapp(url_boutique):
    """
    Génère un lien de partage WhatsApp pour une boutique.
    """
    message = f"Découvrez ma boutique sur Djaapp ! {url_boutique}"
    return f"https://wa.me/?text={requests.utils.quote(message)}"


def initier_paiement_mobile_money(numero, montant):
    """
    Initie un paiement Mobile Money (simulé pour l'instant).
    En prod, intégrer Orange Money ou MTN MoMo API.
    """
    # Simulation
    print(f"Paiement Mobile Money simulé: {numero} - {montant} FCFA")
    # Ici, appels API réels vers Orange/MTN
    return True


def convertir_devise(montant, de="XOF", vers="EUR"):
    """
    Convertit une devise (avec taux hardcodés pour démo).
    """
    taux = {
        ("XOF", "EUR"): 0.0015,
        ("EUR", "XOF"): 655.0,
    }
    return montant * taux.get((de, vers), 1.0)
