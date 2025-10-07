"""
Modèle pour les utilisateurs.
"""
from datetime import datetime
from .. import db

class User(db.Model):
    """
    But : stocker les informations d'identification et de connexion du système ; 
    sert de référence (clé étrangère) pour notes, contacts, attributions, logs
    """
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        """Représentation textuelle de l'objet User pour le débogage.
        Returns: str: Chaîne représentant l'instance User avec son ID et nom d'utilisateur.
        """
        return f"<User id={self.id} username={self.username!r}>"

    def to_dict(self):
        """
        Convertit l'instance User en dictionnaire pour la sérialisation JSON.
        Returns: dict: Dictionnaire contenant les données de l'utilisateur (id, username, email, created_at).
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }