"""
Routes pour la gestion des logs d'actions.
"""
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from ... import db
from ...models import ActionLog, User

bp = Blueprint('action_logs', __name__)

@bp.post('/action_logs')
def create_action_log():
    """Créer un nouveau log d'action."""
    data = request.get_json()
    if not data or not data.get("user_id") or not data.get("action_type"):
        abort(400, description="Missing user_id or action_type")
        
    # Vérifier que l'utilisateur existe
    # Utiliser Session.get() (db.session.get) pour éviter l'API dépréciée Query.get()
    user = db.session.get(User, data["user_id"])
    if not user:
        abort(400, description="User not found")
    
    # target_id est obligatoire
    if not data.get("target_id"):
        abort(400, description="Missing target_id")
        
    action_log = ActionLog(
        user_id=data["user_id"],
        action_type=data["action_type"],
        target_id=data["target_id"],
        payload=data.get("payload"),
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(action_log)
    db.session.commit()
    return action_log.to_dict(), 201

@bp.get('/action_logs')
def list_action_logs():
    """Lister tous les logs d'actions."""
    # Pagination pour éviter de surcharger
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Filtres optionnels
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type')
    
    query = ActionLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action_type:
        query = query.filter_by(action_type=action_type)
        
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

@bp.get('/action_logs/<int:log_id>')
def get_action_log(log_id):
    """Récupérer un log d'action par son ID."""
    action_log = ActionLog.query.get_or_404(log_id)
    return action_log.to_dict()

@bp.delete('/action_logs/<int:log_id>')
def delete_action_log(log_id):
    """Supprimer un log d'action."""
    action_log = ActionLog.query.get_or_404(log_id)
    db.session.delete(action_log)
    db.session.commit()
    return {"deleted": True}

@bp.get('/action_logs/stats')
def get_action_log_stats():
    """Récupérer des statistiques sur les actions."""
    from sqlalchemy import func
    
    # Compter les actions par type
    action_counts = db.session.query(
        ActionLog.action_type,
        func.count(ActionLog.id).label('count')
    ).group_by(ActionLog.action_type).all()
    
    # Compter les actions par utilisateur
    user_counts = db.session.query(
        ActionLog.user_id,
        func.count(ActionLog.id).label('count')
    ).group_by(ActionLog.user_id).all()
    
    return {
        "action_counts": [{"action_type": action_type, "count": count} for action_type, count in action_counts],
        "user_counts": [{"user_id": user_id, "count": count} for user_id, count in user_counts]
    }