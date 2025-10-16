"""
Modèle pour les utilisateurs.
"""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
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
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user' ou 'admin'
    created_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Ajout de la relation avec les contacts
    # Les relations sont configurées dans les autres modèles (Assignment, Note, Contact)
    contacts = db.relationship('Contact', foreign_keys='Contact.user_id', back_populates='user')

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"

    # méthodes de validation SQAlchemy
    @validates('username')
    def validate_username(self, key, username):
        """Valide que le username n'est pas vide et respecte les contraintes."""
        if not username or not username.strip():
            raise ValueError("Le nom d'utilisateur ne peut pas être vide")
        if len(username.strip()) < 2:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 2 caractères")
        if len(username) > 80:
            raise ValueError("Le nom d'utilisateur ne peut pas dépasser 80 caractères")
        return username.strip()

    @validates('email')
    def validate_email(self, key, email):
        """Valide que l'email n'est pas vide et a un format basique."""
        if not email or not email.strip():
            raise ValueError("L'email ne peut pas être vide")
        email = email.strip().lower()
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValueError("Format d'email invalide")
        if len(email) > 120:
            raise ValueError("L'email ne peut pas dépasser 120 caractères")
        return email

    @validates('password_hash')
    def validate_password_hash(self, key, password_hash):
        """Valide que le hash du mot de passe n'est pas vide."""
        if not password_hash or not password_hash.strip():
            raise ValueError("Le mot de passe ne peut pas être vide")
        return password_hash

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_date": self.created_date.isoformat() if self.created_date else None,
        }

    # gestion mdp
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Vérifie si l'utilisateur est un administrateur."""
        return self.role == 'admin'
