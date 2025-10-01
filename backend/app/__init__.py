"""
Module d'initialisation de l'application Flask pour le projet MVP Sticky Notes.
Ce module contient la factory function pour créer l'instance de l'app Flask.
"""
from flask import Flask

def create_app():
    """
    Factory function pour créer et configurer l'app Flask.
    Returns:
        Flask: Instance configurée de l'app Flask avec les routes de base.
    """
    app = Flask(__name__)

    @app.get("/health") # vérifie que l'API répond
    def health():
        return {"status": "ok"}

    return app
