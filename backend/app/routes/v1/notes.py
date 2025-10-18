"""
Routes pour la gestion des notes.
"""
from datetime import datetime, timezone
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from ... import db
from ...models import Note, Assignment

bp = Blueprint('notes', __name__)


@bp.post('/notes')
@jwt_required()
def create_note():
    """Créer une nouvelle note (requiert authentification)."""
    data = request.get_json()
    if not data or not data.get("content"):
        abort(400, description="Missing content")
    current_user_id = int(get_jwt_identity())
    note = Note(
        content=data["content"],
        creator_id=current_user_id,
        important=data.get("important", False)
    )
    db.session.add(note)
    db.session.commit()
    return note.to_dict(), 201


@bp.route('/notes', methods=['GET'])
@jwt_required()
def get_notes():
    """
    Get all notes with their assignments
    ---
    Returns list of notes created by OR assigned to current user
    Query Parameters:
      - filter: 'important', 'important_by_me', 'unread', 'received', 'sent'
      - sort: 'date_asc', 'date_desc', 'important_first'
    """
    current_user_id = int(get_jwt_identity())
    
    # Query de base
    query = Note.query.join(
        Assignment, Note.id == Assignment.note_id, isouter=True
    ).filter(
        or_(
            Note.creator_id == current_user_id,
            Assignment.user_id == current_user_id
        )
    )
    
    # Filtres
    filter_param = request.args.get('filter')
    if filter_param:
        if filter_param == 'important':
            # Notes marquées importantes par le créateur
            query = query.filter(Note.important == True)
        elif filter_param == 'important_by_me':
            # Notes marquées prioritaires par le destinataire
            query = query.filter(
                Assignment.user_id == current_user_id,
                Assignment.recipient_priority == True
            )
        elif filter_param == 'unread':
            # Assignations non lues
            query = query.filter(
                Assignment.user_id == current_user_id,
                Assignment.is_read == False
            )
        elif filter_param == 'received':
            # Notes assignées à l'utilisateur (pas créées par lui)
            query = query.filter(
                Assignment.user_id == current_user_id,
                Note.creator_id != current_user_id
            )
        elif filter_param == 'sent':
            # Notes créées par l'utilisateur
            query = query.filter(Note.creator_id == current_user_id)
    
    # Tri
    sort_param = request.args.get('sort', 'date_desc')
    if sort_param == 'date_asc':
        query = query.order_by(Note.created_date.asc())
    elif sort_param == 'date_desc':
        query = query.order_by(Note.created_date.desc())
    elif sort_param == 'important_first':
        # Important d'abord, puis par date décroissante
        query = query.order_by(Note.important.desc(), Note.created_date.desc())
    else:
        # Par défaut : date décroissante
        query = query.order_by(Note.created_date.desc())
    
    notes = query.distinct().all()
    return [note.to_dict() for note in notes], 200


@bp.get('/notes/<int:note_id>')
@jwt_required()
def get_note(note_id):
    """Récupérer une note par son ID avec infos contextuelles selon le rôle."""
    current_user_id = int(get_jwt_identity())
    note = Note.query.get_or_404(note_id)
    
    # Vérifier accès (créateur OU destinataire)
    is_creator = note.creator_id == current_user_id
    my_assignment = Assignment.query.filter_by(
        note_id=note_id,
        user_id=current_user_id
    ).first()
    
    if not is_creator and not my_assignment:
        abort(403, description="Access denied")
    
    # Auto-marquer comme lu si destinataire
    if my_assignment and not my_assignment.is_read:
        my_assignment.is_read = True
        my_assignment.read_date = datetime.now(timezone.utc)
        db.session.commit()
    
    # Construire la réponse de base
    response = note.to_dict()
    
    if is_creator:
        # CRÉATEUR : voir tous les destinataires et leurs statuts
        all_assignments = Assignment.query.filter_by(note_id=note_id).all()
        
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
        
    else:
        # DESTINATAIRE : voir uniquement ses propres infos
        response["my_assignment"] = {
            "is_read": my_assignment.is_read,
            "read_date": my_assignment.read_date.isoformat() if my_assignment.read_date else None,
            "recipient_priority": my_assignment.recipient_priority,
            "recipient_status": my_assignment.recipient_status,
            "finished_date": my_assignment.finished_date.isoformat() if my_assignment.finished_date else None,
            "assigned_date": my_assignment.assigned_date.isoformat()
        }
        
        # Confidentialité : le destinataire ne voit pas les autres
        response["assigned_to"] = None
        response["read_by"] = None
        response["assignments_details"] = None
    
    return response


@bp.get('/notes/<int:note_id>/details')
@jwt_required()
def get_note_details(note_id):
    """Récupérer les détails d'une note sans contenu, pour survol ou audit côté front."""
    note = Note.query.get_or_404(note_id)
    current_user_id = int(get_jwt_identity())
    assignment = Assignment.query.filter_by(note_id=note_id, user_id=current_user_id).first()
    return note.to_details_dict(assignment)


@bp.get('/notes/<int:note_id>/assignments')
@jwt_required()
def get_note_assignments(note_id):
    """Récupérer tous les destinataires avec leur statut (créateur uniquement)."""
    note = Note.query.get_or_404(note_id)
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur est bien le créateur
    if note.creator_id != current_user_id:
        abort(403, description="Only the creator can view all assignments")
    
    # Récupérer toutes les assignations
    assignments = Assignment.query.filter_by(note_id=note_id).order_by(Assignment.assigned_date.desc()).all()
    
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
                # recipient_priority est PRIVÉ, le créateur ne le voit pas
            }
            for a in assignments
        ]
    }


@bp.put('/notes/<int:note_id>')
@jwt_required()
def update_note(note_id):
    """Mettre à jour une note (authentifié)."""
    note = Note.query.get_or_404(note_id)
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur est bien le créateur
    if note.creator_id != current_user_id:
        abort(403, description="Only the creator can update this note")
    
    data = request.get_json()
    if not data or "content" not in data:
        abort(400, description="Missing content")
    note.content = data["content"]
    if "important" in data:
        note.important = data["important"]
    note.update_date = datetime.now(timezone.utc)
    db.session.commit()
    return note.to_dict()


@bp.delete('/notes/<int:note_id>')
@jwt_required()
def delete_note(note_id):
    """
    Soft delete : pose la date de suppression et enregistre qui a supprimé.
    Autorisé pour le créateur OU le destinataire de la note (traçabilité complète).
    """
    note = Note.query.get_or_404(note_id)
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur est créateur OU destinataire
    is_creator = note.creator_id == current_user_id
    is_recipient = Assignment.query.filter_by(
        note_id=note_id,
        user_id=current_user_id
    ).first() is not None
    
    if not is_creator and not is_recipient:
        abort(403, description="Only the creator or recipient can delete this note")
    
    # Soft delete avec traçabilité de QUI a supprimé
    note.delete_date = datetime.now(timezone.utc)
    note.deleted_by = current_user_id
    db.session.commit()
    
    return note.to_dict()
