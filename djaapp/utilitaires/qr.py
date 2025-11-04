"""
Utilitaires pour génération de QR codes.
"""

import qrcode
import os
from PIL import Image
import io


def generer_qr(texte, nom_fichier=None):
    """
    Génère un QR code pour le texte donné et le sauve en PNG.
    Retourne le chemin du fichier.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(texte)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if nom_fichier is None:
        nom_fichier = f"qr_{hash(texte)}.png"

    chemin = os.path.join("static", "qr", nom_fichier)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    img.save(chemin)

    return chemin


def generer_qr_boutique(url_boutique, id_boutique):
    """
    Génère un QR code pour une boutique.
    """
    nom_fichier = f"boutique_{id_boutique}.png"
    return generer_qr(url_boutique, nom_fichier)
