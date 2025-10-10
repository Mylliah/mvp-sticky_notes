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
    
    # Enregistrer tous les blueprints
    blueprints_to_register = [
        notes.bp,
        users.bp,
        assignments.bp,
        contacts.bp,
        action_logs.bp,
        auth.bp
    ]
    
    for blueprint in blueprints_to_register:
        # Vérifier si le blueprint n'est pas déjà enregistré
        if blueprint.name not in app.blueprints:
            app.register_blueprint(blueprint, url_prefix='/v1')
