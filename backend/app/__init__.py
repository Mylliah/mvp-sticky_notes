"""
Module d'initialisation de l'application Flask pour le projet MVP Sticky Notes.
Ce module contient la factory function pour créer l'instance de l'app Flask.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """
    Factory function pour créer et configurer l'app Flask.
    Returns: Flask: Instance configurée de l'app Flask avec les routes de base.
    """
    app = Flask(__name__)

    # Configuration de la clé secrète Flask
    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY", 
        "dev-secret-key-change-in-production"
    )

    # config DB : lit DATABASE_URL (sinon valeur par défaut vers le service 'db')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app:app@db:5432/appdb",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
        "SQLALCHEMY_TRACK_MODIFICATIONS", 
        "False"
    ).lower() == "true"

    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Importer les modèles pour les migrations
    from .models import ActionLog, Assignment, Contact, Note, User

    # Route de base pour vérifier que l'API répond
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Enregistrer les blueprints de l'API v1
    from .routes.v1 import register_v1_blueprints
    register_v1_blueprints(app)

    return app