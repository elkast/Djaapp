"""
Routes principales de Djaapp - Architecture simple avec séparation Commerçant/Client
"""

from flask import request, jsonify, render_template, redirect, url_for, flash, session
import requests
from controllers.auth import (
    inscrire_commercant,
    connecter_commercant,
    inscrire_client,
    connecter_client,
    guard_commercant,
    guard_client,
    deconnecter,
)
from controllers.commercant import (
    obtenir_statistiques_commercant,
    obtenir_produits_commercant,
    obtenir_commandes_commercant,
    creer_boutique,
    ajouter_produit,
    traiter_commande,
    obtenir_boutiques_commercant,
    obtenir_statistiques_boutiques,
)
from controllers.client import (
    rechercher_boutiques,
    obtenir_boutique,
    ajouter_au_panier,
    obtenir_panier,
    passer_commande,
    traiter_paiement,
    obtenir_commandes_client,
    obtenir_details_commande,
)
from utilitaires.qr import generer_qr_boutique
from utilitaires.integrations import partager_boutique_whatsapp
from models.bdd import (
    executer_requete_sql,
    selectionner_commercant_par_id,
)


def enregistrer_routes(app):
    """Enregistrer toutes les routes de l'application."""

    # ==========================================
    # ROUTES PUBLIQUES
    # ==========================================

    @app.get("/")
    def page_accueil():
        """Page d'accueil principale."""
        # Rediriger vers dashboard si déjà connecté
        if session.get('role') == 'commercant':
            return redirect(url_for('dashboard_commercant'))
        elif session.get('role') == 'client':
            return redirect(url_for('dashboard_client'))

        boutiques = rechercher_boutiques()[:6]  # 6 populaires
        return render_template("index.html", boutiques=boutiques)

    # ==========================================
    # ROUTES COMMERCANTS
    # ==========================================

    @app.get("/commercant/inscription")
    def inscription_commercant():
        """Formulaire d'inscription commerçant."""
        return render_template("commercant/inscription.html")

    @app.post("/commercant/inscription")
    def traiter_inscription_commercant():
        """Traiter l'inscription commerçant."""
        donnees = request.form
        nom = (donnees.get("nom") or "").strip()
        email = (donnees.get("email") or "").strip().lower()
        telephone = (donnees.get("telephone") or "").strip()
        adresse = (donnees.get("adresse") or "").strip()
        mot_de_passe = donnees.get("mot_de_passe") or ""

        if inscrire_commercant(nom, email, mot_de_passe, telephone, adresse):
            return redirect(url_for("dashboard_commercant"))
        return redirect(url_for("inscription_commercant"))

    @app.get("/commercant/login")
    def connexion_commercant():
        """Formulaire de connexion commerçant."""
        return render_template("commercant/connexion.html")

    @app.post("/commercant/login")
    def traiter_connexion_commercant():
        """Traiter la connexion commerçant."""
        email = request.form.get("email", "").strip().lower()
        mot_de_passe = request.form.get("mot_de_passe", "")
        if connecter_commercant(email, mot_de_passe):
            return redirect(url_for("dashboard_commercant"))
        return redirect(url_for("connexion_commercant"))

    @app.get("/commercant/dashboard")
    def dashboard_commercant():
        """Tableau de bord commerçant."""
        guard = guard_commercant()
        if guard:
            return guard
        id_commercant = session["id_commercant"]
        stats = obtenir_statistiques_commercant(id_commercant)
        produits = obtenir_produits_commercant(id_commercant)[:10]  # 10 derniers
        return render_template("commercant/dashboard.html", stats=stats, produits=produits)

    @app.get("/commercant/boutique/creer")
    def creer_boutique_page():
        """Formulaire création boutique."""
        guard = guard_commercant()
        if guard:
            return guard
        return render_template("commercant/creer-boutique.html")

    @app.post("/commercant/boutique/creer")
    def traiter_creer_boutique():
        """Traiter la création de boutique."""
        guard = guard_commercant()
        if guard:
            return guard

        donnees = request.form
        nom_boutique = (donnees.get("nom_boutique") or "").strip()
        description = (donnees.get("description") or "").strip()

        erreurs = []
        if not nom_boutique:
            erreurs.append("Le nom de la boutique est obligatoire.")

        if erreurs:
            flash(" ".join(erreurs), "error")
            return redirect(url_for("creer_boutique_page"))

        id_commercant = session["id_commercant"]
        try:
            id_boutique = creer_boutique(id_commercant, nom_boutique, description)
            url_boutique = url_for("voir_boutique", id_boutique=id_boutique, _external=True)
            qr_path = generer_qr_boutique(url_boutique, id_boutique)
            lien_boutique = url_boutique
            flash("Boutique créée avec succès.", "success")
            return render_template("commercant/creer-boutique.html", qr_path=qr_path, lien_boutique=lien_boutique)
        except Exception as e:
            flash(f"Erreur: {str(e)}", "error")
            return redirect(url_for("creer_boutique_page"))

    @app.get("/commercant/produits")
    def gerer_produits():
        """Gestion des produits."""
        guard = guard_commercant()
        if guard:
            return guard
        id_commercant = session["id_commercant"]
        produits = obtenir_produits_commercant(id_commercant)
        boutiques = obtenir_boutiques_commercant(id_commercant)
        return render_template("commercant/produits.html", produits=produits, boutiques=boutiques)

    @app.post("/commercant/produit/ajouter")
    def ajouter_produit_route():
        """Ajouter un produit."""
        guard = guard_commercant()
        if guard:
            return guard

        donnees = request.form
        id_boutique = int(donnees.get("id_boutique"))
        nom = (donnees.get("nom") or "").strip()
        description = (donnees.get("description") or "").strip()
        prix = float(donnees.get("prix"))
        stock = int(donnees.get("stock"))
        categorie = (donnees.get("categorie") or "").strip()

        # Gestion de l'image
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                # Sauvegarder l'image
                import os
                from werkzeug.utils import secure_filename

                upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'produits')
                os.makedirs(upload_folder, exist_ok=True)

                filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                image_path = f"uploads/produits/{filename}"  # Chemin relatif pour la BDD

        try:
            ajouter_produit(id_boutique, nom, description, prix, stock, categorie, image_path)
            flash("Produit ajouté.", "success")
        except Exception as e:
            flash(f"Erreur: {str(e)}", "error")
        return redirect(url_for("gerer_produits"))

    @app.post("/commercant/produit/<int:id_produit>/modifier")
    def modifier_produit_route(id_produit):
        """Modifier un produit."""
        guard = guard_commercant()
        if guard:
            return guard

        donnees = request.form
        nom = (donnees.get("nom") or "").strip()
        description = (donnees.get("description") or "").strip()
        prix = float(donnees.get("prix"))
        stock = int(donnees.get("stock"))
        categorie = (donnees.get("categorie") or "").strip()

        # Gestion de l'image
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                import os
                from werkzeug.utils import secure_filename

                upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'produits')
                os.makedirs(upload_folder, exist_ok=True)

                filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                image_path = f"uploads/produits/{filename}"

        try:
            # Mettre à jour le produit (fonction à implémenter)
            from models.bdd import mettre_a_jour_produit
            mettre_a_jour_produit(id_produit, nom=nom, description=description, prix=prix, stock=stock, categorie=categorie, image=image_path)
            flash("Produit modifié.", "success")
        except Exception as e:
            flash(f"Erreur: {str(e)}", "error")
        return redirect(url_for("gerer_produits"))

    @app.post("/commercant/produit/<int:id_produit>/supprimer")
    def supprimer_produit_route(id_produit):
        """Supprimer un produit."""
        guard = guard_commercant()
        if guard:
            return guard

        try:
            from models.bdd import supprimer_produit
            supprimer_produit(id_produit)
            flash("Produit supprimé.", "success")
        except Exception as e:
            flash(f"Erreur: {str(e)}", "error")
        return redirect(url_for("gerer_produits"))

    @app.get("/commercant/commandes")
    def gerer_commandes():
        """Gestion des commandes."""
        guard = guard_commercant()
        if guard:
            return guard
        id_commercant = session["id_commercant"]
        commandes = obtenir_commandes_commercant(id_commercant)
        return render_template("commercant/commandes.html", commandes=commandes)

    @app.post("/commercant/commande/<int:id_commande>/traiter")
    def traiter_commande_route(id_commande):
        """Traiter une commande."""
        guard = guard_commercant()
        if guard:
            return guard
        action = request.form.get("action")
        if traiter_commande(id_commande, action):
            flash("Commande traitée.", "success")
        else:
            flash("Erreur traitement.", "error")
        return redirect(url_for("gerer_commandes"))

    @app.get("/commercant/partage/<int:id_boutique>")
    def partager_boutique(id_boutique):
        """Partager boutique via WhatsApp."""
        guard = guard_commercant()
        if guard:
            return guard
        url_boutique = url_for("voir_boutique", id_boutique=id_boutique, _external=True)
        lien_whatsapp = partager_boutique_whatsapp(url_boutique)
        return redirect(lien_whatsapp)

    # ==========================================
    # ROUTES CLIENTS
    # ==========================================

    @app.get("/client/inscription")
    def inscription_client():
        """Formulaire d'inscription client."""
        return render_template("client/inscription.html")

    @app.post("/client/inscription")
    def traiter_inscription_client():
        """Traiter l'inscription client."""
        donnees = request.form
        nom = (donnees.get("nom") or "").strip()
        telephone = (donnees.get("telephone") or "").strip()
        email = (donnees.get("email") or "").strip().lower()
        adresse = (donnees.get("adresse") or "").strip()
        mot_de_passe = donnees.get("mot_de_passe") or None

        if inscrire_client(nom, telephone, email, adresse, mot_de_passe):
            return redirect(url_for("dashboard_client"))
        return redirect(url_for("inscription_client"))

    @app.get("/client/login")
    def connexion_client():
        """Formulaire de connexion client."""
        return render_template("client/connexion.html")

    @app.post("/client/login")
    def traiter_connexion_client():
        """Traiter la connexion client."""
        telephone = request.form.get("telephone", "").strip()
        mot_de_passe = request.form.get("mot_de_passe")
        if connecter_client(telephone, mot_de_passe):
            return redirect(url_for("dashboard_client"))
        return redirect(url_for("connexion_client"))

    @app.get("/client/dashboard")
    def dashboard_client():
        """Tableau de bord client."""
        guard = guard_client()
        if guard:
            return guard
        boutiques = rechercher_boutiques()[:12]  # 12 populaires
        return render_template("client/dashboard.html", boutiques=boutiques)

    @app.get("/client/profil")
    def profil_client():
        """Profil client."""
        guard = guard_client()
        if guard:
            return guard
        return render_template("client/profil.html")

    @app.get("/client/panier")
    def panier_client():
        """Panier d'achat."""
        guard = guard_client()
        if guard:
            return guard
        panier = obtenir_panier(session)
        return render_template("client/panier.html", panier=panier)

    @app.post("/client/panier/ajouter/<int:id_produit>")
    def ajouter_panier(id_produit):
        """Ajouter au panier."""
        quantite = int(request.form.get("quantite", 1))
        ajouter_au_panier(session, id_produit, quantite)
        flash("Ajouté au panier.", "success")
        return redirect(request.referrer or url_for("dashboard_client"))

    @app.post("/client/panier/modifier")
    def modifier_panier():
        """Modifier quantité dans le panier."""
        id_produit = int(request.form.get("id_produit"))
        quantite = int(request.form.get("quantite", 1))
        if quantite <= 0:
            # Supprimer du panier
            panier = session.get("panier", {})
            if str(id_produit) in panier:
                del panier[str(id_produit)]
                session["panier"] = panier
        else:
            ajouter_au_panier(session, id_produit, quantite - session.get("panier", {}).get(str(id_produit), 0))
        return "", 200

    @app.post("/client/panier/supprimer")
    def supprimer_panier():
        """Supprimer produit du panier."""
        id_produit = int(request.form.get("id_produit"))
        panier = session.get("panier", {})
        if str(id_produit) in panier:
            del panier[str(id_produit)]
            session["panier"] = panier
        return "", 200

    @app.post("/client/panier/vider")
    def vider_panier():
        """Vider complètement le panier."""
        session["panier"] = {}
        return "", 200

    @app.get("/client/commandes")
    def commandes_client():
        """Historique des commandes."""
        guard = guard_client()
        if guard:
            return guard
        id_client = session["id_client"]
        commandes = obtenir_commandes_client(id_client)
        return render_template("client/commandes.html", commandes=commandes)

    @app.get("/client/commande/<int:id_commande>")
    def details_commande(id_commande):
        """Détails d'une commande."""
        guard = guard_client()
        if guard:
            return guard
        id_client = session["id_client"]
        details = obtenir_details_commande(id_commande, id_client)
        return render_template("client/commandes.html", details=details, id_commande=id_commande)

    # ==========================================
    # ROUTES BOUTIQUES (PUBLIQUES)
    # ==========================================

    @app.get("/boutique/<int:id_boutique>")
    def voir_boutique(id_boutique):
        """Voir une boutique publique."""
        boutique = obtenir_boutique(id_boutique)
        if not boutique:
            flash("Boutique introuvable.", "error")
            return redirect(url_for("page_accueil"))
        return render_template("boutique.html", boutique=boutique)

    @app.get("/boutiques/recherche")
    def rechercher_boutiques_route():
        """Recherche boutiques."""
        query = request.args.get("q", "").strip()
        boutiques = rechercher_boutiques(query)
        return render_template("client/dashboard.html", boutiques=boutiques, query=query)

    # ==========================================
    # ROUTES PAIEMENT
    # ==========================================

    @app.get("/paiement")
    def page_paiement():
        """Page de paiement."""
        guard = guard_client()
        if guard:
            return guard
        panier = obtenir_panier(session)
        if not panier["items"]:
            flash("Panier vide.", "error")
            return redirect(url_for("panier_client"))
        etape = int(request.args.get("etape", 1))
        return render_template("client/paiement.html", panier=panier, etape=etape)

    @app.post("/client/paiement/continuer")
    def continuer_paiement():
        """Continuer vers l'étape 2."""
        guard = guard_client()
        if guard:
            return guard
        return redirect(url_for("page_paiement", etape=2))

    @app.post("/client/paiement/mobile-money")
    def traiter_paiement_mobile_money():
        """Traiter paiement Mobile Money."""
        guard = guard_client()
        if guard:
            return guard

        donnees = request.form
        operateur = donnees.get("operateur")
        telephone = donnees.get("telephone")

        panier = obtenir_panier(session)
        if not panier["items"]:
            flash("Panier vide.", "error")
            return redirect(url_for("panier_client"))

        id_client = session["id_client"]
        # Déterminer boutique depuis premier produit du panier
        premier_produit = panier["items"][0]
        requete_boutique = "SELECT id_boutique FROM produits WHERE id = %s"
        boutique = executer_requete_sql(requete_boutique, (premier_produit["id"],), fetchone=True)
        id_boutique = boutique["id_boutique"] if boutique else 1

        id_commande = passer_commande(session, id_client, id_boutique, "mobile_money")
        if not id_commande:
            flash("Erreur commande.", "error")
            return redirect(url_for("page_paiement", etape=2))

        if traiter_paiement(id_commande, "mobile_money", {"numero": telephone, "montant": panier["total"]}):
            flash("Paiement réussi.", "success")
            return redirect(url_for("page_paiement", etape=3))
        else:
            flash("Erreur paiement.", "error")
            return redirect(url_for("page_paiement", etape=2))

    @app.post("/client/paiement/carte")
    def traiter_paiement_carte():
        """Traiter paiement par carte."""
        guard = guard_client()
        if guard:
            return guard

        donnees = request.form
        nom_carte = donnees.get("nom_carte")
        numero_carte = donnees.get("numero_carte")
        expiration = donnees.get("expiration")
        cvc = donnees.get("cvc")

        panier = obtenir_panier(session)
        if not panier["items"]:
            flash("Panier vide.", "error")
            return redirect(url_for("panier_client"))

        id_client = session["id_client"]
        # Déterminer boutique depuis premier produit du panier
        premier_produit = panier["items"][0]
        requete_boutique = "SELECT id_boutique FROM produits WHERE id = %s"
        boutique = executer_requete_sql(requete_boutique, (premier_produit["id"],), fetchone=True)
        id_boutique = boutique["id_boutique"] if boutique else 1

        id_commande = passer_commande(session, id_client, id_boutique, "carte")
        if not id_commande:
            flash("Erreur commande.", "error")
            return redirect(url_for("page_paiement", etape=2))

        if traiter_paiement(id_commande, "carte", {"nom_carte": nom_carte, "numero_carte": numero_carte, "expiration": expiration, "cvc": cvc}):
            flash("Paiement réussi.", "success")
            return redirect(url_for("page_paiement", etape=3))
        else:
            flash("Erreur paiement.", "error")
            return redirect(url_for("page_paiement", etape=2))

    @app.post("/paiement/traiter")
    def traiter_paiement_route():
        """Traiter le paiement."""
        guard = guard_client()
        if guard:
            return guard

        methode = request.form.get("methode")
        details = request.form

        # Simuler commande depuis panier (premier item pour boutique)
        panier = obtenir_panier(session)
        if not panier["items"]:
            flash("Panier vide.", "error")
            return redirect(url_for("panier_client"))

        id_client = session["id_client"]
        # Déterminer boutique depuis premier produit du panier
        premier_produit = panier["items"][0]
        requete_boutique = "SELECT id_boutique FROM produits WHERE id = %s"
        boutique = executer_requete_sql(requete_boutique, (premier_produit["id"],), fetchone=True)
        id_boutique = boutique["id_boutique"] if boutique else 1

        id_commande = passer_commande(session, id_client, id_boutique, methode)
        if not id_commande:
            flash("Erreur commande.", "error")
            return redirect(url_for("panier_client"))

        if traiter_paiement(id_commande, methode, details):
            flash("Paiement réussi.", "success")
            return redirect(url_for("commandes_client"))
        else:
            flash("Erreur paiement.", "error")
            return redirect(url_for("page_paiement"))

    # ==========================================
    # ROUTES GÉNÉRALES
    # ==========================================

    @app.get("/deconnexion")
    def deconnexion():
        """Déconnexion."""
        deconnecter()
        return redirect(url_for("page_accueil"))

    # ==========================================
    # REDIRECTIONS POUR COMPATIBILITE
    # ==========================================

    @app.route("/inscription-commercant", methods=["GET", "POST"])
    def redirect_inscription_commercant():
        if request.method == "POST":
            return redirect(url_for("traiter_inscription_commercant"))
        return redirect(url_for("inscription_commercant"))

    @app.get("/commercant/profil")
    def profil_commercant():
        """Profil commerçant."""
        guard = guard_commercant()
        if guard:
            return guard
        id_commercant = session["id_commercant"]
        stats = obtenir_statistiques_commercant(id_commercant)
        boutiques = obtenir_statistiques_boutiques(id_commercant)
        return render_template("commercant/profil_commercant.html", stats=stats, boutiques=boutiques)

    @app.get("/commercant/profil/modifier")
    def modifier_profil_commercant():
        """Modifier profil commerçant."""
        guard = guard_commercant()
        if guard:
            return guard
        id_commercant = session["id_commercant"]
        commercant = selectionner_commercant_par_id(id_commercant)
        boutiques = obtenir_boutiques_commercant(id_commercant)
        return render_template("commercant/modifier_profil_commercant.html", commercant=commercant, boutiques=boutiques)

    @app.post("/commercant/profil/modifier")
    def traiter_modifier_profil_commercant():
        """Traiter la modification du profil commerçant."""
        guard = guard_commercant()
        if guard:
            return guard

        id_commercant = session["id_commercant"]
        donnees = request.form

        # Récupération des données
        nom = (donnees.get("nom") or "").strip()
        telephone = (donnees.get("telephone") or "").strip()
        adresse = (donnees.get("adresse") or "").strip()
        latitude = donnees.get("latitude")
        longitude = donnees.get("longitude")

        # Gestion de l'image du commerçant
        image_commercant_path = None
        if 'image_commercant' in request.files:
            image = request.files['image_commercant']
            if image and image.filename:
                import os
                from werkzeug.utils import secure_filename

                upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'commercants')
                os.makedirs(upload_folder, exist_ok=True)

                filename = secure_filename(image.filename)
                image_commercant_path = os.path.join(upload_folder, filename)
                image.save(image_commercant_path)
                image_commercant_path = f"uploads/commercants/{filename}"

        # Gestion de l'image de la boutique
        image_boutique_path = None
        if 'image_boutique' in request.files:
            image = request.files['image_boutique']
            if image and image.filename:
                import os
                from werkzeug.utils import secure_filename

                upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'boutiques')
                os.makedirs(upload_folder, exist_ok=True)

                filename = secure_filename(image.filename)
                image_boutique_path = os.path.join(upload_folder, filename)
                image.save(image_boutique_path)
                image_boutique_path = f"uploads/boutiques/{filename}"

        # Mise à jour du commerçant
        try:
            from models.bdd import mettre_a_jour_commercant
            mettre_a_jour_commercant(
                id_commercant=id_commercant,
                nom=nom if nom else None,
                telephone=telephone if telephone else None,
                adresse=adresse if adresse else None,
                image=image_commercant_path,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
            )

            # Mise à jour de la boutique si image fournie
            if image_boutique_path:
                boutiques = obtenir_boutiques_commercant(id_commercant)
                if boutiques:
                    from models.bdd import mettre_a_jour_boutique
                    mettre_a_jour_boutique(
                        id_boutique=boutiques[0]['id'],
                        image=image_boutique_path
                    )

            # Mise à jour de la session avec les nouvelles valeurs
            if nom:
                session['nom'] = nom
            if telephone:
                session['telephone'] = telephone
            if adresse:
                session['adresse'] = adresse
            if image_commercant_path:
                session['image'] = image_commercant_path
            if latitude:
                session['latitude'] = float(latitude)
            if longitude:
                session['longitude'] = float(longitude)

            flash("Profil mis à jour avec succès.", "success")
        except Exception as e:
            flash(f"Erreur lors de la mise à jour: {str(e)}", "error")

        return redirect(url_for("profil_commercant"))

    @app.get("/dashboard-commercant")
    def redirect_dashboard_commercant():
        return redirect(url_for("dashboard_commercant"))

    @app.get("/commandes-commercant")
    def redirect_commandes_commercant():
        return redirect(url_for("gerer_commandes"))

    @app.get("/inscription-client")
    def redirect_inscription_client():
        return redirect(url_for("inscription_client"))

    @app.get("/dashboard-client")
    def redirect_dashboard_client():
        return redirect(url_for("dashboard_client"))

    @app.get("/profil-client")
    def redirect_profil_client():
        return redirect(url_for("profil_client"))

    @app.get("/login")
    def login():
        """Page de connexion générale."""
        return render_template("login.html")
