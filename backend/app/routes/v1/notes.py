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
        status=data.get("status", "en_cours"),
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
    current_user_id = get_jwt_identity()
    
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
        query = query.order_by(Note.creation_date.asc())
    elif sort_param == 'date_desc':
        query = query.order_by(Note.creation_date.desc())
    elif sort_param == 'important_first':
        # Important d'abord, puis par date décroissante
        query = query.order_by(Note.important.desc(), Note.creation_date.desc())
    else:
        # Par défaut : date décroissante
        query = query.order_by(Note.creation_date.desc())
    
    notes = query.distinct().all()
    return [note.to_dict() for note in notes], 200


@bp.get('/notes/<int:note_id>')
@jwt_required()
def get_note(note_id):
    """Récupérer une note par son ID (affichage complet)."""
    note = Note.query.get_or_404(note_id)
    return note.to_dict()


@bp.get('/notes/<int:note_id>/details')
@jwt_required()
def get_note_details(note_id):
    """Récupérer les détails d'une note sans contenu, pour survol ou audit côté front."""
    note = Note.query.get_or_404(note_id)
    current_user_id = int(get_jwt_identity())
    assignment = Assignment.query.filter_by(note_id=note_id, user_id=current_user_id).first()
    return note.to_details_dict(assignment)


@bp.put('/notes/<int:note_id>')
@jwt_required()
def update_note(note_id):
    """Mettre à jour une note (authentifié)."""
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    if not data or "content" not in data:
        abort(400, description="Missing content")
    note.content = data["content"]
    if "status" in data:
        note.status = data["status"]
    if "important" in data:
        note.important = data["important"]
    note.update_date = datetime.now(timezone.utc)
    db.session.commit()
    return note.to_dict()


@bp.delete('/notes/<int:note_id>')
@jwt_required()
def delete_note(note_id):
    """Soft delete : pose la date de suppression, conserve la note pour audit (authentifié)."""
    note = Note.query.get_or_404(note_id)
    note.delete_date = datetime.now(timezone.utc)
    db.session.commit()
    return note.to_dict()
