"""
Service pour la logique métier des assignations.
"""
from typing import Dict, Any, List
from flask import abort
from ..models import Assignment
from ..repositories.assignment_repository import AssignmentRepository
from ..repositories.note_repository import NoteRepository
from ..repositories.user_repository import UserRepository
from ..repositories.contact_repository import ContactRepository


class AssignmentService:
    """Service de gestion de la logique métier des assignations."""
    
    def __init__(self):
        self.assignment_repo = AssignmentRepository()
        self.note_repo = NoteRepository()
        self.user_repo = UserRepository()
        self.contact_repo = ContactRepository()
    
    def create_assignment(self, note_id: int, user_id: int, creator_id: int, 
                         is_read: bool = False) -> Dict[str, Any]:
        """
        Créer une nouvelle assignation.
        
        Vérifie que :
        - La note existe
        - L'utilisateur existe
        - Le créateur est bien le créateur de la note
        - L'utilisateur assigné est soit le créateur, soit un contact mutuel
        - Pas de doublon
        
        Args:
            note_id: ID de la note
            user_id: ID de l'utilisateur à assigner
            creator_id: ID du créateur de la note (pour vérification)
            is_read: Si l'assignation est déjà lue (défaut: False)
            
        Returns:
            Dictionnaire représentant l'assignation créée
            
        Raises:
            404: Si la note ou l'utilisateur n'existe pas
            403: Si le créateur n'est pas autorisé ou utilisateur pas contact mutuel
            400: Si l'assignation existe déjà
        """
        # Vérifier que la note existe
        note = self.note_repo.find_by_id(note_id)
        if not note:
            abort(404, description="Note not found")
        
        # Vérifier que l'utilisateur à assigner existe
        assigned_user = self.user_repo.find_by_id(user_id)
        if not assigned_user:
            abort(404, description="User not found")
        
        # Vérifier que le créateur est bien le créateur de la note
        if note.creator_id != creator_id:
            abort(403, description="Only the note creator can assign it")
        
        # Vérifier que l'utilisateur assigné est soit le créateur, soit un contact mutuel
        if user_id != creator_id:
            # Vérifier que c'est un contact mutuel
            contact = self.contact_repo.find_by_user_and_contact(creator_id, user_id)
            if not contact or not contact.is_mutual():
                abort(403, description="Can only assign to mutual contacts")
        
        # Vérifier qu'il n'y a pas déjà une assignation
        existing = self.assignment_repo.find_for_user_and_note(user_id, note_id)
        if existing:
            abort(400, description="Assignment already exists")
        
        # Créer l'assignation
        assignment = Assignment(
            note_id=note_id,
            user_id=user_id,
            is_read=is_read
        )
        
        assignment = self.assignment_repo.save(assignment)
        
        return assignment.to_dict()
    
    def get_assignment(self, assignment_id: int, current_user_id: int) -> Dict[str, Any]:
        """
        Récupérer une assignation par son ID.
        
        Accessible par le créateur de la note ou le destinataire.
        
        Args:
            assignment_id: ID de l'assignation
            current_user_id: ID de l'utilisateur qui demande
            
        Returns:
            Dictionnaire représentant l'assignation
            
        Raises:
            404: Si l'assignation n'existe pas
            403: Si l'utilisateur n'a pas accès
        """
        assignment = self.assignment_repo.find_by_id(assignment_id)
        if not assignment:
            abort(404, description="Assignment not found")
        
        # Vérifier l'accès (créateur de la note OU destinataire)
        note = assignment.note
        is_creator = note and note.creator_id == current_user_id
        is_recipient = assignment.user_id == current_user_id
        
        if not is_creator and not is_recipient:
            abort(403, description="Access denied")
        
        return assignment.to_dict()
    
    def update_assignment(self, assignment_id: int, current_user_id: int, 
                         is_read: bool = None, user_id: int = None) -> Dict[str, Any]:
        """
        Mettre à jour une assignation.
        
        Args:
            assignment_id: ID de l'assignation
            current_user_id: ID de l'utilisateur qui modifie
            is_read: Nouveau statut de lecture (optionnel)
            user_id: Nouvel utilisateur assigné (optionnel, créateur uniquement)
            
        Returns:
            Dictionnaire représentant l'assignation mise à jour
            
        Raises:
            404: Si l'assignation n'existe pas
            403: Si l'utilisateur n'a pas les droits
            400: Si données invalides
        """
        assignment = self.assignment_repo.find_by_id(assignment_id)
        if not assignment:
            abort(404, description="Assignment not found")
        
        note = assignment.note
        is_creator = note and note.creator_id == current_user_id
        is_recipient = assignment.user_id == current_user_id
        
        if not is_creator and not is_recipient:
            abort(403, description="Access denied")
        
        # Mise à jour du statut de lecture (créateur ou destinataire)
        if is_read is not None:
            if is_read:
                self.assignment_repo.mark_as_read(assignment)
            else:
                self.assignment_repo.mark_as_unread(assignment)
        
        # Changement d'utilisateur (créateur uniquement)
        if user_id is not None:
            if not is_creator:
                abort(403, description="Only the creator can change the assigned user")
            
            # Vérifier que le nouvel utilisateur existe
            new_user = self.user_repo.find_by_id(user_id)
            if not new_user:
                abort(404, description="User not found")
            
            # Vérifier qu'il n'y a pas de doublon
            if assignment.user_id != user_id:
                existing = self.assignment_repo.find_for_user_and_note(user_id, assignment.note_id)
                if existing:
                    abort(400, description="Assignment already exists for this user")
            
            assignment.user_id = user_id
            assignment = self.assignment_repo.save(assignment)
        
        return assignment.to_dict()
    
    def delete_assignment(self, assignment_id: int, current_user_id: int) -> Dict[str, Any]:
        """
        Supprimer une assignation.
        
        Seul le créateur de la note peut supprimer une assignation.
        
        Args:
            assignment_id: ID de l'assignation à supprimer
            current_user_id: ID de l'utilisateur qui supprime
            
        Returns:
            Dictionnaire représentant l'assignation supprimée
            
        Raises:
            404: Si l'assignation n'existe pas
            403: Si l'utilisateur n'est pas le créateur
        """
        assignment = self.assignment_repo.find_by_id(assignment_id)
        if not assignment:
            abort(404, description="Assignment not found")
        
        # Seul le créateur de la note peut supprimer
        note = assignment.note
        if not note or note.creator_id != current_user_id:
            abort(403, description="Only the note creator can delete assignments")
        
        assignment_dict = assignment.to_dict()
        self.assignment_repo.delete(assignment)
        
        return assignment_dict
    
    def toggle_priority(self, assignment_id: int, current_user_id: int) -> Dict[str, Any]:
        """
        Basculer la priorité d'une assignation.
        
        Seul le destinataire peut changer sa propre priorité.
        
        Args:
            assignment_id: ID de l'assignation
            current_user_id: ID de l'utilisateur (doit être le destinataire)
            
        Returns:
            Dictionnaire représentant l'assignation mise à jour
            
        Raises:
            404: Si l'assignation n'existe pas
            403: Si l'utilisateur n'est pas le destinataire
        """
        assignment = self.assignment_repo.find_by_id(assignment_id)
        if not assignment:
            abort(404, description="Assignment not found")
        
        # Seul le destinataire peut changer sa priorité
        if assignment.user_id != current_user_id:
            abort(403, description="Only the recipient can toggle priority")
        
        assignment = self.assignment_repo.toggle_priority(assignment)
        
        return assignment.to_dict()
    
    def update_status(self, assignment_id: int, current_user_id: int, status: str) -> Dict[str, Any]:
        """
        Mettre à jour le statut d'une assignation.
        
        Seul le destinataire peut changer le statut.
        
        Args:
            assignment_id: ID de l'assignation
            current_user_id: ID de l'utilisateur (doit être le destinataire)
            status: Nouveau statut ('en_attente', 'en_cours', 'terminé')
            
        Returns:
            Dictionnaire représentant l'assignation mise à jour
            
        Raises:
            404: Si l'assignation n'existe pas
            403: Si l'utilisateur n'est pas le destinataire
            400: Si le statut est invalide
        """
        assignment = self.assignment_repo.find_by_id(assignment_id)
        if not assignment:
            abort(404, description="Assignment not found")
        
        # Seul le destinataire peut changer le statut
        if assignment.user_id != current_user_id:
            abort(403, description="Only the recipient can update status")
        
        # Valider le statut
        valid_statuses = ['en_attente', 'en_cours', 'terminé']
        if status not in valid_statuses:
            abort(400, description=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        assignment = self.assignment_repo.update_status(assignment, status)
        
        return assignment.to_dict()
    
    def get_unread_assignments(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupérer les assignations non lues d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des assignations non lues
        """
        assignments = self.assignment_repo.find_by_user(user_id)
        unread = [a.to_dict() for a in assignments if not a.is_read]
        return unread
