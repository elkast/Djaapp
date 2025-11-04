"""
Contrôleur pour la logique d'authentification.
Fonctions procédurales en français pour inscription, connexion, sessions rôle-based.
"""

import bcrypt
from flask import session, flash, redirect, url_for
from models.bdd import (
    inserer_commercant,
    selectionner_commercant_par_email,
    inserer_client,
    selectionner_client_par_telephone,
    selectionner_client_par_email,
)


def _hasher_mot_de_passe(mot_de_passe: str) -> str:
    """Hash un mot de passe avec bcrypt."""
    sel = bcrypt.gensalt()
    h = bcrypt.hashpw(mot_de_passe.encode("utf-8"), sel)
    return h.decode("utf-8")


def _verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    return bcrypt.checkpw(mot_de_passe.encode("utf-8"), hash_stocke.encode("utf-8"))


def _email_valide(email: str) -> bool:
    """Valide un email avec regex."""
    import re
    motif = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(motif, (email or "").strip()))


def _telephone_valide(telephone: str) -> bool:
    """Valide un téléphone CI (+225...)."""
    import re
    motif = r"^\+225\d{8,10}$"  # Exemple pour Côte d'Ivoire
    return bool(re.match(motif, (telephone or "").strip()))


# ---------------------------------------------
# Inscription
# ---------------------------------------------

def inscrire_commercant(nom, email, mot_de_passe, telephone=None, adresse=None):
    """
    Inscrit un commerçant.
    Vérifications: unicité email/tel, hash mdp, insert BDD, set session.
    Retourne True si succès, False sinon.
    """
    erreurs = []
    if not nom or len(nom.strip()) < 2:
        erreurs.append("Le nom doit comporter au moins 2 caractères.")
    if not _email_valide(email):
        erreurs.append("L'email est invalide.")
    if not mot_de_passe or len(mot_de_passe) < 6:
        erreurs.append("Le mot de passe doit comporter au moins 6 caractères.")
    if telephone and not _telephone_valide(telephone):
        erreurs.append("Le téléphone est invalide (format +225...).")

    if erreurs:
        for err in erreurs:
            flash(err, "error")
        return False

    # Vérifier unicité
    if selectionner_commercant_par_email(email):
        flash("Cet email est déjà utilisé.", "error")
        return False

    # Hash mdp et insert
    mot_de_passe_hash = _hasher_mot_de_passe(mot_de_passe)
    try:
        id_commercant = inserer_commercant(
            nom=nom.strip(),
            email=email.strip().lower(),
            mot_de_passe_hash=mot_de_passe_hash,
            telephone=telephone.strip() if telephone else None,
            adresse=adresse.strip() if adresse else None,
        )
        # Set session
        session["id_commercant"] = id_commercant
        session["role"] = "commercant"
        session["nom"] = nom.strip()
        session["email"] = email.strip().lower()
        session["telephone"] = telephone.strip() if telephone else None
        session["adresse"] = adresse.strip() if adresse else None
        flash("Inscription réussie.", "success")
        return True
    except Exception as e:
        flash(f"Erreur lors de l'inscription: {str(e)}", "error")
        return False


def inscrire_client(nom, telephone, email=None, adresse=None, mot_de_passe=None):
    """
    Inscrit un client (mdp optionnel pour comptes persistants).
    Vérifications: unicité tel, insert BDD, set session temp ou persistante.
    Retourne True si succès.
    """
    erreurs = []
    if not nom or len(nom.strip()) < 2:
        erreurs.append("Le nom doit comporter au moins 2 caractères.")
    if not _telephone_valide(telephone):
        erreurs.append("Le téléphone est invalide (format +225...).")
    if email and not _email_valide(email):
        erreurs.append("L'email est invalide.")
    if mot_de_passe and len(mot_de_passe) < 6:
        erreurs.append("Le mot de passe doit comporter au moins 6 caractères.")

    if erreurs:
        for err in erreurs:
            flash(err, "error")
        return False

    # Vérifier unicité tel
    if selectionner_client_par_telephone(telephone):
        flash("Ce numéro de téléphone est déjà utilisé.", "error")
        return False

    try:
        id_client = inserer_client(
            nom=nom.strip(),
            email=email.strip().lower() if email else None,
            telephone=telephone.strip(),
            adresse=adresse.strip() if adresse else None,
        )
        # Set session: si mdp fourni, persistante; sinon temp
        session["id_client"] = id_client
        session["role"] = "client"
        if mot_de_passe:
            session["client_persistant"] = True
        flash("Inscription réussie.", "success")
        return True
    except Exception as e:
        flash(f"Erreur lors de l'inscription: {str(e)}", "error")
        return False


# ---------------------------------------------
# Connexion
# ---------------------------------------------

def connecter_commercant(email, mot_de_passe):
    """
    Connecte un commerçant par email/mdp.
    Retourne True si succès.
    """
    erreurs = []
    if not _email_valide(email):
        erreurs.append("L'email est invalide.")
    if not mot_de_passe:
        erreurs.append("Le mot de passe est requis.")

    if erreurs:
        for err in erreurs:
            flash(err, "error")
        return False

    commercant = selectionner_commercant_par_email(email.strip().lower())
    if not commercant:
        flash("Email ou mot de passe incorrect.", "error")
        return False

    if not _verifier_mot_de_passe(mot_de_passe, commercant["mot_de_passe"]):
        flash("Email ou mot de passe incorrect.", "error")
        return False

    # Set session with all user data
    session["id_commercant"] = commercant["id"]
    session["role"] = "commercant"
    session["nom"] = commercant["nom"]
    session["email"] = commercant["email"]
    session["telephone"] = commercant.get("telephone")
    session["adresse"] = commercant.get("adresse")
    session["image"] = commercant.get("image")
    session["latitude"] = commercant.get("latitude")
    session["longitude"] = commercant.get("longitude")
    session["date_inscription"] = str(commercant.get("date_inscription")) if commercant.get("date_inscription") else None
    flash("Connexion réussie.", "success")
    return True


def connecter_client(telephone, mot_de_passe=None):
    """
    Connecte un client par tel (OTP simulé) ou email/mdp si persistante.
    Retourne True si succès.
    """
    erreurs = []
    if not _telephone_valide(telephone):
        erreurs.append("Le téléphone est invalide.")

    if erreurs:
        for err in erreurs:
            flash(err, "error")
        return False

    client = selectionner_client_par_telephone(telephone.strip())
    if not client:
        flash("Numéro non trouvé. Veuillez vous inscrire.", "error")
        return False

    # Si mdp fourni, vérifier pour compte persistante
    if mot_de_passe:
        if not client.get("mot_de_passe"):
            flash("Ce compte n'a pas de mot de passe. Utilisez le téléphone.", "error")
            return False
        if not _verifier_mot_de_passe(mot_de_passe, client["mot_de_passe"]):
            flash("Téléphone ou mot de passe incorrect.", "error")
            return False

    # Simuler OTP: en prod, envoyer SMS et vérifier code
    # Pour démo, accepter directement
    session["id_client"] = client["id"]
    session["role"] = "client"
    flash("Connexion réussie.", "success")
    return True


# ---------------------------------------------
# Déconnexion et Guards
# ---------------------------------------------

def deconnecter():
    """Déconnecte l'utilisateur."""
    session.clear()
    flash("Déconnexion réussie.", "info")


def guard_commercant():
    """Vérifie si session commerçant valide. Redirige sinon."""
    if session.get("role") != "commercant" or not session.get("id_commercant"):
        flash("Accès réservé aux commerçants.", "error")
        return redirect(url_for("inscription_commercant"))
    return None


def guard_client():
    """Vérifie si session client valide. Redirige sinon."""
    if session.get("role") != "client" or not session.get("id_client"):
        flash("Accès réservé aux clients.", "error")
        return redirect(url_for("inscription_client"))
    return None


# ---------------------------------------------
# Mise à jour profil
# ---------------------------------------------

def mettre_a_jour_profil_commercant(id_commercant, champs):
    """
    Met à jour le profil commerçant.
    Champs: nom, telephone, adresse.
    """
    # Placeholder: implémenter update BDD
    pass


def mettre_a_jour_profil_client(id_client, champs):
    """
    Met à jour le profil client.
    Champs: nom, email, telephone, adresse.
    """
    # Placeholder: implémenter update BDD
    pass
