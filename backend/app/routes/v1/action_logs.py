"""
Routes pour la gestion des logs d'actions.
"""
from flask import Blueprint, request, abort
from datetime import datetime
from ... import db
from ...models import ActionLog, User

bp = Blueprint('action_logs', __name__, url_prefix='/action_logs')

@bp.post('')
def create_action_log():
    """Créer un nouveau log d'action."""
    data = request.get_json()
    if not data or not data.get("user_id") or not data.get("action"):
        abort(400, description="Missing user_id or action")
        
    # Vérifier que l'utilisateur existe
    user = User.query.get(data["user_id"])
    if not user:
        abort(400, description="User not found")
        
    action_log = ActionLog(
        user_id=data["user_id"],
        action=data["action"],
        entity_type=data.get("entity_type"),
        entity_id=data.get("entity_id"),
        details=data.get("details"),
        timestamp=datetime.utcnow()
    )
    db.session.add(action_log)
    db.session.commit()
    return action_log.to_dict(), 201

@bp.get('')
def list_action_logs():
    """Lister tous les logs d'actions."""
    # Pagination pour éviter de surcharger
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Filtres optionnels
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    entity_type = request.args.get('entity_type')
    
    query = ActionLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action:
        query = query.filter_by(action=action)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
        
    logs = query.order_by(ActionLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return {
        "logs": [log.to_dict() for log in logs.items],
        "total": logs.total,
        "page": page,
        "per_page": per_page,
        "pages": logs.pages
    }

@bp.get('/<int:log_id>')
def get_action_log(log_id):
    """Récupérer un log d'action par son ID."""
    action_log = ActionLog.query.get_or_404(log_id)
    return action_log.to_dict()

@bp.delete('/<int:log_id>')
def delete_action_log(log_id):
    """Supprimer un log d'action."""
    action_log = ActionLog.query.get_or_404(log_id)
    db.session.delete(action_log)
    db.session.commit()
    return {"deleted": True}

@bp.get('/stats')
def get_action_stats():
    """Récupérer des statistiques sur les actions."""
    from sqlalchemy import func
    
    # Compter les actions par type
    action_counts = db.session.query(
        ActionLog.action,
        func.count(ActionLog.id).label('count')
    ).group_by(ActionLog.action).all()
    
    # Compter les actions par utilisateur
    user_counts = db.session.query(
        ActionLog.user_id,
        func.count(ActionLog.id).label('count')
    ).group_by(ActionLog.user_id).all()
    
    return {
        "action_counts": [{"action": action, "count": count} for action, count in action_counts],
        "user_counts": [{"user_id": user_id, "count": count} for user_id, count in user_counts]
    }