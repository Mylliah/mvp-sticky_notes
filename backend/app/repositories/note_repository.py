"""
Repository pour l'accès aux données des notes.
Encapsule toutes les requêtes SQLAlchemy liées aux notes.
"""
from typing import List, Optional
from sqlalchemy import or_
from .. import db
from ..models import Note, Assignment


class NoteRepository:
    """Gestion de l'accès aux données pour les notes."""
    
    def find_by_id(self, note_id: int) -> Optional[Note]:
        """
        Récupérer une note par son ID.
        
        Args:
            note_id: ID de la note
            
        Returns:
            Note ou None si non trouvée
        """
        return Note.query.get(note_id)
    
    def find_visible_by_user(self, user_id: int, include_deleted: bool = False) -> List[Note]:
        """
        Récupérer toutes les notes visibles par un utilisateur.
        Une note est visible si l'utilisateur est créateur OU destinataire.
        
        Args:
            user_id: ID de l'utilisateur
            include_deleted: Inclure les notes supprimées (soft delete)
            
        Returns:
            Liste des notes visibles
        """
        query = Note.query.join(
            Assignment, Note.id == Assignment.note_id, isouter=True
        ).filter(
            or_(
                Note.creator_id == user_id,
                Assignment.user_id == user_id
            )
        )
        
        if not include_deleted:
            query = query.filter(Note.delete_date.is_(None))
        
        return query.distinct().all()
    
    def find_created_by(self, user_id: int, include_deleted: bool = False) -> List[Note]:
        """
        Récupérer toutes les notes créées par un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur créateur
            include_deleted: Inclure les notes supprimées
            
        Returns:
            Liste des notes créées
        """
        query = Note.query.filter_by(creator_id=user_id)
        
        if not include_deleted:
            query = query.filter(Note.delete_date.is_(None))
        
        return query.all()
    
    def save(self, note: Note) -> Note:
        """
        Sauvegarder une note (création ou modification).
        
        Args:
            note: Instance de Note à sauvegarder
            
        Returns:
            Note sauvegardée avec ID généré si création
        """
        db.session.add(note)
        db.session.commit()
        db.session.refresh(note)  # Rafraîchir pour avoir les relations à jour
        return note
    
    def soft_delete(self, note: Note, deleted_by_user_id: int) -> None:
        """
        Suppression logique (soft delete) d'une note.
        
        Args:
            note: Note à supprimer
            deleted_by_user_id: ID de l'utilisateur qui supprime
        """
        from datetime import datetime, timezone
        note.delete_date = datetime.now(timezone.utc)
        note.deleted_by = deleted_by_user_id
        db.session.commit()
    
    def count_orphans(self, user_id: int) -> int:
        """
        Compter les notes orphelines d'un utilisateur.
        Une note orpheline = créée par l'utilisateur + aucune assignation active.
        
        Args:
            user_id: ID de l'utilisateur créateur
            
        Returns:
            Nombre de notes orphelines
        """
        # Notes créées par l'utilisateur, non supprimées
        my_notes = self.find_created_by(user_id, include_deleted=False)
        
        orphan_count = 0
        for note in my_notes:
            # Compter les assignations pour cette note
            assignment_count = Assignment.query.filter_by(note_id=note.id).count()
            if assignment_count == 0:
                orphan_count += 1
        
        return orphan_count
