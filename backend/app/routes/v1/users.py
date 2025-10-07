"""
Routes pour la gestion des utilisateurs.
"""
from flask import Blueprint, request, abort, jsonify
from werkzeug.security import generate_password_hash
from ... import db
from ...models import User

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.post('')
def create_user():
    """Créer un nouvel utilisateur."""
    data = request.get_json()
    if not data:
        abort(400, description="Missing data")
    
    # Vérifier les champs requis
    required_fields = ['username', 'email', 'password_hash']
    for field in required_fields:
        if not data.get(field):
            abort(400, description=f"Missing {field}")
    
    # Vérifier l'unicité de l'username et de l'email
    existing_user = User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()
    if existing_user:
        if existing_user.username == data['username']:
            abort(400, description="Username already exists")
        if existing_user.email == data['email']:
            abort(400, description="Email already exists")
    
    # Créer le nouvel utilisateur
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=data['password_hash']
    )
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201

@bp.get('')
def list_users():
    """Lister tous les utilisateurs."""
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([u.to_dict() for u in users])

@bp.get('/<int:user_id>')
def get_user(user_id):
    """Récupérer un utilisateur par son ID."""
    user = User.query.get_or_404(user_id)
    return user.to_dict()

@bp.put('/<int:user_id>')
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

@bp.delete('/<int:user_id>')
def delete_user(user_id):
    """Supprimer un utilisateur."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return {"deleted": True}