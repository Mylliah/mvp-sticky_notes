"""
Service pour la logique métier de l'authentification.
"""
from typing import Dict, Any, Tuple
from flask import abort
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from flask_jwt_extended import create_access_token
from ..models import User
from ..repositories.user_repository import UserRepository


class AuthService:
    """Service de gestion de l'authentification et des utilisateurs."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[Dict[str, Any], str]:
        """
        Créer un nouvel utilisateur.
        
        Args:
            username: Nom d'utilisateur
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            Tuple (user_dict, access_token)
            
        Raises:
            400: Si les données sont invalides ou si l'utilisateur existe déjà
        """
        # Validation des champs
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
        
        # Vérifier si l'utilisateur existe déjà
        if self.user_repo.exists(username=username, email=email):
            abort(400, description="Username or email already exists")
        
        # Créer l'utilisateur
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        # Sauvegarder
        user = self.user_repo.save(user)
        
        # Générer un token JWT pour login automatique
        access_token = create_access_token(identity=str(user.id))
        
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        
        return user_dict, access_token
    
    def login_user(self, email: str, password: str) -> Tuple[str, Dict[str, Any]]:
        """
        Authentifier un utilisateur et générer un JWT.
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            Tuple (access_token, user_dict)
            
        Raises:
            400: Si les données sont manquantes
            401: Si les credentials sont invalides
        """
        # Validation
        if not email or not password:
            abort(400, description="Missing email or password")
        
        # Chercher l'utilisateur par email
        user = self.user_repo.find_by_email(email)
        
        if not user or not check_password_hash(user.password_hash, password):
            abort(401, description="Invalid credentials")
        
        # Générer le token
        access_token = create_access_token(identity=str(user.id))
        
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
        
        return access_token, user_dict
    
    def get_current_user(self, user_id: int) -> Dict[str, Any]:
        """
        Récupérer le profil de l'utilisateur connecté.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dictionnaire avec les infos de l'utilisateur
            
        Raises:
            404: Si l'utilisateur n'existe pas
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            abort(404, description="User not found")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_date": user.created_date.isoformat() if user.created_date else None
        }
