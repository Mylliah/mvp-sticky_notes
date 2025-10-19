"""
Routes pour la gestion des utilisateurs.
"""
import json
from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ... import db
from ...models import User, ActionLog

bp = Blueprint('users', __name__)

# Route POST /users supprimée car redondante avec /auth/register

@bp.get('/users/me')
@jwt_required()
def get_current_user():
    """Récupérer le profil de l'utilisateur connecté."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    return user.to_dict()

@bp.get('/users')
@jwt_required()
def list_users():
    """Lister tous les utilisateurs (authentification requise)."""
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users])

@bp.get('/users/<int:user_id>')
@jwt_required()
def get_user(user_id):
    """Récupérer un utilisateur par son ID (authentification requise)."""
    user = User.query.get_or_404(user_id)
    return user.to_dict()

@bp.put('/users/<int:user_id>')
@jwt_required()
def update_user(user_id):
    """Mettre à jour un utilisateur (seulement son propre profil ou admin)."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    
    # Vérifier que l'utilisateur modifie son propre profil
    if current_user_id != user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin():
            abort(403, description="You can only update your own profile")
    data = request.get_json()
    
    if "username" in data:
        if not data["username"] or data["username"].strip() == "":
            abort(400, description="Username cannot be empty")
        # Vérifier l'unicité du username
        existing = User.query.filter(User.username == data["username"], User.id != user_id).first()
        if existing:
            abort(400, description="Username already exists")
        user.username = data["username"]
        
    if "email" in data:
        if not data["email"] or data["email"].strip() == "":
            abort(400, description="Email cannot be empty")
        # Vérifier l'unicité de l'email
        existing = User.query.filter(User.email == data["email"], User.id != user_id).first()
        if existing:
            abort(400, description="Email already exists")
        user.email = data["email"]
        
    if "password" in data:
        if not data["password"] or data["password"].strip() == "":
            abort(400, description="Password cannot be empty")
        user.password_hash = generate_password_hash(data["password"])
        
    db.session.commit()
    return user.to_dict()

@bp.delete('/users/<int:user_id>')
@jwt_required()
def delete_user(user_id):
    """Supprimer un utilisateur (seulement son propre compte ou admin)."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    
    # Vérifier que l'utilisateur supprime son propre compte
    if current_user_id != user_id:
        current_user = User.query.get(current_user_id)
        if not current_user or not current_user.is_admin():
            abort(403, description="You can only delete your own account")
    
    # Sauvegarder info pour le log
    username = user.username
    
    # Log de suppression d'utilisateur (AVANT la suppression)
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="user_deleted",
        target_id=user_id,
        payload=json.dumps({"username": username})
    )
    db.session.add(action_log)
    
    db.session.delete(user)
    db.session.commit()
    return {"deleted": True}
