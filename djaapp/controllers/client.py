"""
Contrôleur pour la logique métier des clients.
Fonctions procédurales en français pour gérer paniers, commandes, paiements.
"""

from models.bdd import (
    inserer_client,
    selectionner_client_par_telephone,
    inserer_commande,
    inserer_ligne_commande,
    selectionner_boutiques_populaires,
    selectionner_boutique_par_id,
    selectionner_produits_par_boutique,
    executer_requete_sql,
)
from utilitaires.integrations import initier_paiement_mobile_money
import uuid


def inscrire_client(nom, telephone, email=None, adresse=None):
    """
    Inscrit un nouveau client.
    """
    return inserer_client(
        nom=nom,
        email=email,
        telephone=telephone,
        adresse=adresse,
    )


def rechercher_boutiques(query=None):
    """
    Recherche des boutiques par nom ou populaires si pas de query.
    """
    if query:
        requete = """
            SELECT b.*, COUNT(c.id) AS nb_commandes
            FROM boutiques b LEFT JOIN commandes c ON c.id_boutique = b.id
            WHERE b.nom_boutique LIKE %s
            GROUP BY b.id ORDER BY nb_commandes DESC LIMIT 20
        """
        return executer_requete_sql(requete, (f"%{query}%",), fetchall=True)
    return selectionner_boutiques_populaires(20)


def obtenir_boutique(id_boutique):
    """
    Récupère les détails d'une boutique et ses produits.
    """
    boutique = selectionner_boutique_par_id(id_boutique)
    if boutique:
        produits = selectionner_produits_par_boutique(id_boutique)
        boutique["produits"] = produits
    return boutique


def ajouter_au_panier(session, id_produit, quantite):
    """
    Ajoute un produit au panier en session.
    """
    panier = session.get("panier", {})
    panier[str(id_produit)] = panier.get(str(id_produit), 0) + quantite
    session["panier"] = panier


def obtenir_panier(session):
    """
    Récupère le contenu du panier avec détails produits depuis BDD.
    """
    panier = session.get("panier", {})
    if not panier:
        return {"items": [], "total": 0.0}

    # Récupérer détails produits avec nom de boutique
    ids_produits = list(panier.keys())
    placeholders = ",".join(["%s"] * len(ids_produits))
    requete = f"""
        SELECT p.id, p.nom, CAST(p.prix AS DECIMAL(10,2)) as prix, b.nom_boutique
        FROM produits p
        JOIN boutiques b ON p.id_boutique = b.id
        WHERE p.id IN ({placeholders})
    """
    produits = executer_requete_sql(requete, ids_produits, fetchall=True)

    # Mapper par ID
    produits_dict = {str(p["id"]): p for p in produits}

    items = []
    total = 0.0
    for id_prod, qty in panier.items():
        prod = produits_dict.get(id_prod)
        if prod:
            prix_float = float(prod["prix"])
            sous_total = prix_float * float(qty)
            items.append({
                "id": int(id_prod),
                "nom": prod["nom"],
                "prix": prix_float,
                "quantite": qty,
                "sous_total": sous_total,
                "nom_boutique": prod["nom_boutique"],
            })
            total = total + sous_total
    return {"items": items, "total": float(total)}


def passer_commande(session, id_client, id_boutique, methode_paiement):
    """
    Crée une commande depuis le panier.
    """
    panier = obtenir_panier(session)
    if not panier["items"]:
        return None

    total = panier["total"]

    # Créer la commande
    id_commande = inserer_commande(
        id_client=id_client,
        id_boutique=id_boutique,
        total=total,
        methode_paiement=methode_paiement,
    )

    # Ajouter les lignes
    for item in panier["items"]:
        inserer_ligne_commande(
            id_commande=id_commande,
            id_produit=item["id"],
            quantite=item["quantite"],
            prix_unitaire=item["prix"],
        )

    # Vider le panier
    session["panier"] = {}

    return id_commande


def traiter_paiement(id_commande, methode, details_paiement):
    """
    Traite le paiement selon la méthode choisie.
    """
    if methode == "mobile_money":
        numero = details_paiement.get("numero")
        montant = details_paiement.get("montant")
        return initier_paiement_mobile_money(numero, montant)
    elif methode == "carte":
        # Intégrer Stripe (placeholder)
        return True  # Simuler succès
    return False


def obtenir_commandes_client(id_client):
    """
    Récupère l'historique des commandes du client.
    """
    requete = """
        SELECT c.*, b.nom_boutique
        FROM commandes c
        JOIN boutiques b ON c.id_boutique = b.id
        WHERE c.id_client = %s
        ORDER BY c.date_commande DESC
    """
    return executer_requete_sql(requete, (id_client,), fetchall=True)


def obtenir_details_commande(id_commande, id_client):
    """
    Récupère les détails d'une commande (lignes).
    """
    requete = """
        SELECT lc.*, p.nom AS nom_produit
        FROM lignes_commandes lc
        JOIN produits p ON lc.id_produit = p.id
        JOIN commandes c ON lc.id_commande = c.id
        WHERE lc.id_commande = %s AND c.id_client = %s
    """
    return executer_requete_sql(requete, (id_commande, id_client), fetchall=True)
