"""
Module d'accès MySQL procédural pour Djaapp.
Toutes les fonctions sont nommées en français et utilisent des requêtes paramétrées.
"""

import mysql.connector
from mysql.connector import Error
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from config import DB_CONFIG


# ---------------------------------------------
# Connexion et exécution SQL
# ---------------------------------------------

def connecter_bdd():
    """Établir une connexion MySQL en utilisant la configuration DB_CONFIG."""
    return mysql.connector.connect(**DB_CONFIG)


def executer_requete_sql(
    requete: str,
    params: Optional[Union[Tuple[Any, ...], Dict[str, Any]]] = None,
    fetchone: bool = False,
    fetchall: bool = False,
    retourner_lastrowid: bool = False,
):
    """
    Exécuter une requête SQL paramétrée.

    - fetchone True: retourne une seule ligne (dict) ou None
    - fetchall True: retourne une liste de lignes (list[dict])
    - retourner_lastrowid True: retourne l'ID auto-incrémenté après INSERT

    Par défaut, ne retourne rien.
    """
    conn = connecter_bdd()
    try:
        curseur = conn.cursor(dictionary=True)
        curseur.execute(requete, params or ())

        resultat = None
        if fetchone:
            resultat = curseur.fetchone()
        elif fetchall:
            resultat = curseur.fetchall()
        elif retourner_lastrowid:
            # mysql-connector: lastrowid sur le curseur
            resultat = curseur.lastrowid

        conn.commit()
        return resultat
    finally:
        try:
            curseur.close()
        except Exception:
            pass
        conn.close()


# ---------------------------------------------
# Fonctions métier simples (CRUD) - Commerçants
# ---------------------------------------------

def inserer_commercant(
    nom: str,
    email: str,
    mot_de_passe_hash: str,
    telephone: Optional[str] = None,
    adresse: Optional[str] = None,
) -> int:
    """Insérer un commerçant et retourner son ID."""
    requete = (
        "INSERT INTO commercants (nom, email, mot_de_passe, telephone, adresse) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    return executer_requete_sql(
        requete,
        (nom, email, mot_de_passe_hash, telephone, adresse),
        retourner_lastrowid=True,
    )


def selectionner_commercant_par_email(email: str) -> Optional[Dict[str, Any]]:
    """Récupérer un commerçant par son email."""
    requete = "SELECT * FROM commercants WHERE email = %s LIMIT 1"
    return executer_requete_sql(requete, (email,), fetchone=True)


# ---------------------------------------------
# Boutiques
# ---------------------------------------------

def inserer_boutique(
    id_commercant: int,
    nom_boutique: str,
    description: Optional[str] = None,
    qr_code: Optional[str] = None,
) -> int:
    """Insérer une boutique et retourner son ID."""
    requete = (
        "INSERT INTO boutiques (id_commercant, nom_boutique, description, qr_code) "
        "VALUES (%s, %s, %s, %s)"
    )
    return executer_requete_sql(
        requete,
        (id_commercant, nom_boutique, description, qr_code),
        retourner_lastrowid=True,
    )


def selectionner_boutique_par_id(id_boutique: int) -> Optional[Dict[str, Any]]:
    requete = "SELECT * FROM boutiques WHERE id = %s"
    return executer_requete_sql(requete, (id_boutique,), fetchone=True)


def selectionner_boutiques_populaires(limit: int = 10) -> List[Dict[str, Any]]:
    """Sélection simple (placeholder) des boutiques populaires."""
    requete = (
        "SELECT b.*, COUNT(c.id) AS nb_commandes "
        "FROM boutiques b LEFT JOIN commandes c ON c.id_boutique = b.id "
        "GROUP BY b.id ORDER BY nb_commandes DESC LIMIT %s"
    )
    return executer_requete_sql(requete, (limit,), fetchall=True)


# ---------------------------------------------
# Produits
# ---------------------------------------------

def inserer_produit(
    id_boutique: int,
    nom: str,
    description: Optional[str],
    prix: float,
    stock: int,
    image: Optional[str] = None,
    categorie: Optional[str] = None,
) -> int:
    requete = (
        "INSERT INTO produits (id_boutique, nom, description, prix, stock, image, categorie) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    return executer_requete_sql(
        requete,
        (id_boutique, nom, description, prix, stock, image, categorie),
        retourner_lastrowid=True,
    )


def selectionner_produits_par_boutique(id_boutique: int) -> List[Dict[str, Any]]:
    requete = "SELECT * FROM produits WHERE id_boutique = %s ORDER BY id DESC"
    return executer_requete_sql(requete, (id_boutique,), fetchall=True)


def mettre_a_jour_stock_produit(id_produit: int, stock: int) -> None:
    requete = "UPDATE produits SET stock = %s WHERE id = %s"
    executer_requete_sql(requete, (stock, id_produit))


def mettre_a_jour_produit(
    id_produit: int,
    nom: Optional[str] = None,
    description: Optional[str] = None,
    prix: Optional[float] = None,
    stock: Optional[int] = None,
    categorie: Optional[str] = None,
    image: Optional[str] = None,
) -> None:
    """Mettre à jour un produit."""
    champs = []
    valeurs = []

    if nom is not None:
        champs.append("nom = %s")
        valeurs.append(nom)
    if description is not None:
        champs.append("description = %s")
        valeurs.append(description)
    if prix is not None:
        champs.append("prix = %s")
        valeurs.append(prix)
    if stock is not None:
        champs.append("stock = %s")
        valeurs.append(stock)
    if categorie is not None:
        champs.append("categorie = %s")
        valeurs.append(categorie)
    if image is not None:
        champs.append("image = %s")
        valeurs.append(image)

    if not champs:
        return

    requete = f"UPDATE produits SET {', '.join(champs)} WHERE id = %s"
    valeurs.append(id_produit)
    executer_requete_sql(requete, tuple(valeurs))


def supprimer_produit(id_produit: int) -> None:
    """Supprimer un produit."""
    requete = "DELETE FROM produits WHERE id = %s"
    executer_requete_sql(requete, (id_produit,))


# ---------------------------------------------
# Clients
# ---------------------------------------------

def inserer_client(
    nom: str,
    email: Optional[str],
    telephone: str,
    adresse: Optional[str] = None,
) -> int:
    requete = (
        "INSERT INTO clients (nom, email, telephone, adresse) VALUES (%s, %s, %s, %s)"
    )
    return executer_requete_sql(
        requete,
        (nom, email, telephone, adresse),
        retourner_lastrowid=True,
    )


def selectionner_client_par_telephone(telephone: str) -> Optional[Dict[str, Any]]:
    requete = "SELECT * FROM clients WHERE telephone = %s LIMIT 1"
    return executer_requete_sql(requete, (telephone,), fetchone=True)


def selectionner_client_par_email(email: str) -> Optional[Dict[str, Any]]:
    requete = "SELECT * FROM clients WHERE email = %s LIMIT 1"
    return executer_requete_sql(requete, (email,), fetchone=True)


# ---------------------------------------------
# Commandes
# ---------------------------------------------

def inserer_commande(
    id_client: int,
    id_boutique: int,
    total: float,
    methode_paiement: str,
    statut: str = "en_attente",
) -> int:
    requete = (
        "INSERT INTO commandes (id_client, id_boutique, total, methode_paiement, statut) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    return executer_requete_sql(
        requete,
        (id_client, id_boutique, total, methode_paiement, statut),
        retourner_lastrowid=True,
    )


def inserer_ligne_commande(
    id_commande: int,
    id_produit: int,
    quantite: int,
    prix_unitaire: float,
) -> int:
    requete = (
        "INSERT INTO lignes_commandes (id_commande, id_produit, quantite, prix_unitaire) "
        "VALUES (%s, %s, %s, %s)"
    )
    return executer_requete_sql(
        requete,
        (id_commande, id_produit, quantite, prix_unitaire),
        retourner_lastrowid=True,
    )


def mettre_a_jour_commande_statut(id_commande: int, statut: str) -> None:
    requete = "UPDATE commandes SET statut = %s WHERE id = %s"
    executer_requete_sql(requete, (statut, id_commande))


# ---------------------------------------------
# Notifications
# ---------------------------------------------

def inserer_notification(id_destinataire: int, type: str, message: str) -> int:
    requete = (
        "INSERT INTO notifications (id_destinataire, type, message) VALUES (%s, %s, %s)"
    )
    return executer_requete_sql(requete, (id_destinataire, type, message), retourner_lastrowid=True)


# ---------------------------------------------
# Mise à jour profils
# ---------------------------------------------

def mettre_a_jour_commercant(
    id_commercant: int,
    nom: Optional[str] = None,
    telephone: Optional[str] = None,
    adresse: Optional[str] = None,
    image: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> None:
    """Mettre à jour un commerçant."""
    champs = []
    valeurs = []

    if nom is not None:
        champs.append("nom = %s")
        valeurs.append(nom)
    if telephone is not None:
        champs.append("telephone = %s")
        valeurs.append(telephone)
    if adresse is not None:
        champs.append("adresse = %s")
        valeurs.append(adresse)
    if image is not None:
        champs.append("image = %s")
        valeurs.append(image)
    if latitude is not None:
        champs.append("latitude = %s")
        valeurs.append(latitude)
    if longitude is not None:
        champs.append("longitude = %s")
        valeurs.append(longitude)

    if not champs:
        return

    requete = f"UPDATE commercants SET {', '.join(champs)} WHERE id = %s"
    valeurs.append(id_commercant)
    executer_requete_sql(requete, tuple(valeurs))


def mettre_a_jour_boutique(
    id_boutique: int,
    nom_boutique: Optional[str] = None,
    description: Optional[str] = None,
    image: Optional[str] = None,
) -> None:
    """Mettre à jour une boutique."""
    champs = []
    valeurs = []

    if nom_boutique is not None:
        champs.append("nom_boutique = %s")
        valeurs.append(nom_boutique)
    if description is not None:
        champs.append("description = %s")
        valeurs.append(description)
    if image is not None:
        champs.append("image = %s")
        valeurs.append(image)

    if not champs:
        return

    requete = f"UPDATE boutiques SET {', '.join(champs)} WHERE id = %s"
    valeurs.append(id_boutique)
    executer_requete_sql(requete, tuple(valeurs))


def selectionner_commercant_par_id(id_commercant: int) -> Optional[Dict[str, Any]]:
    """Récupérer un commerçant par son ID."""
    requete = "SELECT * FROM commercants WHERE id = %s LIMIT 1"
    return executer_requete_sql(requete, (id_commercant,), fetchone=True)
