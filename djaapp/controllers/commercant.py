"""
Contrôleur pour la logique métier des commerçants.
Fonctions procédurales en français pour gérer boutiques, produits, commandes.
"""

from models.bdd import (
    inserer_boutique,
    selectionner_boutique_par_id,
    selectionner_produits_par_boutique,
    inserer_produit,
    mettre_a_jour_stock_produit,
    selectionner_commercant_par_email,
    mettre_a_jour_commande_statut,
    inserer_notification,
    executer_requete_sql,
)
from utilitaires.qr import generer_qr_boutique
from utilitaires.notifications import envoyer_notification
import os


def creer_boutique(id_commercant, nom_boutique, description=None):
    """
    Crée une boutique pour un commerçant et génère un QR code.
    Retourne l'ID de la boutique créée.
    """
    # Insérer la boutique en BDD
    id_boutique = inserer_boutique(
        id_commercant=id_commercant,
        nom_boutique=nom_boutique,
        description=description,
    )

    # Générer le QR code pointant vers la page boutique
    url_boutique = f"/boutique/{id_boutique}"
    chemin_qr = generer_qr_boutique(url_boutique, id_boutique)

    # Mettre à jour la boutique avec le chemin du QR
    # Note: Ajouter une fonction pour mettre à jour le QR si nécessaire

    return id_boutique


def ajouter_produit(id_boutique, nom, description, prix, stock, categorie=None, image=None):
    """
    Ajoute un produit à une boutique.
    """
    return inserer_produit(
        id_boutique=id_boutique,
        nom=nom,
        description=description,
        prix=prix,
        stock=stock,
        image=image,
        categorie=categorie,
    )


def obtenir_statistiques_commercant(id_commercant):
    """
    Calcule les statistiques pour le tableau de bord commerçant.
    Retourne un dict avec ventes_jour, ventes_semaine, nb_commandes, nb_produits.
    """
    # Ventes du jour
    requete_ventes_jour = """
        SELECT COALESCE(SUM(c.total), 0) AS ventes_jour
        FROM commandes c
        JOIN boutiques b ON c.id_boutique = b.id
        WHERE b.id_commercant = %s AND DATE(c.date_commande) = CURDATE()
    """
    ventes_jour = executer_requete_sql(requete_ventes_jour, (id_commercant,), fetchone=True)["ventes_jour"]

    # Ventes de la semaine
    requete_ventes_semaine = """
        SELECT COALESCE(SUM(c.total), 0) AS ventes_semaine
        FROM commandes c
        JOIN boutiques b ON c.id_boutique = b.id
        WHERE b.id_commercant = %s AND YEARWEEK(c.date_commande) = YEARWEEK(CURDATE())
    """
    ventes_semaine = executer_requete_sql(requete_ventes_semaine, (id_commercant,), fetchone=True)["ventes_semaine"]

    # Nombre de commandes
    requete_nb_commandes = """
        SELECT COUNT(*) AS nb_commandes
        FROM commandes c
        JOIN boutiques b ON c.id_boutique = b.id
        WHERE b.id_commercant = %s
    """
    nb_commandes = executer_requete_sql(requete_nb_commandes, (id_commercant,), fetchone=True)["nb_commandes"]

    # Nombre de produits
    requete_nb_produits = """
        SELECT COUNT(*) AS nb_produits
        FROM produits p
        JOIN boutiques b ON p.id_boutique = b.id
        WHERE b.id_commercant = %s
    """
    nb_produits = executer_requete_sql(requete_nb_produits, (id_commercant,), fetchone=True)["nb_produits"]

    return {
        "ventes_jour": float(ventes_jour),
        "ventes_semaine": float(ventes_semaine),
        "nb_commandes": nb_commandes,
        "nb_produits": nb_produits,
    }


def obtenir_produits_commercant(id_commercant):
    """
    Récupère tous les produits des boutiques du commerçant.
    """
    requete = """
        SELECT p.*, b.nom_boutique
        FROM produits p
        JOIN boutiques b ON p.id_boutique = b.id
        WHERE b.id_commercant = %s
        ORDER BY p.id DESC
    """
    return executer_requete_sql(requete, (id_commercant,), fetchall=True)


def obtenir_commandes_commercant(id_commercant):
    """
    Récupère toutes les commandes des boutiques du commerçant.
    """
    requete = """
        SELECT c.*, cl.nom AS nom_client, b.nom_boutique
        FROM commandes c
        JOIN clients cl ON c.id_client = cl.id
        JOIN boutiques b ON c.id_boutique = b.id
        WHERE b.id_commercant = %s
        ORDER BY c.date_commande DESC
    """
    return executer_requete_sql(requete, (id_commercant,), fetchall=True)


def traiter_commande(id_commande, action):
    """
    Traite une commande (marquer payée/livrée) et notifie le client.
    """
    if action == "payer":
        statut = "paye"
    elif action == "livrer":
        statut = "livre"
    else:
        return False

    mettre_a_jour_commande_statut(id_commande, statut)

    # Récupérer id_client pour notification
    requete_client = "SELECT id_client FROM commandes WHERE id = %s"
    commande = executer_requete_sql(requete_client, (id_commande,), fetchone=True)
    if commande:
        id_client = commande["id_client"]
        message = f"Votre commande #{id_commande} a été marquée comme {statut}."
        inserer_notification(id_client, "commande", message)
        # Envoyer notification réelle si configuré
        envoyer_notification(id_client, "commande", message)

    return True


def obtenir_boutiques_commercant(id_commercant):
    """
    Récupère les boutiques du commerçant.
    """
    requete = "SELECT * FROM boutiques WHERE id_commercant = %s ORDER BY date_creation DESC"
    return executer_requete_sql(requete, (id_commercant,), fetchall=True)


def obtenir_statistiques_boutiques(id_commercant):
    """
    Récupère les statistiques détaillées des boutiques du commerçant.
    """
    requete = """
        SELECT
            b.id,
            b.nom_boutique,
            b.description,
            COUNT(DISTINCT p.id) AS nb_produits,
            COUNT(DISTINCT c.id) AS nb_commandes,
            COALESCE(SUM(c.total), 0) AS total_ventes
        FROM boutiques b
        LEFT JOIN produits p ON p.id_boutique = b.id
        LEFT JOIN commandes c ON c.id_boutique = b.id
        WHERE b.id_commercant = %s
        GROUP BY b.id, b.nom_boutique, b.description
        ORDER BY b.date_creation DESC
    """
    return executer_requete_sql(requete, (id_commercant,), fetchall=True)
