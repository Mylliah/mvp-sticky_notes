"""
Routes pour la gestion des notes.
"""
from datetime import datetime
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
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


@bp.get('/notes')
@jwt_required()
def list_notes():
    """Lister toutes les notes (résumé pour vignettes, authentifié)."""
    notes = Note.query.order_by(Note.id.asc()).all()
    current_user_id = int(get_jwt_identity())
    return [note.to_summary_dict(current_user_id=current_user_id) for note in notes]


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
    note.update_date = datetime.utcnow()
    db.session.commit()
    return note.to_dict()


@bp.delete('/notes/<int:note_id>')
@jwt_required()
def delete_note(note_id):
    """Soft delete : pose la date de suppression, conserve la note pour audit (authentifié)."""
    note = Note.query.get_or_404(note_id)
    note.delete_date = datetime.utcnow()
    db.session.commit()
    return note.to_dict()
