"""
Modèle pour les notes.
"""
from datetime import datetime
from .. import db

class Note(db.Model):
    """
    But : représenter une note (titre et date de création) stockée dans la table "notes".
    """
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Permet à un utilisateur d'accéder à toutes ses notes via (ex : user.notes)
    # et à une note d'accéder à son créateur via (ex : note.creator)
    creator = db.relationship('User', backref=db.backref('notes', lazy=True))

    def __repr__(self):
        """Représentation textuelle de l'objet Note pour le débogage.
        Returns: str: Chaîne représentant l'instance Note avec son ID et contenu.
        """
        return f"<Note id={self.id} content={self.content[:30]!r}>"

    def to_dict(self):
        """
        Convertit l'instance Note en dictionnaire pour la sérialisation JSON.
        Returns: dict: Dictionnaire contenant les données de la note (id, content, created_at).
        """
        return {
            "id": self.id,
            "content": self.content,
            "create_date": self.created_date.isoformat() if self.created_date else None,
        }