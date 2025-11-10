"""
Routes pour la gestion des utilisateurs.
"""
import json
from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from ...models import User, ActionLog
from ...services import UserService
from ...repositories import ActionLogRepository

bp = Blueprint('users', __name__)

# Route POST /users supprimée car redondante avec /auth/register

@bp.get('/users/me')
@jwt_required()
def get_current_user():
    """Récupérer le profil de l'utilisateur connecté."""
    current_user_id = int(get_jwt_identity())
    
    # Utiliser le service
    service = UserService()
    user = service.get_user(current_user_id, current_user_id)
    
    return user

@bp.get('/users')
@jwt_required()
def list_users():
    """Lister tous les utilisateurs (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    is_admin = current_user and current_user.is_admin()
    
    # Utiliser le service
    service = UserService()
    users = service.list_users(
        current_user_id=current_user_id,
        is_admin=is_admin
    )
    
    return jsonify(users)

@bp.get('/users/<int:user_id>')
@jwt_required()
def get_user(user_id):
    """Récupérer un utilisateur par son ID (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    is_admin = current_user and current_user.is_admin()
    
    # Utiliser le service
    service = UserService()
    user = service.get_user(user_id, current_user_id, is_admin)
    
    return user

@bp.put('/users/<int:user_id>')
@jwt_required()
def update_user(user_id):
    """Mettre à jour un utilisateur (seulement son propre profil ou admin)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    is_admin = current_user and current_user.is_admin()
    
    data = request.get_json()
    
    # Validation du changement de mot de passe (si demandé)
    password = None
    if "new_password" in data:
        # Vérifier que current_password est fourni
        if "current_password" not in data:
            abort(400, description="Current password is required to change password")
        
        # Vérifier que le mot de passe actuel est correct
        user_obj = User.query.get_or_404(user_id)
        if not check_password_hash(user_obj.password_hash, data["current_password"]):
            abort(400, description="Current password is incorrect")
        
        # Valider la longueur du nouveau mot de passe
        if len(data["new_password"]) < 6:
            abort(400, description="New password must be at least 6 characters long")
        
        password = data["new_password"]
        
        # Log de changement de mot de passe
        action_log = ActionLog(
            user_id=current_user_id,
            action_type="password_changed",
            target_id=user_id,
            payload=json.dumps({"timestamp": "password_updated"})
        )
        action_log_repo = ActionLogRepository()
        action_log_repo.save(action_log)
    
    # Ancien format "password" (pour compatibilité)
    elif "password" in data:
        if not data["password"] or data["password"].strip() == "":
            abort(400, description="Password cannot be empty")
        password = data["password"]
    
    # Utiliser le service
    service = UserService()
    user = service.update_user(
        user_id=user_id,
        current_user_id=current_user_id,
        is_admin=is_admin,
        username=data.get("username"),
        email=data.get("email"),
        password=password,
        role=data.get("role")
    )
    
    return user

@bp.delete('/users/<int:user_id>')
@jwt_required()
def delete_user(user_id):
    """Supprimer un utilisateur (seulement son propre compte ou admin)."""
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    is_admin = current_user and current_user.is_admin()
    
    # Sauvegarder info pour le log
    user_obj = User.query.get_or_404(user_id)
    username = user_obj.username
    
    # Log de suppression d'utilisateur (AVANT la suppression)
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="user_deleted",
        target_id=user_id,
        payload=json.dumps({"username": username})
    )
    action_log_repo = ActionLogRepository()
    action_log_repo.save(action_log)
    
    # Utiliser le service
    service = UserService()
    service.delete_user(user_id, current_user_id, is_admin)
    
    return {"deleted": True}