# Djaapp - Plateforme E-commerce Mobile-First pour l'Afrique

## Vue d'ensemble

Djaapp est une plateforme e-commerce innovante conçue spécifiquement pour les petits commerçants en Côte d'Ivoire et en Afrique de l'Ouest. Elle transforme les boutiques traditionnelles en boutiques en ligne modernes, accessibles via QR codes et optimisées pour les appareils mobiles. La plateforme met l'accent sur la simplicité, la rapidité et l'intégration des méthodes de paiement locales comme Mobile Money.

### Mission
Révolutionner le commerce de détail en Afrique en rendant le e-commerce accessible aux petits commerçants, sans nécessiter de compétences techniques avancées.

### Valeurs
- **Mobile-First** : Optimisé pour les connexions lentes et les smartphones africains
- **Local** : Intégration des paiements Mobile Money (Orange Money, MTN MoMo)
- **Simple** : Interface intuitive pour commerçants et clients
- **Rapide** : Démarrage en quelques minutes

## Architecture et Technologies

### Backend
- **Framework** : Flask 2.3.3 (Python)
- **Base de données** : MySQL 8.3.0 avec mysql-connector-python
- **Sessions** : Stockage côté serveur (filesystem) avec Flask-Session
- **Compression** : GZIP avec Flask-Compress
- **Authentification** : bcrypt pour le hashage des mots de passe
- **QR Codes** : qrcode[pil] avec Pillow pour génération
- **Paiements** : Intégration Stripe pour cartes + simulation Mobile Money
- **Notifications** : Twilio pour SMS, smtplib pour emails
- **WhatsApp** : Partage via liens wa.me

### Frontend
- **Templates** : Jinja2 avec Bootstrap 5
- **CSS** : Variables CSS dynamiques pour thème personnalisable
- **JavaScript** : Vanilla JS avec Font Awesome 6
- **Responsive** : Design mobile-first

### Couleurs Thématiques
- Primaire : Orange africain (#FF7F00)
- Secondaire : Vert confiance (#228B22)
- Accent : Jaune joie (#FFD700)
- Fond : Clair lisible (#F5F5F5)

## Fonctionnalités Clés

### Pour les Commerçants
1. **Inscription/Connexion**
   - Formulaire simple avec validation email/téléphone
   - Sessions persistantes avec données utilisateur

2. **Gestion des Boutiques**
   - Création de boutiques avec nom et description
   - Génération automatique de QR codes
   - Partage WhatsApp intégré

3. **Gestion des Produits**
   - Ajout/modification/suppression de produits
   - Upload d'images
   - Gestion du stock en temps réel
   - Catégorisation des produits

4. **Tableau de Bord**
   - Statistiques : ventes jour/semaine, nombre de commandes/produits
   - Vue d'ensemble des boutiques et performances

5. **Gestion des Commandes**
   - Liste des commandes par boutique
   - Statuts : en_attente, paye, livre
   - Notifications automatiques aux clients

6. **Profil et Paramètres**
   - Mise à jour des informations personnelles
   - Géolocalisation (latitude/longitude)
   - Upload de photos de profil et boutique

### Pour les Clients
1. **Inscription/Connexion**
   - Comptes temporaires (téléphone seulement) ou persistants
   - Validation Côte d'Ivoire (+225)

2. **Exploration des Boutiques**
   - Recherche par nom
   - Boutiques populaires
   - Vue détaillée avec produits

3. **Panier d'Achat**
   - Ajout/suppression/modification de quantités
   - Calcul automatique des totaux
   - Persistance en session

4. **Paiement**
   - Mobile Money (Orange/MTN) - simulé en démo
   - Cartes bancaires via Stripe
   - Processus en 3 étapes : panier → détails → confirmation

5. **Historique des Commandes**
   - Suivi des achats passés
   - Détails des commandes

### Fonctionnalités Partagées
- **QR Codes** : Accès direct aux boutiques
- **Notifications** : SMS/Email/WhatsApp pour mises à jour
- **Multilingue** : Interface en français
- **Sécurité** : Guards pour accès rôle-based

## Structure du Projet

```
djaapp/
├── app.py                 # Application Flask principale
├── config.py              # Configuration (DB, sessions, etc.)
├── routes.py              # Définition de toutes les routes
├── requirements.txt       # Dépendances Python
├── TODO.md                # Liste des tâches en cours
├── controllers/           # Logique métier
│   ├── auth.py           # Authentification
│   ├── commercant.py     # Fonctions commerçants
│   ├── client.py         # Fonctions clients
│   └── admin.py          # Administration (basique)
├── models/
│   └── bdd.py            # Fonctions CRUD MySQL
├── utilitaires/           # Utilitaires externes
│   ├── qr.py             # Génération QR codes
│   ├── notifications.py  # SMS/Email
│   └── integrations.py   # WhatsApp, Mobile Money
├── templates/             # Templates HTML
│   ├── base.html         # Template de base
│   ├── index.html        # Page d'accueil
│   ├── boutique.html     # Vue boutique publique
│   ├── client/           # Templates clients
│   └── commercant/       # Templates commerçants
├── static/                # Assets statiques
│   ├── css/
│   │   └── style.css     # Styles custom
│   ├── js/
│   │   └── script.js     # JavaScript
│   ├── uploads/          # Images uploadées
│   │   ├── boutiques/
│   │   ├── commercants/
│   │   └── produits/
│   └── qr/               # QR codes générés
└── __pycache__/          # Cache Python (ignoré)
```

## Base de Données

### Schéma MySQL (utf8mb4)

#### Tables Principales
- **commercants** : id, nom, email, mot_de_passe, telephone, adresse, date_inscription
- **boutiques** : id, id_commercant, nom_boutique, description, qr_code, date_creation
- **produits** : id, id_boutique, nom, description, prix, stock, image, categorie
- **clients** : id, nom, email, telephone, adresse, date_inscription
- **commandes** : id, id_client, id_boutique, date_commande, statut, total, methode_paiement
- **lignes_commandes** : id, id_commande, id_produit, quantite, prix_unitaire
- **notifications** : id, id_destinataire, type, message, date_envoi, lu

#### Index et Contraintes
- Index sur emails, telephones, boutiques, produits
- Clés étrangères avec CASCADE pour intégrité
- Triggers pour mise à jour automatique du stock

#### Encodage
- Base et tables en utf8mb4 pour support Unicode complet
- Collate utf8mb4_general_ci

## Installation et Configuration

### Prérequis
- Python 3.8+
- MySQL 8.0+
- pip pour gestion des dépendances

### Étapes d'Installation

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd djaapp
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration MySQL**
   - Créer une base de données `djaapp_db`
   - Modifier `config.py` ou variables d'environnement :
     ```bash
     export DJAAAPP_DB_HOST=localhost
     export DJAAAPP_DB_USER=root
     export DJAAAPP_DB_PASSWORD=votre_mot_de_passe
     export DJAAAPP_DB_NAME=djaapp_db
     ```

4. **Configuration optionnelle**
   - Clé secrète : `DJAAAPP_SECRET_KEY`
   - Twilio : `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
   - SMTP : `SMTP_EMAIL`, `SMTP_PASSWORD`

5. **Initialisation**
   ```bash
   python app.py
   # Accéder à /init-bdd pour créer les tables
   ```

6. **Lancement**
   ```bash
   python app.py
   # Serveur sur http://localhost:5000
   ```

## Utilisation

### Démarrage Rapide
1. Lancer l'application
2. Accéder à `/init-bdd` pour initialiser la BDD
3. Créer un compte commerçant
4. Ajouter une boutique et des produits
5. Scanner le QR code ou partager le lien

### Routes API Principales

#### Santé et Utilitaires
- `GET /sante` : Vérification santé application/BDD
- `POST /init-bdd` : Initialisation base de données

#### Commerçants
- `GET/POST /commercant/inscription` : Inscription
- `GET/POST /commercant/login` : Connexion
- `GET /commercant/dashboard` : Tableau de bord
- `GET/POST /commercant/boutique/creer` : Créer boutique
- `GET/POST /commercant/produit/ajouter` : Ajouter produit
- `POST /commercant/produit/{id}/modifier` : Modifier produit
- `POST /commercant/produit/{id}/supprimer` : Supprimer produit
- `GET /commercant/commandes` : Gérer commandes
- `POST /commercant/commande/{id}/traiter` : Traiter commande

#### Clients
- `GET/POST /client/inscription` : Inscription
- `GET/POST /client/login` : Connexion
- `GET /client/dashboard` : Explorer boutiques
- `GET /client/panier` : Voir panier
- `POST /client/panier/ajouter/{id}` : Ajouter au panier
- `POST /client/panier/modifier` : Modifier panier
- `GET/POST /client/paiement` : Processus de paiement
- `GET /client/commandes` : Historique commandes

#### Publiques
- `GET /` : Page d'accueil
- `GET /boutique/{id}` : Voir boutique
- `GET /boutiques/recherche` : Rechercher boutiques

## Dépendances

### Core
- Flask==2.3.3 : Framework web
- mysql-connector-python==8.3.0 : Connecteur MySQL
- bcrypt==4.1.2 : Hashage mots de passe

### Extensions Flask
- Flask-Session==0.4.0 : Sessions serveur
- Flask-Compress==1.13 : Compression GZIP
- Flask-WTF==1.2.1 : Formulaires (non utilisé actuellement)

### Utilitaires
- qrcode[pil]==7.4.2 : Génération QR codes
- Pillow==10.4.0 : Manipulation images
- numpy==1.26.4 : Calculs (dépendances)

### Paiements et Communications
- stripe==5.5.0 : Paiements cartes
- twilio==8.13.0 : SMS
- africastalking==1.2.4 : SMS Afrique (non utilisé)

### Autres
- python-dotenv==1.0.1 : Variables d'environnement

## Sécurité

### Authentification
- Hashage bcrypt des mots de passe
- Sessions côté serveur (sécurisé)
- Guards rôle-based (commercant/client)

### Validation
- Emails avec regex
- Téléphones Côte d'Ivoire (+225)
- Sanitisation des entrées

### Protection
- CSRF via Flask-WTF (à implémenter)
- HTTPS recommandé en production
- Variables d'environnement pour secrets

## TODO et Améliorations Futures

### Fonctionnalités à Implémenter
- [ ] Géolocalisation boutiques (carte interactive)
- [ ] Catégories de produits hiérarchiques
- [ ] Système de notation/commentaires
- [ ] Intégration livraison (rapide, etc.)
- [ ] API REST pour applications mobiles
- [ ] Multi-devises (XOF, EUR, USD)
- [ ] Exports Excel/PDF pour commerçants
- [ ] Notifications push web
- [ ] Mode hors-ligne (PWA)

### Améliorations Techniques
- [ ] Tests unitaires (pytest)
- [ ] Logging structuré
- [ ] Cache Redis pour performances
- [ ] Migration vers SQLAlchemy
- [ ] Containerisation Docker
- [ ] CI/CD avec GitHub Actions
- [ ] Monitoring (Sentry, etc.)

### Optimisations UX
- [ ] Progressive Web App (PWA)
- [ ] Mode sombre
- [ ] Internationalisation (anglais, autres langues)
- [ ] Accessibilité (WCAG)
- [ ] Performance (lazy loading images)

## Contribution

### Structure de Développement
- Branches feature/ pour nouvelles fonctionnalités
- Pull requests avec revue de code
- Tests avant merge
- Documentation mise à jour

### Conventions
- Code en français pour noms de fonctions/variables
- Commentaires en anglais pour complexité
- PEP 8 pour style Python
- Commits atomiques et descriptifs

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Support

- **Email** : support@djaapp.ci
- **Téléphone** : +225 XX XX XX XX
- **Documentation** : [Lien vers docs]

---

*Djaapp - Révolutionner le commerce en Afrique, un QR code à la fois.*
