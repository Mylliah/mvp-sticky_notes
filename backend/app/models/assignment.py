"""
Modèle pour les assignations de notes aux utilisateurs.
"""
from datetime import datetime
from .. import db

class Assignment(db.Model):
    """
    But : attribuer une note à un utilisateur précis, suivre la date d'attribution et la lecture
    """
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # Permet d'accéder directement à l'objet User ou Note depuis une instance d'Assignment (ex : assignment.user)
    # et réciproquement (ex : user.assignments récupère toutes les attributions d'un utilisateur)
    user = db.relationship('User', backref=db.backref('assignments', lazy=True)) 
    note = db.relationship('Note', backref=db.backref('assignments', lazy=True))

    def __repr__(self):
        """Représentation textuelle de l'objet Assignment pour le débogage.
        Returns: str: Chaîne représentant l'instance Assignment avec son ID, user_id et note_id.
        """
        return f"<Assignment id={self.id} user_id={self.user_id} note_id={self.note_id}>"

    def to_dict(self):
        """
        Convertit l'instance Assignment en dictionnaire pour la sérialisation JSON.
        Returns: dict: Dictionnaire contenant les données de l'attribution (id, user_id, note_id, assigned_at).
        """
        return {
            "id": self.id,
            "note_id": self.note_id,
            "user_id": self.user_id,
            "assigned_date": self.assigned_date.isoformat() if self.assigned_date else None,
            "is_read": self.is_read,
        }