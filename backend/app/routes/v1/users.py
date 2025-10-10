"""
Routes pour la gestion des utilisateurs.
"""
from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ... import db
from ...models import User

bp = Blueprint('users', __name__)

# Route POST /users supprimée car redondante avec /auth/register

@bp.get('/users')
def list_users():
    """Lister tous les utilisateurs."""
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users])

@bp.get('/users/<int:user_id>')
def get_user(user_id):
    """Récupérer un utilisateur par son ID."""
    user = User.query.get_or_404(user_id)
    return user.to_dict()

@bp.put('/users/<int:user_id>')
def update_user(user_id):
    """Mettre à jour un utilisateur."""
    user = User.query.get_or_404(user_id)
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
def delete_user(user_id):
    """Supprimer un utilisateur."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return {"deleted": True}