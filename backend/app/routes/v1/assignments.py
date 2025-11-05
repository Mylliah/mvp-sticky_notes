"""
Routes pour la gestion des assignations.
"""
import json
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from ... import db
from ...models import Assignment, Note, ActionLog
from ...services import AssignmentService

bp = Blueprint('assignments', __name__)

@bp.post('/assignments')
@jwt_required()
def create_assignment():
    """Créer une nouvelle assignation (authentification requise)."""
    data = request.get_json()
    if not data or not data.get("note_id") or not data.get("user_id"):
        abort(400, description="Missing note_id or user_id")
        
    current_user_id = int(get_jwt_identity())
    
    # Utiliser le service
    service = AssignmentService()
    assignment = service.create_assignment(
        note_id=data["note_id"],
        user_id=data["user_id"],
        creator_id=current_user_id,
        is_read=data.get("is_read", False)
    )
    
    # Log de création d'assignation
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="assignment_created",
        target_id=assignment["id"],
        payload=json.dumps({"note_id": data["note_id"], "assigned_to": data["user_id"]})
    )
    db.session.add(action_log)
    db.session.commit()
    
    return assignment, 201

@bp.get('/assignments')
@jwt_required()
def list_assignments():
    """Lister les assignations avec filtres optionnels (authentification requise)."""
    # Récupérer les paramètres de requête
    note_id = request.args.get('note_id', type=int)
    user_id = request.args.get('user_id', type=int)
    assigner_id = request.args.get('assigner_id', type=int)
    status = request.args.get('status')
    
    # Construire la requête avec filtres
    query = Assignment.query
    
    if note_id:
        query = query.filter_by(note_id=note_id)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if assigner_id:
        # Filtrer par créateur de la note
        query = query.join(Note).filter(Note.creator_id == assigner_id)
    
    if status:
        query = query.filter_by(recipient_status=status)
    
    assignments = query.order_by(Assignment.id.asc()).all()
    return [a.to_dict() for a in assignments]

@bp.get('/assignments/<int:assignment_id>')
@jwt_required()
def get_assignment(assignment_id):
    """Récupérer une assignation par son ID."""
    current_user_id = int(get_jwt_identity())
    
    # Utiliser le service
    service = AssignmentService()
    assignment = service.get_assignment(assignment_id, current_user_id)
    
    return assignment

@bp.put('/assignments/<int:assignment_id>')
@jwt_required()
def update_assignment(assignment_id):
    """Mettre à jour une assignation (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Utiliser le service
    service = AssignmentService()
    assignment = service.update_assignment(
        assignment_id=assignment_id,
        current_user_id=current_user_id,
        is_read=data.get("is_read"),
        user_id=data.get("user_id")
    )
    
    # Log de modification d'assignation
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="assignment_updated",
        target_id=assignment["id"],
        payload=json.dumps({"note_id": assignment["note_id"], "user_id": assignment["user_id"]})
    )
    db.session.add(action_log)
    db.session.commit()
    
    return assignment

@bp.delete('/assignments/<int:assignment_id>')
@jwt_required()
def delete_assignment(assignment_id):
    """Supprimer une assignation (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    
    # Utiliser le service
    service = AssignmentService()
    assignment = service.delete_assignment(assignment_id, current_user_id)
    
    # Log de suppression d'assignation
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="assignment_deleted",
        target_id=assignment_id,
        payload=json.dumps({"note_id": assignment["note_id"], "assigned_user_id": assignment["user_id"]})
    )
    db.session.add(action_log)
    db.session.commit()
    
    return {"deleted": True}

@bp.put('/assignments/<int:assignment_id>/priority')
@jwt_required()
def toggle_priority(assignment_id):
    """Basculer la priorité personnelle du destinataire (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    
    # Utiliser le service
    service = AssignmentService()
    assignment = service.toggle_priority(assignment_id, current_user_id)
    
    # Log de modification de priorité
    action_log = ActionLog(
        user_id=current_user_id,
        action_type="assignment_priority_updated",
        target_id=assignment["id"],
        payload=json.dumps({"priority": assignment["recipient_priority"]})
    )
    db.session.add(action_log)
    db.session.commit()
    
    return assignment

@bp.put('/assignments/<int:assignment_id>/status')
@jwt_required()
def update_status(assignment_id):
    """Modifier le statut personnel du destinataire (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or "recipient_status" not in data:
        abort(400, description="Missing recipient_status")
    
    # Récupérer l'ancien statut pour le log
    assignment_obj = Assignment.query.get_or_404(assignment_id)
    old_status = assignment_obj.recipient_status
    new_status = data["recipient_status"]
    
    # Utiliser le service
    service = AssignmentService()
    assignment = service.update_status(assignment_id, current_user_id, new_status)
    
    # Log de modification de statut avec type spécifique
    if old_status != new_status:
        if new_status == "terminé":
            action_type = "assignment_completed"
        else:
            action_type = "assignment_uncompleted"
        
        action_log = ActionLog(
            user_id=current_user_id,
            action_type=action_type,
            target_id=assignment["id"],
            payload=json.dumps({
                "status": new_status,
                "note_id": assignment["note_id"],
                "user_id": assignment["user_id"]
            })
        )
        db.session.add(action_log)
        db.session.commit()
    
    return assignment

@bp.get('/assignments/unread')
@jwt_required()
def get_unread_assignments():
    """Récupérer les assignations non lues de l'utilisateur connecté (authentification requise)."""
    current_user_id = int(get_jwt_identity())
    
    # Utiliser le service
    service = AssignmentService()
    unread_assignments = service.get_unread_assignments(current_user_id)
    
    return {
        "count": len(unread_assignments),
        "assignments": unread_assignments
    }
