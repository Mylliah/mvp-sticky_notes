"""
Modèle pour les utilisateurs.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(db.Model):
    """
    Stockage des informations utilisateur pour identification, contacts, etc.
    """
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Augmenté de 128 à 255 car erreur mdp trop long
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relations
    # Les relations sont configurées dans les autres modèles (Assignment, Note, Contact)
    # Ajout de la relation avec les contacts
    contacts = db.relationship('Contact', foreign_keys='Contact.user_id', back_populates='user')

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_date": self.created_at.isoformat() if self.created_at else None,
        }

    # gestion mdp
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
