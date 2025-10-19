"""
Blueprint pour l'authentification.
"""
from flask import Blueprint, request, abort
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from ... import db, limiter
from ...models import User

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

    return {"access_token": access_token, "username": user.username}
