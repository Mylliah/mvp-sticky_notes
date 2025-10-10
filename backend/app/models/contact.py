"""
Modèle pour les contacts.
"""
from datetime import datetime
from .. import db

class Contact(db.Model):
    """
    Gestion du carnet de contacts d'un utilisateur.
    """
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)            # propriétaire du carnet
    contact_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)    # personne ajoutée
    nickname = db.Column(db.String(80), nullable=False)
    contact_action = db.Column(db.String(80))
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relations pour accès rapide à l'objet User (propriétaire et contact)
    user = db.relationship('User', foreign_keys=[user_id], back_populates='contacts')
    contact_user = db.relationship('User', foreign_keys=[contact_user_id])

    def __repr__(self):
        return f"<Contact id={self.id} nickname={self.nickname!r}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contact_user_id": self.contact_user_id,
            "nickname": self.nickname,
            "contact_action": self.contact_action,
            "created_date": self.created_date.isoformat() if self.created_date else None,
        }
