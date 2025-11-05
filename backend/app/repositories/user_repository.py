"""
Repository pour l'accès aux données des utilisateurs.
Encapsule toutes les requêtes SQLAlchemy liées aux utilisateurs.
"""
from typing import Optional
from .. import db
from ..models import User


class UserRepository:
    """Gestion de l'accès aux données pour les utilisateurs."""
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Récupérer un utilisateur par son ID.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            User ou None si non trouvé
        """
        return User.query.get(user_id)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Récupérer un utilisateur par son email.
        
        Args:
            email: Email de l'utilisateur
            
        Returns:
            User ou None si non trouvé
        """
        return User.query.filter_by(email=email).first()
    
    def find_by_username(self, username: str) -> Optional[User]:
        """
        Récupérer un utilisateur par son username.
        
        Args:
            username: Username de l'utilisateur
            
        Returns:
            User ou None si non trouvé
        """
        return User.query.filter_by(username=username).first()
    
    def exists(self, username: str = None, email: str = None) -> bool:
        """
        Vérifier si un utilisateur existe par username ou email.
        
        Args:
            username: Username à vérifier (optionnel)
            email: Email à vérifier (optionnel)
            
        Returns:
            True si l'utilisateur existe
        """
        if username and email:
            return User.query.filter(
                (User.username == username) | (User.email == email)
            ).first() is not None
        elif username:
            return self.find_by_username(username) is not None
        elif email:
            return self.find_by_email(email) is not None
        return False
    
    def save(self, user: User) -> User:
        """
        Sauvegarder un utilisateur (création ou modification).
        
        Args:
            user: Instance de User à sauvegarder
            
        Returns:
            User sauvegardé avec ID généré si création
        """
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user
