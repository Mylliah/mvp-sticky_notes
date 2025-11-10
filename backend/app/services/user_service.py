"""
Service pour la logique métier des utilisateurs.
"""
from typing import Dict, Any, List, Optional
from flask import abort
from werkzeug.security import generate_password_hash
from ..models import User
from ..repositories.user_repository import UserRepository


class UserService:
    """Service de gestion de la logique métier des utilisateurs."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def get_user(self, user_id: int, current_user_id: int, is_admin: bool = False) -> Dict[str, Any]:
        """
        Récupérer un utilisateur par son ID.
        
        Un utilisateur peut voir son propre profil.
        Un admin peut voir n'importe quel profil.
        
        Args:
            user_id: ID de l'utilisateur à récupérer
            current_user_id: ID de l'utilisateur qui demande
            is_admin: Si l'utilisateur qui demande est admin
            
        Returns:
            Dictionnaire représentant l'utilisateur
            
        Raises:
            404: Si l'utilisateur n'existe pas
            403: Si accès non autorisé
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            abort(404, description="User not found")
        
        # Vérifier l'accès (soi-même ou admin)
        if user_id != current_user_id and not is_admin:
            abort(403, description="Access denied")
        
        return user.to_dict()
    
    def update_user(self, user_id: int, current_user_id: int, is_admin: bool = False,
                   username: Optional[str] = None, email: Optional[str] = None, 
                   password: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """
        Mettre à jour un utilisateur.
        
        Un utilisateur peut modifier son propre profil (username, email, password).
        Un admin peut modifier n'importe quel profil et changer le rôle.
        
        Args:
            user_id: ID de l'utilisateur à modifier
            current_user_id: ID de l'utilisateur qui modifie
            is_admin: Si l'utilisateur qui modifie est admin
            username: Nouveau nom d'utilisateur (optionnel)
            email: Nouvel email (optionnel)
            password: Nouveau mot de passe (optionnel)
            role: Nouveau rôle (optionnel, admin uniquement)
            
        Returns:
            Dictionnaire représentant l'utilisateur mis à jour
            
        Raises:
            404: Si l'utilisateur n'existe pas
            403: Si accès non autorisé
            400: Si données invalides
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            abort(404, description="User not found")
        
        # Vérifier l'accès (soi-même ou admin)
        if user_id != current_user_id and not is_admin:
            abort(403, description="Access denied")
        
        # Mise à jour du username
        if username is not None:
            if len(username.strip()) < 3:
                abort(400, description="Username must be at least 3 characters")
            
            # Vérifier l'unicité
            existing = self.user_repo.find_by_username(username)
            if existing and existing.id != user_id:
                abort(400, description="Username already exists")
            
            user.username = username.strip()
        
        # Mise à jour de l'email
        if email is not None:
            if not email or '@' not in email:
                abort(400, description="Invalid email format")
            
            # Vérifier l'unicité
            existing = self.user_repo.find_by_email(email)
            if existing and existing.id != user_id:
                abort(400, description="Email already exists")
            
            user.email = email.strip().lower()
        
        # Mise à jour du mot de passe
        if password is not None:
            if len(password) < 6:
                abort(400, description="Password must be at least 6 characters")
            
            user.password = generate_password_hash(password)
        
        # Mise à jour du rôle (admin uniquement)
        if role is not None:
            if not is_admin:
                abort(403, description="Only admins can change user roles")
            
            valid_roles = ['user', 'admin']
            if role not in valid_roles:
                abort(400, description=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
            
            user.role = role
        
        user = self.user_repo.save(user)
        
        return user.to_dict()
    
    def delete_user(self, user_id: int, current_user_id: int, is_admin: bool = False) -> Dict[str, Any]:
        """
        Supprimer un utilisateur.
        
        Un utilisateur peut supprimer son propre compte.
        Un admin peut supprimer n'importe quel compte.
        
        Args:
            user_id: ID de l'utilisateur à supprimer
            current_user_id: ID de l'utilisateur qui supprime
            is_admin: Si l'utilisateur qui supprime est admin
            
        Returns:
            Dictionnaire représentant l'utilisateur supprimé
            
        Raises:
            404: Si l'utilisateur n'existe pas
            403: Si accès non autorisé
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            abort(404, description="User not found")
        
        # Vérifier l'accès (soi-même ou admin)
        if user_id != current_user_id and not is_admin:
            abort(403, description="Access denied")
        
        user_dict = user.to_dict()
        
        # ✅ Utiliser le repository pour la suppression
        # La suppression en cascade est gérée par SQLAlchemy
        # Notes, Assignments, Contacts, ActionLogs seront supprimés
        self.user_repo.delete(user)
        
        return user_dict
    
    def list_users(self, current_user_id: int, is_admin: bool = False, 
                   page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """
        Lister tous les utilisateurs.
        
        Accessible à tous pour compatibilité (peut être restreint aux admins si nécessaire).
        
        Args:
            current_user_id: ID de l'utilisateur qui demande
            is_admin: Si l'utilisateur qui demande est admin
            page: Numéro de page (défaut: 1)
            per_page: Éléments par page (défaut: 20)
            
        Returns:
            Liste des utilisateurs (pour compatibilité avec l'ancienne API)
            
        Raises:
            Aucune exception
        """
        # Pour compatibilité avec l'ancienne API, retourner une liste simple
        from ..models import User
        
        users = User.query.order_by(User.id.asc()).all()
        return [user.to_dict() for user in users]
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Récupérer un utilisateur par email.
        
        Args:
            email: Email de l'utilisateur
            
        Returns:
            Dictionnaire représentant l'utilisateur ou None
        """
        user = self.user_repo.find_by_email(email)
        if not user:
            return None
        return user.to_dict()
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Récupérer un utilisateur par nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            Dictionnaire représentant l'utilisateur ou None
        """
        user = self.user_repo.find_by_username(username)
        if not user:
            return None
        return user.to_dict()
