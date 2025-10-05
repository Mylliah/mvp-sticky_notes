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

    # config DB : lit DATABASE_URL (sinon valeur par défaut vers le service 'db')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app:app@db:5432/appdb",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # branche SQLAlchemy + Alembic/Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/health") # vérifie que l'API répond
    def health():
        return {"status": "ok"}

    # import provisoire des modèles ici "from . import models (models.py)"
    from . import models
    from flask import jsonify
    from .models import Note

    @app.get("/notes")
    def list_notes():
        notes = Note.query.order_by(Note.id.asc()).all()
        return jsonify([n.to_dict() for n in notes])

    return app
