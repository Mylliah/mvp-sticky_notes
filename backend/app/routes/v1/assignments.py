"""
Routes pour la gestion des assignations.
"""
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ... import db
from ...models import Assignment, Note, User

bp = Blueprint('assignments', __name__)

@bp.post('/assignments')
@jwt_required()
def create_assignment():
    """Créer une nouvelle assignation (authentification requise)."""
    data = request.get_json()
    if not data or not data.get("note_id") or not data.get("user_id"):
        abort(400, description="Missing note_id or user_id")
        
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que la note et l'utilisateur existent
    note = db.session.get(Note, data["note_id"])
    if not note:
        abort(400, description="Note not found")
    user = db.session.get(User, data["user_id"])
    if not user:
        abort(400, description="User not found")
    
    # Vérifier que l'utilisateur est le créateur de la note
    if note.creator_id != current_user_id:
        abort(403, description="Only the creator can assign this note")
    
    # Si on assigne à quelqu'un d'autre (pas soi-même), vérifier que le contact est mutuel
    if data["user_id"] != current_user_id:
        from ...models import Contact
        contact = Contact.query.filter_by(
            user_id=current_user_id,
            contact_user_id=data["user_id"]
        ).first()
        
        if not contact:
            abort(400, description="User is not in your contacts")
        
        if not contact.is_mutual():
            abort(403, description="Cannot assign note: contact has not added you back yet")
        
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

@bp.get('/assignments')
@jwt_required()
def list_assignments():
    """Lister toutes les assignations (authentification requise)."""
    assignments = Assignment.query.order_by(Assignment.id.asc()).all()
    return [a.to_dict() for a in assignments]

@bp.get('/assignments/<int:assignment_id>')
@jwt_required()
def get_assignment(assignment_id):
    """Récupérer une assignation par son ID."""
    assignment = Assignment.query.get_or_404(assignment_id)
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur est soit le créateur de la note, soit le destinataire
    note = db.session.get(Note, assignment.note_id)
    if note.creator_id != current_user_id and assignment.user_id != current_user_id:
        abort(403, description="You can only view your own assignments")
    
    return assignment.to_dict()

@bp.put('/assignments/<int:assignment_id>')
@jwt_required()
def update_assignment(assignment_id):
    """Mettre à jour une assignation (authentification requise)."""
    assignment = Assignment.query.get_or_404(assignment_id)
    current_user_id = int(get_jwt_identity())
    
    # Vérifier que l'utilisateur est soit le créateur de la note, soit le destinataire
    note = db.session.get(Note, assignment.note_id)
    if note.creator_id != current_user_id and assignment.user_id != current_user_id:
        abort(403, description="You can only update your own assignments")
    
    # Le destinataire ne peut modifier que is_read, pas user_id
    data = request.get_json()
    
    if "user_id" in data:
        # Seul le créateur peut changer le destinataire
        if note.creator_id != current_user_id:
            abort(403, description="Only the creator can change the assignment recipient")
        
        # Vérifier que le nouvel utilisateur existe
        user = db.session.get(User, data["user_id"])
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

@bp.delete('/assignments/<int:assignment_id>')
@jwt_required()
def delete_assignment(assignment_id):
    """Supprimer une assignation (authentification requise)."""
    assignment = Assignment.query.get_or_404(assignment_id)
    current_user_id = int(get_jwt_identity())
    
    # Seul le créateur de la note peut supprimer une assignation
    note = db.session.get(Note, assignment.note_id)
    if note.creator_id != current_user_id:
        abort(403, description="Only the creator can delete assignments")
    
    db.session.delete(assignment)
    db.session.commit()
    return {"deleted": True}

@bp.put('/assignments/<int:assignment_id>/priority')
@jwt_required()
def toggle_priority(assignment_id):
    """Basculer la priorité personnelle du destinataire (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Vérifier que l'utilisateur connecté est bien le destinataire
    if assignment.user_id != current_user_id:
        abort(403, description="You can only toggle priority on your own assignments")
    
    # Basculer la priorité
    assignment.recipient_priority = not assignment.recipient_priority
    db.session.commit()
    return assignment.to_dict()

@bp.put('/assignments/<int:assignment_id>/status')
@jwt_required()
def update_status(assignment_id):
    """Modifier le statut personnel du destinataire (authentification requise)."""
    from datetime import datetime, timezone
    
    current_user_id = int(get_jwt_identity())
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Vérifier que l'utilisateur connecté est bien le destinataire
    if assignment.user_id != current_user_id:
        abort(403, description="You can only update status on your own assignments")
    
    data = request.get_json()
    if not data or "recipient_status" not in data:
        abort(400, description="Missing recipient_status")
    
    # Valider le statut
    valid_statuses = ['en_cours', 'terminé']
    if data["recipient_status"] not in valid_statuses:
        abort(400, description=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    # Mettre à jour le statut
    assignment.recipient_status = data["recipient_status"]
    
    # Gérer finished_date selon le statut
    if data["recipient_status"] == "terminé":
        # Marquer comme terminé avec timestamp
        assignment.finished_date = datetime.now(timezone.utc)
    else:
        # Remettre en cours : reset finished_date
        assignment.finished_date = None
    
    db.session.commit()
    return assignment.to_dict()

@bp.get('/assignments/unread')
@jwt_required()
def get_unread_assignments():
    """Récupérer les assignations non lues de l'utilisateur connecté (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    
    unread_assignments = Assignment.query.filter_by(
        user_id=current_user_id,
        is_read=False
    ).order_by(Assignment.assigned_date.desc()).all()
    
    return {
        "count": len(unread_assignments),
        "assignments": [a.to_dict() for a in unread_assignments]
    }
