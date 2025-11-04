import os
from pathlib import Path

# Clé secrète Flask (à changer en production). Vous pouvez aussi utiliser la variable d'environnement DJAAAPP_SECRET_KEY.
SECRET_KEY = os.environ.get("DJAAAPP_SECRET_KEY", "dev-changez-moi")

# Configuration des sessions côté serveur (stockage fichier pour simplicité)
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = str(Path(__file__).resolve().parent / ".sessions")

# Configuration MySQL (modifiable via variables d'environnement)
DB_CONFIG = {
    "host": os.environ.get("DJAAAPP_DB_HOST", "127.0.0.1"),
    "user": os.environ.get("DJAAAPP_DB_USER", "root"),
    "password": os.environ.get("DJAAAPP_DB_PASSWORD", ""),
    "database": os.environ.get("DJAAAPP_DB_NAME", "djaapp_db"),
    "port": int(os.environ.get("DJAAAPP_DB_PORT", "3306")),
    # Autocommit facilite le mode procédural pour des opérations simples
    "autocommit": True,
}
