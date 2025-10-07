"""
Routes pour la gestion des assignations.
"""
from flask import Blueprint, request, abort
from .. import db
from ..models import Assignment, Note, User

bp = Blueprint('assignments', __name__, url_prefix='/assignments')

@bp.post('')
def create_assignment():
    """Créer une nouvelle assignation."""
    data = request.get_json()
    if not data or not data.get("note_id") or not data.get("user_id"):
        abort(400, description="Missing note_id or user_id")
        
    # Vérifier que la note et l'utilisateur existent
    note = Note.query.get(data["note_id"])
    if not note:
        abort(400, description="Note not found")
    user = User.query.get(data["user_id"])
    if not user:
        abort(400, description="User not found")
        
    # Vérifier qu'il n'y a pas déjà une assignation
    existing = Assignment.query.filter_by(
        note_id=data["note_id"], 
        user_id=data["user_id"]
    ).first()
    if existing:
        abort(400, description="Assignment already exists")
        
    assignment = Assignment(
        note_id=data["note_id"],
        user_id=data["user_id"],
        is_read=data.get("is_read", False)
    )
    db.session.add(assignment)
    db.session.commit()
    return assignment.to_dict(), 201

@bp.get('')
def list_assignments():
    """Lister toutes les assignations."""
    assignments = Assignment.query.order_by(Assignment.id.asc()).all()
    return [a.to_dict() for a in assignments]

@bp.get('/<int:assignment_id>')
def get_assignment(assignment_id):
    """Récupérer une assignation par son ID."""
    assignment = Assignment.query.get_or_404(assignment_id)
    return assignment.to_dict()

@bp.put('/<int:assignment_id>')
def update_assignment(assignment_id):
    """Mettre à jour une assignation."""
    assignment = Assignment.query.get_or_404(assignment_id)
    data = request.get_json()
    
    if "user_id" in data:
        # Vérifier que le nouvel utilisateur existe
        user = User.query.get(data["user_id"])
        if not user:
            abort(400, description="User not found")
        # Vérifier qu'il n'y a pas déjà une assignation avec ce user
        existing = Assignment.query.filter_by(
            note_id=assignment.note_id, 
            user_id=data["user_id"]
        ).filter(Assignment.id != assignment_id).first()
        if existing:
            abort(400, description="Assignment already exists for this user")
        assignment.user_id = data["user_id"]
        
    if "is_read" in data:
        assignment.is_read = data["is_read"]
        
    db.session.commit()
    return assignment.to_dict()

@bp.delete('/<int:assignment_id>')
def delete_assignment(assignment_id):
    """Supprimer une assignation."""
    assignment = Assignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    return {"deleted": True}