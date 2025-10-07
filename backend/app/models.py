# backend/app/models.py
from datetime import datetime
from . import db  # 'db' vient de app/__init__.py

class Note(db.Model):
    """
    But : représ    target_id = db.Column(db.Integer, nullable=False)  # id d'entité concernée
    action_type = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payload = db.Column(db.String(255))  # détails supplémentaires sur l'action/JSONr une note (titre et date de création) stockée dans la table "notes".
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

class User(db.Model):
    """
    But : stocker les informations d’identification et de connexion du système ; 
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
    
class Assignment(db.Model):
    """
    But : attribuer une note à un utilisateur précis, suivre la date d’attribution et la lecture
    """
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # Permet d’accéder directement à l’objet User ou Note depuis une instance d’Assignment (ex : assignment.user)
    # et réciproquement (ex : user.assignments récupère toutes les attributions d’un utilisateur)
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

class Contact(db.Model):
    """
    But : permettre à chaque utilisateur de gérer ses contacts pour l’attribution des notes, gestion des surnoms, d’actions ou permissions
    """
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    nickname = db.Column(db.String(80), nullable=False)
    contact_action = db.Column(db.String(80))
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Permet d’accéder à l’utilisateur propriétaire du carnet de contacts (contact.user)
    # et côté utilisateur, récupérer tous ses contacts (user.contacts)
    # user = propriétaire du carnet de contacts
    # contact_user = concerne le contact ajouté
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('contacts', lazy=True))
    contact_user = db.relationship('User', foreign_keys=[contact_user_id])

    def __repr__(self):
        """Représentation textuelle de l'objet Contact pour le débogage.
        Returns: str: Chaîne représentant l'instance Contact avec son ID et nom.
        """
        return f"<Contact id={self.id} name={self.name!r}>"

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

class ActionLog(db.Model):
    """
    But : journaliser les actions effectuées par les utilisateurs pour l'audit et le suivi.
    """
    __tablename__ = "action_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)  # id d’entité concernée
    action_type = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    playload = db.Column(db.String(255))  # détails supplémentaires sur l’action/JSON

    # Donne accès à l’utilisateur qui a généré une action/journal
    # et permet d’obtenir tous les logs d’un utilisateur facilement (user.action_logs)
    user = db.relationship('User', backref=db.backref('action_logs', lazy=True))

    def __repr__(self):
        """Représentation textuelle de l'objet ActionLog pour le débogage.
        Returns: str: Chaîne représentant l'instance ActionLog avec son ID, user_id et action_type.
        """
        return f"<ActionLog id={self.id} user_id={self.user_id} action_type={self.action_type!r}>"

    def to_dict(self):
        """
        Convertit l'instance ActionLog en dictionnaire pour la sérialisation JSON.
        Returns: dict: Dictionnaire contenant les données du journal d'action (id, user_id, action_type, action_details, timestamp).
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_id": self.target_id,
            "action_type": self.action_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "payload": self.payload,
        }
    