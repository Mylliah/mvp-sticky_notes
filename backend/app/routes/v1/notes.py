"""
Routes pour la gestion des notes.
"""
from flask import Blueprint, request, abort
from ... import db
from ...models import Note

bp = Blueprint('notes', __name__, url_prefix='/notes')

@bp.post('')
def create_note():
    """Créer une nouvelle note."""
    data = request.get_json()
    if not data or not data.get("content"):
        abort(400, description="Missing content")
    note = Note(content=data["content"], creator_id=data.get("creator_id"))
    db.session.add(note)
    db.session.commit()
    return note.to_dict(), 201

@bp.get('')
def list_notes():
    """Lister toutes les notes."""
    notes = Note.query.order_by(Note.id.asc()).all()
    return [note.to_dict() for note in notes]

@bp.get('/<int:note_id>')
def get_note(note_id):
    """Récupérer une note par son ID."""
    note = Note.query.get_or_404(note_id)
    return note.to_dict()

@bp.put('/<int:note_id>')
def update_note(note_id):
    """Mettre à jour une note."""
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    if not data or "content" not in data:
        abort(400, description="Missing content")
    note.content = data["content"]
    db.session.commit()
    return note.to_dict()

@bp.delete('/<int:note_id>')
def delete_note(note_id):
    """Supprimer une note."""
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return {"deleted": True}
