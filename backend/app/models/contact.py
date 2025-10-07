"""
Modèle pour les contacts.
"""
from datetime import datetime
from .. import db

class Contact(db.Model):
    """
    But : permettre à chaque utilisateur de gérer ses contacts pour l'attribution des notes, gestion des surnoms, d'actions ou permissions
    """
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    nickname = db.Column(db.String(80), nullable=False)
    contact_action = db.Column(db.String(80))
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Permet d'accéder à l'utilisateur propriétaire du carnet de contacts (contact.user)
    # et côté utilisateur, récupérer tous ses contacts (user.contacts)
    # user = propriétaire du carnet de contacts
    # contact_user = concerne le contact ajouté
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('contacts', lazy=True))
    contact_user = db.relationship('User', foreign_keys=[contact_user_id])

    def __repr__(self):
        """Représentation textuelle de l'objet Contact pour le débogage.
        Returns: str: Chaîne représentant l'instance Contact avec son ID et nom.
        """
        return f"<Contact id={self.id} nickname={self.nickname!r}>"

    def to_dict(self):
        """
        Convertit l'instance Contact en dictionnaire pour la sérialisation JSON.
        Returns: dict: Dictionnaire contenant les données du contact (id, user_id, name, email, phone, created_at).
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contact_user_id": self.contact_user_id,
            "nickname": self.nickname,
            "contact_action": self.contact_action,
            "created_date": self.created_date.isoformat() if self.created_date else None,
        }