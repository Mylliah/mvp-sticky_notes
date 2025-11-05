"""
Service pour la logique métier des notes.
Cette couche orchestre les repositories et contient la logique métier.
"""
import json
from typing import Dict, Any, List
from datetime import datetime, timezone
from flask import abort
from ..models import Note
from ..repositories.note_repository import NoteRepository
from ..repositories.assignment_repository import AssignmentRepository
from ..repositories.user_repository import UserRepository


class NoteService:
    """
    Service de gestion de la logique métier des notes.
    
    Ce service :
    - Vérifie les permissions d'accès
    - Applique les règles métier
    - Orchestre les repositories
    - Construit les réponses formatées
    """
    
    def __init__(self):
        self.note_repo = NoteRepository()
        self.assignment_repo = AssignmentRepository()
        self.user_repo = UserRepository()
    
    def get_note_for_user(self, note_id: int, user_id: int) -> Dict[str, Any]:
        """
        Récupérer une note avec les permissions et la logique métier appropriées.
        
        Cette méthode gère :
        - La vérification d'accès (créateur ou destinataire)
        - Le marquage automatique comme lu (si destinataire)
        - La construction de réponse selon le rôle (créateur vs destinataire)
        
        Args:
            note_id: ID de la note à récupérer
            user_id: ID de l'utilisateur qui demande la note
            
        Returns:
            Dictionnaire contenant les données de la note avec les permissions appropriées
            
        Raises:
            404: Si la note n'existe pas
            403: Si l'utilisateur n'a pas accès à cette note
        """
        # 1. Récupérer la note
        note = self.note_repo.find_by_id(note_id)
        if not note:
            abort(404, description="Note not found")
        
        # 2. Vérifier les permissions d'accès
        is_creator = note.creator_id == user_id
        my_assignment = self.assignment_repo.find_for_user_and_note(user_id, note_id)
        
        if not is_creator and not my_assignment:
            abort(403, description="Access denied")
        
        # 3. Logique métier : auto-marquer comme lu (destinataire uniquement)
        if my_assignment and not my_assignment.is_read:
            self.assignment_repo.mark_as_read(my_assignment)
        
        # 4. Construire la réponse selon le rôle
        if is_creator:
            return self._build_creator_response(note)
        else:
            return self._build_recipient_response(note, my_assignment)
    
    def _build_creator_response(self, note) -> Dict[str, Any]:
        """
        Construire la réponse pour le créateur de la note.
        
        Le créateur peut voir :
        - Tous les destinataires
        - Qui a lu la note
        - Les statuts de tous les destinataires
        - Les informations de suppression
        
        Args:
            note: Instance de Note
            
        Returns:
            Dictionnaire avec toutes les informations pour le créateur
        """
        response = note.to_dict()
        
        # Récupérer toutes les assignations
        all_assignments = self.assignment_repo.find_by_note(note.id)
        
        # Infos de traçabilité de suppression (visible par créateur uniquement)
        if note.deleted_by:
            deleter = self.user_repo.find_by_id(note.deleted_by)
            response["deleted_by_username"] = deleter.username if deleter else None
            response["deleted_by_id"] = note.deleted_by
        
        # Liste des usernames qui ont lu
        response["read_by"] = [
            a.user.username for a in all_assignments if a.is_read and a.user
        ]
        
        # Liste de tous les destinataires
        response["assigned_to"] = [
            a.user.username for a in all_assignments if a.user
        ]
        
        # Détails complets des assignations (visible par créateur)
        response["assignments_details"] = [
            {
                "user_id": a.user_id,
                "username": a.user.username if a.user else None,
                "is_read": a.is_read,
                "read_date": a.read_date.isoformat() if a.read_date else None,
                "recipient_status": a.recipient_status,
                "finished_date": a.finished_date.isoformat() if a.finished_date else None,
                "assigned_date": a.assigned_date.isoformat()
                # recipient_priority est PRIVÉ, pas inclus
            }
            for a in all_assignments
        ]
        
        return response
    
    def _build_recipient_response(self, note, assignment) -> Dict[str, Any]:
        """
        Construire la réponse pour un destinataire de la note.
        
        Le destinataire peut voir :
        - Le contenu de la note
        - Ses propres informations d'assignation (statut, priorité, etc.)
        - Si le créateur a supprimé la note (signal de fin de tâche)
        
        Le destinataire NE peut PAS voir :
        - Les autres destinataires
        - Qui d'autre a lu la note
        - Les statuts des autres destinataires
        
        Args:
            note: Instance de Note
            assignment: Instance d'Assignment pour ce destinataire
            
        Returns:
            Dictionnaire avec les informations limitées au destinataire
        """
        response = note.to_dict()
        
        # Informations personnelles d'assignation
        response["my_assignment"] = {
            "is_read": assignment.is_read,
            "read_date": assignment.read_date.isoformat() if assignment.read_date else None,
            "recipient_priority": assignment.recipient_priority,
            "recipient_status": assignment.recipient_status,
            "finished_date": assignment.finished_date.isoformat() if assignment.finished_date else None,
            "assigned_date": assignment.assigned_date.isoformat()
        }
        
        # Infos de traçabilité : le destinataire voit SEULEMENT si le CRÉATEUR a supprimé
        # (signal que la tâche est terminée et qu'il peut faire le ménage aussi)
        # Mais il ne voit PAS si un autre destinataire a supprimé (confidentialité)
        if note.deleted_by and note.deleted_by == note.creator_id:
            deleter = self.user_repo.find_by_id(note.deleted_by)
            response["deleted_by_creator"] = True
            response["deleted_by_username"] = deleter.username if deleter else None
        
        # Confidentialité : le destinataire ne voit pas les autres
        response["assigned_to"] = None
        response["read_by"] = None
        response["assignments_details"] = None
        
        return response
    
    def check_user_has_access(self, note_id: int, user_id: int) -> bool:
        """
        Vérifier si un utilisateur a accès à une note.
        
        Args:
            note_id: ID de la note
            user_id: ID de l'utilisateur
            
        Returns:
            True si l'utilisateur est créateur ou destinataire
        """
        note = self.note_repo.find_by_id(note_id)
        if not note:
            return False
        
        is_creator = note.creator_id == user_id
        is_recipient = self.assignment_repo.find_for_user_and_note(user_id, note_id) is not None
        
        return is_creator or is_recipient
    
    def create_note(self, content: str, creator_id: int, important: bool = False) -> Dict[str, Any]:
        """
        Créer une nouvelle note.
        
        Args:
            content: Contenu de la note
            creator_id: ID de l'utilisateur créateur
            important: Si la note est importante (défaut: False)
            
        Returns:
            Dictionnaire représentant la note créée
            
        Raises:
            400: Si le contenu est vide ou trop long
        """
        # Validation
        if not content or not content.strip():
            abort(400, description="Missing content")
        
        if len(content) > 5000:
            abort(400, description="Content too long (max 5000 characters)")
        
        # Créer la note
        note = Note(
            content=content,
            creator_id=creator_id,
            important=important
        )
        
        # Sauvegarder
        note = self.note_repo.save(note)
        
        return note.to_dict()
    
    def update_note(self, note_id: int, user_id: int, content: str, important: bool = None) -> Dict[str, Any]:
        """
        Mettre à jour une note existante.
        
        Seul le créateur peut mettre à jour une note.
        
        Args:
            note_id: ID de la note à mettre à jour
            user_id: ID de l'utilisateur qui fait la modification
            content: Nouveau contenu
            important: Nouvelle valeur d'importance (optionnel)
            
        Returns:
            Dictionnaire représentant la note mise à jour
            
        Raises:
            404: Si la note n'existe pas
            403: Si l'utilisateur n'est pas le créateur
            400: Si le contenu est invalide
        """
        # Récupérer la note
        note = self.note_repo.find_by_id(note_id)
        if not note:
            abort(404, description="Note not found")
        
        # Vérifier que l'utilisateur est le créateur
        if note.creator_id != user_id:
            abort(403, description="Only the creator can update this note")
        
        # Validation du contenu
        if not content or not content.strip():
            abort(400, description="Missing content")
        
        if len(content) > 5000:
            abort(400, description="Content too long (max 5000 characters)")
        
        # Mettre à jour
        note.content = content
        if important is not None:
            note.important = important
        note.update_date = datetime.now(timezone.utc)
        
        # Sauvegarder
        note = self.note_repo.save(note)
        
        return note.to_dict()
    
    def delete_note(self, note_id: int, user_id: int) -> Dict[str, Any]:
        """
        Supprimer une note (soft delete).
        
        Peut être fait par le créateur OU par un destinataire.
        
        Args:
            note_id: ID de la note à supprimer
            user_id: ID de l'utilisateur qui supprime
            
        Returns:
            Dictionnaire représentant la note supprimée
            
        Raises:
            404: Si la note n'existe pas
            403: Si l'utilisateur n'a pas accès à la note
        """
        # Récupérer la note
        note = self.note_repo.find_by_id(note_id)
        if not note:
            abort(404, description="Note not found")
        
        # Vérifier que l'utilisateur est créateur OU destinataire
        is_creator = note.creator_id == user_id
        is_recipient = self.assignment_repo.find_for_user_and_note(user_id, note_id) is not None
        
        if not is_creator and not is_recipient:
            abort(403, description="Only the creator or recipient can delete this note")
        
        # Soft delete
        self.note_repo.soft_delete(note, user_id)
        
        return note.to_dict()
    
    def get_note_details(self, note_id: int, user_id: int) -> Dict[str, Any]:
        """
        Récupérer les détails d'une note (sans contenu complet).
        Utilisé pour le survol ou l'audit côté frontend.
        
        Args:
            note_id: ID de la note
            user_id: ID de l'utilisateur
            
        Returns:
            Détails de la note
            
        Raises:
            404: Si la note n'existe pas
        """
        note = self.note_repo.find_by_id(note_id)
        if not note:
            abort(404, description="Note not found")
        
        assignment = self.assignment_repo.find_for_user_and_note(user_id, note_id)
        return note.to_details_dict(assignment)
    
    def get_note_assignments(self, note_id: int, user_id: int) -> Dict[str, Any]:
        """
        Récupérer tous les destinataires avec leur statut.
        
        Accessible uniquement au créateur de la note.
        
        Args:
            note_id: ID de la note
            user_id: ID de l'utilisateur (doit être le créateur)
            
        Returns:
            Dictionnaire avec la liste des assignations
            
        Raises:
            404: Si la note n'existe pas
            403: Si l'utilisateur n'est pas le créateur
        """
        # Récupérer la note
        note = self.note_repo.find_by_id(note_id)
        if not note:
            abort(404, description="Note not found")
        
        # Vérifier que l'utilisateur est le créateur
        if note.creator_id != user_id:
            abort(403, description="Only the creator can view all assignments")
        
        # Récupérer toutes les assignations
        assignments = self.assignment_repo.find_by_note(note_id)
        
        return {
            "note_id": note.id,
            "creator_id": note.creator_id,
            "total_recipients": len(assignments),
            "read_count": sum(1 for a in assignments if a.is_read),
            "completed_count": sum(1 for a in assignments if a.recipient_status == 'terminé'),
            "assignments": [
                {
                    "id": a.id,
                    "user_id": a.user_id,
                    "username": a.user.username if a.user else None,
                    "assigned_date": a.assigned_date.isoformat(),
                    "is_read": a.is_read,
                    "recipient_status": a.recipient_status,
                    "finished_date": a.finished_date.isoformat() if a.finished_date else None
                }
                for a in assignments
            ]
        }
    
    def get_orphan_notes(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupérer les notes orphelines (sans aucune assignation active).
        
        Args:
            user_id: ID de l'utilisateur créateur
            
        Returns:
            Liste des notes orphelines
        """
        # Récupérer toutes les notes créées par l'utilisateur (non supprimées)
        my_notes = self.note_repo.find_created_by(user_id, include_deleted=False)
        
        orphan_notes = []
        for note in my_notes:
            # Vérifier si cette note a encore des assignations actives
            active_assignments = self.assignment_repo.find_by_note(note.id)
            
            if len(active_assignments) == 0:
                # Note sans assignation = note orpheline
                note_dict = note.to_dict()
                note_dict['is_orphan'] = True
                orphan_notes.append(note_dict)
        
        return orphan_notes
    
    def get_deletion_history(self, note_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupérer l'historique des suppressions d'assignations pour une note.
        
        Accessible uniquement au créateur de la note.
        
        Args:
            note_id: ID de la note
            user_id: ID de l'utilisateur (doit être le créateur)
            
        Returns:
            Liste des suppressions d'assignations
            
        Raises:
            404: Si la note n'existe pas
            403: Si l'utilisateur n'est pas le créateur
        """
        from ..models import ActionLog
        
        # Récupérer la note
        note = self.note_repo.find_by_id(note_id)
        if not note:
            abort(404, description="Note not found")
        
        # Vérifier que l'utilisateur est le créateur
        if note.creator_id != user_id:
            abort(403, description="Only the creator can view deletion history")
        
        # Récupérer les logs de suppressions d'assignations
        deletion_logs = ActionLog.query.filter_by(
            action_type="assignment_deleted"
        ).all()
        
        # Filtrer ceux qui concernent cette note
        deletions = []
        for log in deletion_logs:
            try:
                payload = json.loads(log.payload)
                if payload.get("note_id") == note_id:
                    assigned_user_id = payload.get("assigned_user_id")
                    user = self.user_repo.find_by_id(assigned_user_id)
                    
                    deletions.append({
                        "user_id": assigned_user_id,
                        "username": user.username if user else f"User #{assigned_user_id}",
                        "deleted_date": log.timestamp.isoformat() if log.timestamp else None,
                        "deleted_by": log.user_id,
                    })
            except (json.JSONDecodeError, KeyError):
                continue
        
        return deletions
    
    def get_completion_history(self, note_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Récupérer l'historique des completions d'assignations pour une note.
        
        Accessible uniquement au créateur de la note.
        Retourne uniquement les completions actives (non décochées).
        
        Args:
            note_id: ID de la note
            user_id: ID de l'utilisateur (doit être le créateur)
            
        Returns:
            Liste des completions actives
            
        Raises:
            404: Si la note n'existe pas
            403: Si l'utilisateur n'est pas le créateur
        """
        from ..models import ActionLog
        
        # Récupérer la note
        note = self.note_repo.find_by_id(note_id)
        if not note:
            abort(404, description="Note not found")
        
        # Vérifier que l'utilisateur est le créateur
        if note.creator_id != user_id:
            abort(403, description="Only the creator can view completion history")
        
        # Récupérer les logs de completions ET d'uncompletions
        completion_logs = ActionLog.query.filter(
            ActionLog.action_type.in_(['assignment_completed', 'assignment_uncompleted'])
        ).order_by(ActionLog.timestamp.desc()).all()
        
        # Filtrer et déterminer l'état actuel de chaque assignation
        completions_by_assignment = {}
        
        for log in completion_logs:
            try:
                payload = json.loads(log.payload)
                if payload.get("note_id") == note_id:
                    assignment_id = log.target_id
                    
                    # Garder seulement le log le plus récent pour chaque assignation
                    if assignment_id not in completions_by_assignment:
                        completions_by_assignment[assignment_id] = log
                    elif log.timestamp > completions_by_assignment[assignment_id].timestamp:
                        completions_by_assignment[assignment_id] = log
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Construire la liste des completions actives
        completions = []
        for assignment_id, log in completions_by_assignment.items():
            if log.action_type == "assignment_completed":
                payload = json.loads(log.payload)
                assigned_user_id = payload.get("user_id")
                user = self.user_repo.find_by_id(assigned_user_id)
                
                completions.append({
                    "assignment_id": assignment_id,
                    "user_id": assigned_user_id,
                    "username": user.username if user else f"User #{assigned_user_id}",
                    "completed_date": log.timestamp.isoformat() if log.timestamp else None,
                    "completed_by": log.user_id,
                })
        
        return completions
