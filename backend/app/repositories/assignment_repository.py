"""
Repository pour l'accès aux données des assignations.
Encapsule toutes les requêtes SQLAlchemy liées aux assignations.
"""
from typing import List, Optional
from datetime import datetime, timezone
from .. import db
from ..models import Assignment


class AssignmentRepository:
    """Gestion de l'accès aux données pour les assignations."""
    
    def find_by_id(self, assignment_id: int) -> Optional[Assignment]:
        """
        Récupérer une assignation par son ID.
        
        Args:
            assignment_id: ID de l'assignation
            
        Returns:
            Assignment ou None si non trouvée
        """
        return Assignment.query.get(assignment_id)
    
    def find_by_note(self, note_id: int) -> List[Assignment]:
        """
        Récupérer toutes les assignations d'une note.
        
        Args:
            note_id: ID de la note
            
        Returns:
            Liste des assignations
        """
        return Assignment.query.filter_by(note_id=note_id).all()
    
    def find_for_user_and_note(self, user_id: int, note_id: int) -> Optional[Assignment]:
        """
        Récupérer l'assignation d'une note pour un utilisateur spécifique.
        
        Args:
            user_id: ID de l'utilisateur
            note_id: ID de la note
            
        Returns:
            Assignment ou None si non trouvée
        """
        return Assignment.query.filter_by(
            user_id=user_id,
            note_id=note_id
        ).first()
    
    def find_by_user(self, user_id: int) -> List[Assignment]:
        """
        Récupérer toutes les assignations d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des assignations
        """
        return Assignment.query.filter_by(user_id=user_id).all()
    
    def mark_as_read(self, assignment: Assignment) -> Assignment:
        """
        Marquer une assignation comme lue.
        
        Args:
            assignment: Assignment à marquer comme lue
            
        Returns:
            Assignment mise à jour
        """
        assignment.is_read = True
        assignment.read_date = datetime.now(timezone.utc)
        db.session.commit()
        return assignment
    
    def mark_as_unread(self, assignment: Assignment) -> Assignment:
        """
        Marquer une assignation comme non lue.
        
        Args:
            assignment: Assignment à marquer comme non lue
            
        Returns:
            Assignment mise à jour
        """
        assignment.is_read = False
        assignment.read_date = None
        db.session.commit()
        return assignment
    
    def update_status(self, assignment: Assignment, status: str) -> Assignment:
        """
        Mettre à jour le statut d'une assignation.
        
        Args:
            assignment: Assignment à mettre à jour
            status: Nouveau statut ('en_attente', 'en_cours', 'terminé')
            
        Returns:
            Assignment mise à jour
        """
        assignment.recipient_status = status
        
        if status == 'terminé':
            assignment.finished_date = datetime.now(timezone.utc)
        elif status in ['en_attente', 'en_cours']:
            assignment.finished_date = None
        
        db.session.commit()
        return assignment
    
    def toggle_priority(self, assignment: Assignment) -> Assignment:
        """
        Basculer la priorité d'une assignation.
        
        Args:
            assignment: Assignment à modifier
            
        Returns:
            Assignment mise à jour
        """
        assignment.recipient_priority = not assignment.recipient_priority
        db.session.commit()
        return assignment
    
    def save(self, assignment: Assignment) -> Assignment:
        """
        Sauvegarder une assignation (création ou modification).
        
        Args:
            assignment: Instance d'Assignment à sauvegarder
            
        Returns:
            Assignment sauvegardée avec ID généré si création
        """
        db.session.add(assignment)
        db.session.commit()
        db.session.refresh(assignment)
        return assignment
    
    def delete(self, assignment: Assignment) -> None:
        """
        Supprimer une assignation (hard delete).
        
        Args:
            assignment: Assignment à supprimer
        """
        db.session.delete(assignment)
        db.session.commit()
