import os
import sys
import logging

from flask import Flask, jsonify, render_template

# Tentative d'import des extensions optionnelles
try:
    from flask_session import Session
except Exception:
    Session = None

try:
    from flask_compress import Compress
except Exception:
    Compress = None

# Tentative d'import des dépendances BDD
try:
    import mysql.connector
    from mysql.connector import errorcode
except Exception:
    mysql = None
    errorcode = None

# Chargement de la configuration (avec valeurs par défaut si config.py absent)
try:
    from config import SECRET_KEY, SESSION_TYPE, SESSION_FILE_DIR, DB_CONFIG
except Exception:
    # Valeurs par défaut pour un démarrage rapide en environnement de dev
    SECRET_KEY = os.environ.get("DJAAAPP_SECRET_KEY", "dev-changez-moi")
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), ".sessions")
    DB_CONFIG = {
        "host": os.environ.get("DJAAAPP_DB_HOST", "127.0.0.1"),
        "user": os.environ.get("DJAAAPP_DB_USER", "root"),
        "password": os.environ.get("DJAAAPP_DB_PASSWORD", ""),
        "database": os.environ.get("DJAAAPP_DB_NAME", "djaapp_db"),
        "port": int(os.environ.get("DJAAAPP_DB_PORT", "3306")),
        "autocommit": True,
    }

# Couleurs (peuvent être exposées aux templates plus tard)
COULEURS = {
    "primaire": "#FF7F00",  # orange africain
    "secondaire": "#228B22",  # vert confiance
    "accent": "#FFD700",  # jaune joie
    "fond": "#F5F5F5",  # clair lisible
}


# ---------------------------------------------
# Initialisation de l'application Flask
# ---------------------------------------------

def creer_application():
    """
    Créer et configurer l'application Flask avec sessions et compression.
    Retourne une instance de Flask prête à l'emploi.
    """
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Configuration de base
    app.config["SECRET_KEY"] = SECRET_KEY

    # Sessions côté serveur (filesystem pour simplicité)
    try:
        os.makedirs(SESSION_FILE_DIR, exist_ok=True)
    except Exception:
        pass
    app.config["SESSION_TYPE"] = SESSION_TYPE
    app.config["SESSION_FILE_DIR"] = SESSION_FILE_DIR

    if Session is not None:
        Session(app)
    else:
        app.logger.warning("Flask-Session non disponible (pip install Flask-Session)")

    # Compression GZIP
    if Compress is not None:
        Compress(app)
    else:
        app.logger.warning("Flask-Compress non disponible (pip install Flask-Compress)")

    # Exposer couleurs aux templates si besoin
    @app.context_processor
    def injecter_couleurs():
        return {"COULEURS": COULEURS}

    return app


app = creer_application()


# ---------------------------------------------
# Utilitaires BDD (procédural, nommage en français)
# ---------------------------------------------

def connecter_bdd_sans_base():
    """
    Se connecter au serveur MySQL sans sélectionner de base (utile pour créer la base).
    """
    if mysql is None:
        raise RuntimeError("mysql-connector-python n'est pas installé.")
    cfg = DB_CONFIG.copy()
    cfg.pop("database", None)
    return mysql.connector.connect(**cfg)


def connecter_bdd():
    """Se connecter à la base configurée (djaapp_db)."""
    if mysql is None:
        raise RuntimeError("mysql-connector-python n'est pas installé.")
    return mysql.connector.connect(**DB_CONFIG)


def executer_sql(connexion, requete, params=None):
    """
    Exécuter une requête SQL simple avec commit automatique.
    """
    curseur = connexion.cursor()
    try:
        curseur.execute(requete, params or ())
        connexion.commit()
    finally:
        curseur.close()


def initialiser_base_si_absente():
    """
    Créer la base djaapp_db si elle n'existe pas, avec encodage utf8mb4.
    """
    conn = connecter_bdd_sans_base()
    try:
        executer_sql(
            conn,
            "CREATE DATABASE IF NOT EXISTS djaapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
        )
    finally:
        conn.close()


def creer_tables_et_indexes():
    """
    Créer les tables, index et triggers selon le schéma défini.
    Idempotent autant que possible (IF NOT EXISTS, DROP TRIGGER IF EXISTS...).
    """
    initialiser_base_si_absente()
    conn = connecter_bdd()
    try:
        # Tables
        executer_sql(
            conn,
            """
            CREATE TABLE IF NOT EXISTS commercants (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                mot_de_passe VARCHAR(255) NOT NULL,
                telephone VARCHAR(20),
                adresse TEXT,
                date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_commercants_email (email),
                INDEX idx_commercants_telephone (telephone)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        )

        executer_sql(
            conn,
            """
            CREATE TABLE IF NOT EXISTS boutiques (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_commercant INT NOT NULL,
                nom_boutique VARCHAR(100) NOT NULL,
                description TEXT,
                qr_code VARCHAR(255),
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_boutiques_commercant (id_commercant),
                CONSTRAINT fk_boutiques_commercant FOREIGN KEY (id_commercant)
                    REFERENCES commercants(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        )

        executer_sql(
            conn,
            """
            CREATE TABLE IF NOT EXISTS produits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_boutique INT NOT NULL,
                nom VARCHAR(100) NOT NULL,
                description TEXT,
                prix DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                image VARCHAR(255),
                categorie VARCHAR(50),
                INDEX idx_produits_boutique (id_boutique),
                INDEX idx_produits_categorie (categorie),
                CONSTRAINT fk_produits_boutique FOREIGN KEY (id_boutique)
                    REFERENCES boutiques(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        )

        executer_sql(
            conn,
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                telephone VARCHAR(20) NOT NULL UNIQUE,
                adresse TEXT,
                date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_clients_email (email),
                INDEX idx_clients_telephone (telephone)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        )

        executer_sql(
            conn,
            """
            CREATE TABLE IF NOT EXISTS commandes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_client INT NOT NULL,
                id_boutique INT NOT NULL,
                date_commande DATETIME DEFAULT CURRENT_TIMESTAMP,
                statut VARCHAR(20) DEFAULT 'en_attente',
                total DECIMAL(10,2) NOT NULL DEFAULT 0,
                methode_paiement VARCHAR(50),
                INDEX idx_commandes_client (id_client),
                INDEX idx_commandes_boutique (id_boutique),
                INDEX idx_commandes_statut (statut),
                CONSTRAINT fk_commandes_client FOREIGN KEY (id_client)
                    REFERENCES clients(id) ON DELETE CASCADE,
                CONSTRAINT fk_commandes_boutique FOREIGN KEY (id_boutique)
                    REFERENCES boutiques(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        )

        executer_sql(
            conn,
            """
            CREATE TABLE IF NOT EXISTS lignes_commandes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_commande INT NOT NULL,
                id_produit INT NOT NULL,
                quantite INT NOT NULL,
                prix_unitaire DECIMAL(10,2) NOT NULL,
                INDEX idx_lignes_commande (id_commande),
                INDEX idx_lignes_produit (id_produit),
                CONSTRAINT fk_lignes_commande FOREIGN KEY (id_commande)
                    REFERENCES commandes(id) ON DELETE CASCADE,
                CONSTRAINT fk_lignes_produit FOREIGN KEY (id_produit)
                    REFERENCES produits(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        )

        executer_sql(
            conn,
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_destinataire INT NOT NULL,
                type VARCHAR(20),
                message TEXT,
                date_envoi DATETIME DEFAULT CURRENT_TIMESTAMP,
                lu BOOLEAN DEFAULT FALSE,
                INDEX idx_notifications_destinataire (id_destinataire),
                INDEX idx_notifications_type (type),
                INDEX idx_notifications_lu (lu)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        )

        # Triggers: mise à jour du stock après insertion de ligne commande
        executer_sql(conn, "DROP TRIGGER IF EXISTS trg_update_stock_apres_ligne;")
        executer_sql(
            conn,
            """
            CREATE TRIGGER trg_update_stock_apres_ligne
            AFTER INSERT ON lignes_commandes
            FOR EACH ROW
            BEGIN
                UPDATE produits
                SET stock = GREATEST(0, stock - NEW.quantite)
                WHERE id = NEW.id_produit;
            END;
            """,
        )

    finally:
        conn.close()


# ---------------------------------------------
# Routes minimales pour démarrer
# ---------------------------------------------

@app.get("/sante")
def verifier_sante():
    """Vérification santé de l'application et de la connexion BDD."""
    etat = {"application": "ok", "bdd": "inconnue"}
    if mysql is None:
        etat["bdd"] = "mysql-connector-python non installé"
        return jsonify(etat), 200
    try:
        conn = connecter_bdd()
        conn.close()
        etat["bdd"] = "connexion_ok"
        code = 200
    except Exception as e:
        etat["bdd"] = f"erreur_connexion: {e}"
        code = 500
    return jsonify(etat), code


@app.post("/init-bdd")
def initialiser_bdd():
    """
    Initialiser la base de données (création base, tables, index, triggers).
    À utiliser lors du premier lancement. Idempotent.
    """
    if mysql is None:
        return jsonify({"erreur": "mysql-connector-python non installé"}), 500
    try:
        creer_tables_et_indexes()
        return jsonify({"message": "Base de données initialisée"}), 201
    except Exception as e:
        app.logger.exception("Erreur init BDD")
        return jsonify({"erreur": str(e)}), 500


# ---------------------------------------------
# Chargement des routes applicatives (si disponibles)
# ---------------------------------------------
try:
    # On s'attend à une fonction enregistrer_routes(app) dans routes.py
    from routes import enregistrer_routes  # type: ignore
    enregistrer_routes(app)
except Exception as e:
    logging.warning("Routes non chargées: %s", e)


# ---------------------------------------------
# Lancement de l'application
# ---------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(port=port, debug=True)
