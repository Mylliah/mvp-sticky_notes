"""
Repository pour l'accès aux données des logs d'actions.
Encapsule toutes les requêtes SQLAlchemy liées aux action logs.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import func
from .. import db
from ..models import ActionLog


class ActionLogRepository:
    """Gestion de l'accès aux données pour les action logs."""
    
    def find_by_id(self, log_id: int) -> Optional[ActionLog]:
        """
        Récupérer un log par son ID.
        
        Args:
            log_id: ID du log
            
        Returns:
            ActionLog ou None si non trouvé
        """
        return ActionLog.query.get(log_id)
    
    def find_all(self, page: int = 1, per_page: int = 50) -> Any:
        """
        Récupérer tous les logs avec pagination.
        
        Args:
            page: Numéro de page (défaut: 1)
            per_page: Nombre d'items par page (défaut: 50)
            
        Returns:
            Objet Pagination de SQLAlchemy
        """
        return ActionLog.query.order_by(
            ActionLog.timestamp.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    def find_by_user(self, user_id: int, page: int = 1, per_page: int = 50) -> Any:
        """
        Récupérer les logs d'un utilisateur avec pagination.
        
        Args:
            user_id: ID de l'utilisateur
            page: Numéro de page
            per_page: Nombre d'items par page
            
        Returns:
            Objet Pagination de SQLAlchemy
        """
        return ActionLog.query.filter_by(user_id=user_id).order_by(
            ActionLog.timestamp.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    def find_by_action_type(self, action_type: str, page: int = 1, per_page: int = 50) -> Any:
        """
        Récupérer les logs par type d'action avec pagination.
        
        Args:
            action_type: Type d'action
            page: Numéro de page
            per_page: Nombre d'items par page
            
        Returns:
            Objet Pagination de SQLAlchemy
        """
        return ActionLog.query.filter_by(action_type=action_type).order_by(
            ActionLog.timestamp.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupérer les statistiques globales des logs.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        total_actions = ActionLog.query.count()
        
        # Compter par type d'action
        action_counts = db.session.query(
            ActionLog.action_type,
            func.count(ActionLog.id).label('count')
        ).group_by(ActionLog.action_type).all()
        
        actions_by_type = {
            action_type: count 
            for action_type, count in action_counts
        }
        
        # Compter les utilisateurs actifs
        active_users = db.session.query(
            func.count(func.distinct(ActionLog.user_id))
        ).scalar()
        
        return {
            "total_actions": total_actions,
            "actions_by_type": actions_by_type,
            "active_users": active_users
        }
    
    def save(self, action_log: ActionLog) -> ActionLog:
        """
        Sauvegarder un log d'action.
        
        Args:
            action_log: Instance d'ActionLog à sauvegarder
            
        Returns:
            ActionLog sauvegardé avec ID généré
        """
        db.session.add(action_log)
        db.session.commit()
        db.session.refresh(action_log)
        return action_log
