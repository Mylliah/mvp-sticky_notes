"""
Routes pour la consultation des logs d'actions (admin uniquement, lecture seule).

Les logs sont créés automatiquement par le système lors des actions utilisateurs.
Aucune création/modification/suppression manuelle n'est permise pour garantir l'intégrité de l'audit.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ... import db
from ...models import ActionLog
from ...decorators import admin_required

bp = Blueprint('action_logs', __name__)

# NOTE: Pas de route POST/PUT/DELETE - Les logs sont IMMUABLES et créés automatiquement
# par le système lors des actions (auth, notes, contacts, assignments, etc.)

@bp.get('/action_logs')
@jwt_required()
@admin_required()
def list_action_logs():
    """Lister tous les logs d'actions (admin uniquement)."""
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
@jwt_required()
@admin_required()
def get_action_log(log_id):
    """Récupérer un log d'action par son ID (admin uniquement)."""
    action_log = ActionLog.query.get_or_404(log_id)
    return action_log.to_dict()

# NOTE: Route DELETE supprimée volontairement pour garantir l'immuabilité des logs (traçabilité)
# Les logs d'actions doivent être conservés pour l'audit et ne peuvent pas être supprimés

@bp.get('/action_logs/stats')
@jwt_required()
@admin_required()
def get_action_log_stats():
    """Récupérer des statistiques sur les actions (admin uniquement)."""
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
