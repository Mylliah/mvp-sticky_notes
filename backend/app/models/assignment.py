"""
Modèle pour les assignations de notes aux utilisateurs.
"""
from datetime import datetime, timezone
from .. import db

class Assignment(db.Model):
    """
    Attribution d'une note à un utilisateur précis,
    suivi de la date et du statut de lecture.
    """
    __tablename__ = "assignments"
    __table_args__ = (
        db.UniqueConstraint('note_id', 'user_id', name='uq_note_user'),
    )

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)
    recipient_priority = db.Column(db.Boolean, default=False)
    recipient_status = db.Column(db.String(20), nullable=False, default='en_cours')  # 'en_cours' ou 'terminé'
    finished_date = db.Column(db.DateTime)  # Date où le destinataire a marqué comme terminé

    # Relations 
    user = db.relationship('User', backref=db.backref('assignments', lazy=True)) 
    note = db.relationship('Note', back_populates='assignments')

    def __repr__(self):
        return f"<Assignment id={self.id} user_id={self.user_id} note_id={self.note_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "note_id": self.note_id,
            "user_id": self.user_id,
            "assigned_date": self.assigned_date.isoformat() if self.assigned_date else None,
            "is_read": self.is_read,
            "recipient_priority": self.recipient_priority,
            "recipient_status": self.recipient_status,
            "finished_date": self.finished_date.isoformat() if self.finished_date else None,
        }
