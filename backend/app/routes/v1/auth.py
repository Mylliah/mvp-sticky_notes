"""
Blueprint pour l'authentification.
"""
import json
from flask import Blueprint, request, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from ... import db, limiter
from ...models import User, ActionLog
from ...services.auth_service import AuthService

bp = Blueprint('auth', __name__)

# Instancier le service
auth_service = AuthService()


@bp.post('/auth/register')
@limiter.limit("3 per minute")
def register():
    """
    Endpoint pour créer un nouvel utilisateur.
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    data = request.get_json()
    
    # ✅ Délégation au service
    user_dict, access_token = auth_service.register_user(
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password")
    )
    
    # Log de création d'utilisateur
    action_log = ActionLog(
        user_id=user_dict["id"],
        action_type="user_registered",
        target_id=user_dict["id"],
        payload=json.dumps({"username": user_dict["username"], "email": user_dict["email"]})
    )
    db.session.add(action_log)
    db.session.commit()

    return {
        "msg": "User created successfully",
        "id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "access_token": access_token
    }, 201


@bp.post('/auth/login')
@limiter.limit("5 per minute")
def login():
    """
    Endpoint pour authentifier l'utilisateur et générer un JWT.
    Accepte uniquement email + password.
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    data = request.get_json()
    
    # ✅ Délégation au service
    access_token, user_dict = auth_service.login_user(
        email=data.get("email"),
        password=data.get("password")
    )

    return {
        "access_token": access_token,
        "user": user_dict
    }


@bp.get('/auth/me')
@jwt_required()
def get_me():
    """
    Endpoint pour récupérer le profil de l'utilisateur connecté.
    Utile pour vérifier la validité du token JWT.
    
    ✅ REFACTORÉ : Architecture 3 couches
    """
    current_user_id = int(get_jwt_identity())
    
    # ✅ Délégation au service
    user_dict = auth_service.get_current_user(current_user_id)
    
    return user_dict, 200


@bp.post('/auth/logout')
@jwt_required()
def logout():
    """
    Endpoint pour déconnecter l'utilisateur.
    
    Note: Avec JWT stateless, le token reste valide jusqu'à expiration.
    Le client doit supprimer le token de son côté.
    Ce endpoint sert principalement à :
    - Logger l'action de déconnexion pour l'audit
    - Informer l'utilisateur que la déconnexion a réussi
    - Préparer pour une future blacklist de tokens si nécessaire
    """
    current_user_id = int(get_jwt_identity())
    
    # Log de déconnexion
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="user_logout",
        target_id=current_user_id,
        payload=json.dumps({"timestamp": "logout"})
    )
    db.session.add(action_log)
    db.session.commit()
    
    return {
        "msg": "Successfully logged out"
    }, 200
