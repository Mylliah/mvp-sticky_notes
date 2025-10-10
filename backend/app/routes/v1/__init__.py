"""
Module d'initialisation pour l'API v1.
Centralise l'enregistrement de tous les blueprints de la version 1.
"""

def register_v1_blueprints(app):
    """
    Enregistre tous les blueprints de la v1 avec le préfixe /v1.
    Args: app: Instance Flask où enregistrer les blueprints
    """
    from . import notes, users, assignments, contacts, action_logs, auth
    
    # Enregistrer tous les blueprints avec le préfixe v1
    app.register_blueprint(notes.bp, url_prefix='/v1')
    app.register_blueprint(users.bp, url_prefix='/v1')
    app.register_blueprint(assignments.bp, url_prefix='/v1')
    app.register_blueprint(contacts.bp, url_prefix='/v1')
    app.register_blueprint(action_logs.bp, url_prefix='/v1')
    app.register_blueprint(auth.bp, url_prefix='/v1')