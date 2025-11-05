"""
Repository pour l'accès aux données des contacts.
Encapsule toutes les requêtes SQLAlchemy liées aux contacts.
"""
from typing import List, Optional
from .. import db
from ..models import Contact


class ContactRepository:
    """Gestion de l'accès aux données pour les contacts."""
    
    def find_by_id(self, contact_id: int) -> Optional[Contact]:
        """
        Récupérer un contact par son ID.
        
        Args:
            contact_id: ID du contact
            
        Returns:
            Contact ou None si non trouvé
        """
        return Contact.query.get(contact_id)
    
    def find_by_user(self, user_id: int) -> List[Contact]:
        """
        Récupérer tous les contacts d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des contacts
        """
        return Contact.query.filter_by(user_id=user_id).all()
    
    def find_by_user_and_contact(self, user_id: int, contact_user_id: int) -> Optional[Contact]:
        """
        Récupérer un contact spécifique entre deux utilisateurs.
        
        Args:
            user_id: ID de l'utilisateur propriétaire
            contact_user_id: ID de l'utilisateur contact
            
        Returns:
            Contact ou None si non trouvé
        """
        return Contact.query.filter_by(
            user_id=user_id,
            contact_user_id=contact_user_id
        ).first()
    
    def exists(self, user_id: int, contact_user_id: int) -> bool:
        """
        Vérifier si un contact existe.
        
        Args:
            user_id: ID de l'utilisateur propriétaire
            contact_user_id: ID de l'utilisateur contact
            
        Returns:
            True si le contact existe
        """
        return self.find_by_user_and_contact(user_id, contact_user_id) is not None
    
    def save(self, contact: Contact) -> Contact:
        """
        Sauvegarder un contact (création ou modification).
        
        Args:
            contact: Instance de Contact à sauvegarder
            
        Returns:
            Contact sauvegardé avec ID généré si création
        """
        db.session.add(contact)
        db.session.commit()
        db.session.refresh(contact)
        return contact
    
    def delete(self, contact: Contact) -> None:
        """
        Supprimer un contact (hard delete).
        
        Args:
            contact: Contact à supprimer
        """
        db.session.delete(contact)
        db.session.commit()
