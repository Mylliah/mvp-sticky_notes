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

bp = Blueprint('auth', __name__)


@bp.post('/auth/register')
@limiter.limit("3 per minute")
def register():
    """
    Endpoint pour créer un nouvel utilisateur.
    """
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        abort(400, description="Missing username, email or password")

    # Valider la longueur du mot de passe
    if len(password) < 8:
        abort(400, description="Password must be at least 8 characters long")

    # Valider le format de l'email
    try:
        validation = validate_email(email, check_deliverability=False)
        email = validation.normalized
    except EmailNotValidError as e:
        abort(400, description=f"Invalid email format: {str(e)}")

    # Vérifie si username ou email existe déjà
    if User.query.filter((User.username==username) | (User.email==email)).first():
        abort(400, description="Username or email already exists")

    # Crée l'utilisateur avec mot de passe haché
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    # Log de création d'utilisateur
    action_log = ActionLog(
        user_id=user.id,
        action_type="user_registered",
        target_id=user.id,
        payload=json.dumps({"username": username, "email": email})
    )
    db.session.add(action_log)
    db.session.commit()

    # Génère un token JWT pour login automatique
    access_token = create_access_token(identity=str(user.id))

    return {
        "msg": "User created successfully",
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "access_token": access_token
    }, 201


@bp.post('/auth/login')
@limiter.limit("5 per minute")
def login():
    """
    Endpoint pour authentifier l'utilisateur et générer un JWT.
    Accepte uniquement email + password.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        abort(400, description="Missing email or password")

    # Cherche par email uniquement
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        abort(401, description="Invalid credentials")

    access_token = create_access_token(identity=str(user.id))

    return {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


@bp.get('/auth/me')
@jwt_required()
def get_me():
    """
    Endpoint pour récupérer le profil de l'utilisateur connecté.
    Utile pour vérifier la validité du token JWT.
    """
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_date": user.created_date.isoformat() if user.created_date else None
    }, 200


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
