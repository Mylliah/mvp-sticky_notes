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
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relation contacts (carnet du propriétaire)
    contacts = db.relationship('Contact', backref='owner', lazy=True)
    # Les autres relations sont configurées dans Assignment et Note

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    # gestion mdp
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
