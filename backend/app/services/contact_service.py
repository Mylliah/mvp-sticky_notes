"""
Service pour la logique métier des contacts.
"""
from typing import Dict, Any, List
from flask import abort
from ..models import Contact
from ..repositories.contact_repository import ContactRepository
from ..repositories.user_repository import UserRepository


class ContactService:
    """Service de gestion de la logique métier des contacts."""
    
    def __init__(self):
        self.contact_repo = ContactRepository()
        self.user_repo = UserRepository()
    
    def get_contacts_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupérer tous les contacts d'un utilisateur.
        
        Inclut l'utilisateur lui-même comme contact spécial.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des contacts avec is_mutual
        """
        # Récupérer l'utilisateur pour l'inclure comme contact spécial
        user = self.user_repo.find_by_id(user_id)
        if not user:
            abort(404, description="User not found")
        
        # Contact spécial : soi-même
        contacts_list = [{
            "id": user.id,
            "user_id": user.id,
            "contact_user_id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": "Moi",
            "is_self": True,
            "contact_action": None,
            "created_date": None,
            "is_mutual": True
        }]
        
        # Contacts réels
        contacts = self.contact_repo.find_by_user(user_id)
        for contact in contacts:
            contact_dict = contact.to_dict()
            # Ajouter username et email du contact_user
            if contact.contact_user:
                contact_dict["username"] = contact.contact_user.username
                contact_dict["email"] = contact.contact_user.email
            contact_dict["is_self"] = False
            contacts_list.append(contact_dict)
        
        return contacts_list
    
    def get_assignable_users(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupérer la liste des utilisateurs assignables.
        
        Un utilisateur est assignable s'il est :
        - L'utilisateur lui-même
        - OU un contact mutuel
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des utilisateurs assignables
        """
        # Inclure soi-même
        user = self.user_repo.find_by_id(user_id)
        if not user:
            abort(404, description="User not found")
        
        assignable = [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_self": True,
            "is_mutual": True
        }]
        
        # Ajouter les contacts mutuels
        contacts = self.contact_repo.find_by_user(user_id)
        for contact in contacts:
            if contact.is_mutual():
                assignable.append({
                    "id": contact.contact_user_id,
                    "username": contact.contact_user.username if contact.contact_user else None,
                    "email": contact.contact_user.email if contact.contact_user else None,
                    "is_self": False,
                    "is_mutual": True
                })
        
        return assignable
    
    def create_contact(self, user_id: int, contact_username: str, 
                      nickname: str, contact_action: str = None) -> Dict[str, Any]:
        """
        Créer un nouveau contact.
        
        Args:
            user_id: ID de l'utilisateur propriétaire
            contact_username: Username de l'utilisateur à ajouter en contact
            nickname: Surnom pour le contact
            contact_action: Action associée (optionnel)
            
        Returns:
            Dictionnaire représentant le contact créé
            
        Raises:
            400: Si tentative d'ajout de soi-même ou si contact existe déjà
            404: Si l'utilisateur contact n'existe pas
        """
        # Vérifier que l'utilisateur contact existe (par username)
        contact_user = self.user_repo.find_by_username(contact_username)
        if not contact_user:
            abort(404, description="User not found")
        
        contact_user_id = contact_user.id
        
        # Vérifier qu'on n'essaie pas de s'ajouter soi-même
        if user_id == contact_user_id:
            abort(400, description="Cannot add yourself as contact")
        
        # Vérifier que le contact n'existe pas déjà
        if self.contact_repo.exists(user_id, contact_user_id):
            abort(400, description="Contact already exists")
        
        # Créer le contact
        from ..models import Contact
        contact = Contact(
            user_id=user_id,
            contact_user_id=contact_user_id,
            nickname=nickname,
            contact_action=contact_action
        )
        
        contact = self.contact_repo.save(contact)
        
        return contact.to_dict()
    
    def get_contact(self, contact_id: int, user_id: int) -> Dict[str, Any]:
        """
        Récupérer un contact par son ID.
        
        Args:
            contact_id: ID du contact
            user_id: ID de l'utilisateur (pour vérifier les permissions)
            
        Returns:
            Dictionnaire représentant le contact
            
        Raises:
            404: Si le contact n'existe pas
            403: Si l'utilisateur n'est pas le propriétaire
        """
        contact = self.contact_repo.find_by_id(contact_id)
        if not contact:
            abort(404, description="Contact not found")
        
        # Vérifier que l'utilisateur est le propriétaire
        if contact.user_id != user_id:
            abort(403, description="You can only view your own contacts")
        
        return contact.to_dict()
    
    def update_contact(self, contact_id: int, user_id: int, 
                      nickname: str = None, contact_action: str = None) -> Dict[str, Any]:
        """
        Mettre à jour un contact (modifier le nickname ou l'action).
        
        Args:
            contact_id: ID du contact à modifier
            user_id: ID de l'utilisateur propriétaire
            nickname: Nouveau nickname (optionnel)
            contact_action: Nouvelle action (optionnel)
            
        Returns:
            Dictionnaire représentant le contact mis à jour
            
        Raises:
            404: Si le contact n'existe pas
            403: Si l'utilisateur n'est pas le propriétaire
        """
        contact = self.contact_repo.find_by_id(contact_id)
        if not contact:
            abort(404, description="Contact not found")
        
        # Vérifier que l'utilisateur est le propriétaire
        if contact.user_id != user_id:
            abort(403, description="You can only update your own contacts")
        
        # Mettre à jour les champs fournis
        if nickname is not None:
            contact.nickname = nickname
        
        if contact_action is not None:
            contact.contact_action = contact_action
        
        contact = self.contact_repo.save(contact)
        
        return contact.to_dict()
    
    def delete_contact(self, contact_id: int, user_id: int) -> Dict[str, Any]:
        """
        Supprimer un contact.
        
        Args:
            contact_id: ID du contact à supprimer
            user_id: ID de l'utilisateur propriétaire
            
        Returns:
            Dictionnaire représentant le contact supprimé
            
        Raises:
            404: Si le contact n'existe pas
            403: Si l'utilisateur n'est pas le propriétaire
        """
        contact = self.contact_repo.find_by_id(contact_id)
        if not contact:
            abort(404, description="Contact not found")
        
        # Vérifier que l'utilisateur est le propriétaire
        if contact.user_id != user_id:
            abort(403, description="You can only delete your own contacts")
        
        contact_dict = contact.to_dict()
        self.contact_repo.delete(contact)
        
        return contact_dict
