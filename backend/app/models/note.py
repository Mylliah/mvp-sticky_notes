"""
Modèle pour les notes.
"""
from datetime import datetime, timezone
from .. import db

class Note(db.Model):
    """
    Représente une note stockée dans la table "notes"
    """
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    update_date = db.Column(db.DateTime)
    delete_date = db.Column(db.DateTime)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # QUI a supprimé (créateur ou destinataire)
    read_date = db.Column(db.DateTime)
    # finished_date et status SUPPRIMÉS : ambigus pour multi-destinataires
    # Utiliser Assignment.recipient_status et Assignment.finished_date à la place
    important = db.Column(db.Boolean, default=False)

    # Relations (foreign_keys spécifié explicitement car 2 FK vers User: creator_id et deleted_by)
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_notes')
    deleter = db.relationship('User', foreign_keys=[deleted_by], backref='deleted_notes')
    assignments = db.relationship('Assignment', back_populates='note', lazy=True)

    def __repr__(self):
        """Représentation textuelle pour le débogage."""
        return f"<Note id={self.id} important={self.important} content={self.content[:30]!r}>"

    def to_dict(self):
        """Conversion en dict pour API"""
        return {
            "id": self.id,
            "content": self.content,
            "important": self.important,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "update_date": self.update_date.isoformat() if self.update_date else None,
            "delete_date": self.delete_date.isoformat() if self.delete_date else None,
            "read_date": self.read_date.isoformat() if self.read_date else None,
            "creator_id": self.creator_id,
        }

    def to_details_dict(self, assignment=None):
        """Conversion pour le bloc détails (inclut deleted_by pour traçabilité)"""
        return {
            "id": self.id,
            "assigned_to": assignment.user_id if assignment else None,
            "assigned_date": assignment.assigned_date.isoformat() if assignment else None,
            "important": self.important,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "update_date": self.update_date.isoformat() if self.update_date else None,
            "delete_date": self.delete_date.isoformat() if self.delete_date else None,
            "deleted_by": self.deleted_by,  # Traçabilité : QUI a supprimé (créateur ou destinataire)
            "read_date": self.read_date.isoformat() if self.read_date else None,
        }

    def to_summary_dict(self, current_user_id=None):
        """Conversion pour vignette"""
        assigned_users = [a.user for a in self.assignments if a.user]
        assigned_usernames = [u.username for u in assigned_users]
        creator_contacts = self.creator.contacts if self.creator else []
        contact_usernames = list(set([c.contact_user.username for c in creator_contacts]))
        if set(assigned_usernames) == set(contact_usernames):
            if current_user_id and self.creator.id == current_user_id:
                assigned_display = "à All + moi"
            else:
                assigned_display = "à All"
        else:
            if len(assigned_usernames) > 3:
                assigned_display = ", ".join(assigned_usernames[:3]) + "..."
            else:
                assigned_display = ", ".join(assigned_usernames)
        return {
            "id": self.id,
            "important": self.important,
            "preview": self.content[:30] + "..." if len(self.content) > 30 else self.content,
            "creator": self.creator.username if self.creator else None,
            "assigned_display": assigned_display,
            "created_date": self.created_date.isoformat() if self.created_date else None,
        }
