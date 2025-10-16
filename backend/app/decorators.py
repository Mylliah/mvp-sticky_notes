"""
Décorateurs personnalisés pour la gestion des autorisations.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from .models import User


def admin_required():
    """
    Décorateur pour restreindre l'accès aux administrateurs uniquement.
    Doit être utilisé après @jwt_required().
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            if not user.is_admin():
                return jsonify({"error": "Admin access required"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
