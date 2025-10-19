"""
Module d'initialisation de l'application Flask pour le projet MVP Sticky Notes.
Ce module contient la factory function pour créer l'instance de l'app Flask.
"""
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from sqlalchemy import event

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager() # on instancie et on lie à l'app plus bas
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
) 

def create_app(test_config=None):
    """
    Factory function pour créer et configurer l'app Flask.
    Args: test_config (dict, optional): Configuration de test optionnelle.
    Returns: Flask: Instance configurée de l'app Flask avec les routes de base.
    """
    app = Flask(__name__)

    # Configuration de la clé secrète Flask
    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY", 
        "dev-secret-key-change-in-production"
    )

    # Configuration de la clé secrète spécifique JWT
    app.config["JWT_SECRET_KEY"] = os.getenv(
        "JWT_SECRET_KEY",
        "dev-jwt-secret-key-change-in-production"
    )

    # configuration DB : lit DATABASE_URL (sinon valeur par défaut vers le service 'db')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app:app@db:5432/appdb",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
        "SQLALCHEMY_TRACK_MODIFICATIONS", 
        "False"
    ).lower() == "true"

    # Si une configuration de test est fournie, l'appliquer
    if test_config is not None:
        app.config.update(test_config)
    

    # [NOTE] Cette option 'check_same_thread' est spécifique à SQLite et doit être activée uniquement pour les tests locaux avec SQLite.
    # Elle provoque une erreur avec PostgreSQL ou d'autres SGBD. Décommentez la ligne ci-dessous uniquement si vous utilisez SQLite pour les tests :
    # app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {"connect_args": {"check_same_thread": False}})

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app) # intégration JWT dans l'app
    
    # Désactiver le rate limiting en mode test
    if app.config.get("TESTING"):
        limiter.enabled = False
    limiter.init_app(app) # intégration Flask-Limiter
    
    # Configuration CORS
    CORS(app, resources={
        r"/v1/*": {
            "origins": os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })

    # Activer les FK en SQLite (important pour des tests d'intégrité corrects)
    with app.app_context():
        engine = db.engine  # ou db.get_engine(app)
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, conn_record):
            if str(app.config.get("SQLALCHEMY_DATABASE_URI", "")).startswith("sqlite"):
                cur = dbapi_conn.cursor()
                cur.execute("PRAGMA foreign_keys=ON")
                cur.close()

    # Importation des modèles pour les migrations
    from .models import ActionLog, Assignment, Contact, Note, User

    # Route de base pour vérifier que l'API répond
    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    # Erreurs JSON cohérentes
    @app.errorhandler(Exception)
    def handle_exceptions(e):
        # Si c'est une HTTPException → garder le code ; sinon 500
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return jsonify(error=e.name, message=e.description), e.code
        # Log ici si besoin (e)
        return jsonify(error="Internal Server Error", message="An unexpected error occurred"), 500

    # JWT erreurs (messages propres)
    @jwt.invalid_token_loader
    def _invalid_token(err):
        return jsonify(error="Invalid token", message=err), 401

    @jwt.unauthorized_loader
    def _no_token(err):
        return jsonify(error="Missing authorization", message=err), 401

    @jwt.expired_token_loader
    def _expired_token(jwt_header, jwt_payload):
        return jsonify(error="Token expired", message="Please log in again"), 401

    # Enregistrement des blueprints de l'API v1
    from .routes.v1 import register_v1_blueprints
    register_v1_blueprints(app)

    return app