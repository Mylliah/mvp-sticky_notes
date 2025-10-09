"""
Routes pour la gestion des notes.
"""
from datetime import datetime
from flask import Blueprint, request, abort
from ... import db
from ...models import Note, Assignment

bp = Blueprint('notes', __name__, url_prefix='/notes')


@bp.post('')
def create_note():
    """Créer une nouvelle note"""
    data = request.get_json()
    if not data or not data.get("content"):
        abort(400, description="Missing content")
    note = Note(
        content=data["content"],
        creator_id=data.get("creator_id"),
        status=data.get("status", "en_cours"),
        important=data.get("important", False)
    )
    db.session.add(note)
    db.session.commit()
    return note.to_dict(), 201


@bp.get('')
def list_notes():
    """Lister toutes les notes (résumé pour vignettes)"""
    notes = Note.query.order_by(Note.id.asc()).all()
    # À remplacer par la mécanique auth réelle
    # from flask_jwt_extended import get_jwt_identity
    # current_user_id = get_jwt_identity()
    current_user_id = 1  # temporaire pour test/dev
    return [note.to_summary_dict(current_user_id=current_user_id) for note in notes]


@bp.get('/<int:note_id>')
def get_note(note_id):
    """Récupérer une note par son ID (pour affichage détail/contenu)."""
    note = Note.query.get_or_404(note_id)
    return note.to_dict()


@bp.get('/<int:note_id>/details')
def get_note_details(note_id):
    """Récupérer les détails d'une note sans le contenu, pour survol ou audit."""
    note = Note.query.get_or_404(note_id)
    current_user_id = 1  # À remplacer par auth réelle
    assignment = Assignment.query.filter_by(note_id=note_id, user_id=current_user_id).first()
    return note.to_details_dict(assignment)


@bp.put('/<int:note_id>')
def update_note(note_id):
    """Mettre à jour une note."""
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


@bp.delete('/<int:note_id>')
def delete_note(note_id):
    """Soft delete : signale la suppression, mais conserve la note pour audit."""
    note = Note.query.get_or_404(note_id)
    note.delete_date = datetime.utcnow()
    db.session.commit()
    return note.to_dict()
