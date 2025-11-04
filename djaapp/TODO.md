# TODO: Créer un contrôleur pour l'authentification (connexion, inscription, déconnexion)

## Étapes à suivre

- [ ] Créer djaapp/controllers/auth.py avec toutes les fonctions d'authentification depuis utilitaires/auth.py
- [ ] Mettre à jour djaapp/routes.py pour importer depuis controllers.auth au lieu de utilitaires.auth
- [ ] Vérifier et mettre à jour tout autre import (ex: si client.py utilise des fonctions auth, mais semble non)
- [ ] Tester que les routes fonctionnent toujours après les changements
- [ ] Supprimer ou déprécier utilitaires/auth.py si plus nécessaire
