"""
Modèle pour les journaux d'actions.
"""
from datetime import datetime, timezone
from .. import db

class ActionLog(db.Model):
    """
    But : journaliser les actions effectuées par les utilisateurs pour l'audit et le suivi.
    """
    __tablename__ = "action_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    target_id = db.Column(db.Integer, nullable=False)  # id d'entité concernée
    action_type = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    payload = db.Column(db.String(255))  # détails supplémentaires sur l'action/JSON

    # Donne accès à l'utilisateur qui a généré une action/journal
    # et permet d'obtenir tous les logs d'un utilisateur facilement (user.action_logs)
    user = db.relationship('User', backref=db.backref('action_logs', lazy=True))

    def __repr__(self):
        """Représentation textuelle de l'objet ActionLog pour le débogage.
        Returns: str: Chaîne représentant l'instance ActionLog avec son ID, user_id et action_type.
        """
        return f"<ActionLog id={self.id} user_id={self.user_id} action_type={self.action_type!r}>"

    def to_dict(self):
        """
        Convertit l'instance ActionLog en dictionnaire pour la sérialisation JSON.
        Returns: dict: Dictionnaire contenant les données du journal d'action (id, user_id, action_type, action_details, timestamp).
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_id": self.target_id,
            "action_type": self.action_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "payload": self.payload,
        }
