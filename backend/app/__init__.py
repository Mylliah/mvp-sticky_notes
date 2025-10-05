"""
Module d'initialisation de l'application Flask pour le projet MVP Sticky Notes.
Ce module contient la factory function pour créer l'instance de l'app Flask.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request, abort

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """
    Factory function pour créer et configurer l'app Flask.
    Returns: Flask: Instance configurée de l'app Flask avec les routes de base.
    """
    app = Flask(__name__)

    # config DB : lit DATABASE_URL (sinon valeur par défaut vers le service 'db')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app:app@db:5432/appdb",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # branche SQLAlchemy + Alembic/Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from .models import ActionLog, Assignment, Contact, Note, User

    @app.get("/health") # vérifie que l'API répond
    def health():
        return {"status": "ok"}

    # ============= CRUD basique pour les notes =============

    @app.post("/notes")  # endpoint pour créer une note
    def create_note():
        data = request.get_json()
        if not data or not data.get("content"):
            abort(400, description="Missing content")
        note = Note(content=data["content"], creator_id=data.get("creator_id"))
        db.session.add(note)
        db.session.commit()
        return note.to_dict(), 201
    
    @app.get("/notes/<int:note_id>")
    def get_note(note_id):
        note = Note.query.get_or_404(note_id)
        return note.to_dict()

    @app.put("/notes/<int:note_id>")
    def update_note(note_id):
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        if not data or "content" not in data:
            abort(400, description="Missing content")
        note.content = data["content"]
        db.session.commit()
        return note.to_dict()

    @app.delete("/notes/<int:note_id>")
    def delete_note(note_id):
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return {"deleted": True}
    
    # ============= CRUD basique pour les utilisateurs =============

    @app.post("/users")
    def create_user():
        data = request.get_json()
        if not data or not data.get("username") or not data.get("email") or not data.get("password_hash"):
            abort(400, description="Missing data")
        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"]
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201

    @app.get("/users/<int:user_id>")
    def get_user(user_id):
        user = User.query.get_or_404(user_id)
        return user.to_dict()

    @app.put("/users/<int:user_id>")
    def update_user(user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        if "username" in data:
            user.username = data["username"]
        if "email" in data:
            user.email = data["email"]
        if "password_hash" in data:
            user.password_hash = data["password_hash"]
        db.session.commit()
        return user.to_dict()

    @app.delete("/users/<int:user_id>")
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"deleted": True}
    
    # ============= CRUD basique pour les attributions =============

    @app.post("/assignments")
    def create_assignment():
        data = request.get_json()
        if not data or not data.get("note_id") or not data.get("user_id"):
            abort(400, description="Missing data")
        assignment = Assignment(
            note_id=data["note_id"],
            user_id=data["user_id"],
            is_read=data.get("is_read", False)
        )
        db.session.add(assignment)
        db.session.commit()
        return assignment.to_dict(), 201

    @app.get("/assignments/<int:assignment_id>")
    def get_assignment(assignment_id):
        assignment = Assignment.query.get_or_404(assignment_id)
        return assignment.to_dict()

    @app.put("/assignments/<int:assignment_id>")
    def update_assignment(assignment_id):
        assignment = Assignment.query.get_or_404(assignment_id)
        data = request.get_json()
        if "is_read" in data:
            assignment.is_read = data["is_read"]
        db.session.commit()
        return assignment.to_dict()

    @app.delete("/assignments/<int:assignment_id>")
    def delete_assignment(assignment_id):
        assignment = Assignment.query.get_or_404(assignment_id)
        db.session.delete(assignment)
        db.session.commit()
        return {"deleted": True}
    
    # ============= CRUD basique pour la liste de contacts =============

    @app.post("/contacts")
    def create_contact():
        data = request.get_json()
        if not data or not data.get("user_id") or not data.get("contact_user_id") or not data.get("nickname"):
            abort(400, description="Missing data")
        contact = Contact(
            user_id=data["user_id"],
            contact_user_id=data["contact_user_id"],
            nickname=data["nickname"],
            contact_action=data.get("contact_action")
        )
        db.session.add(contact)
        db.session.commit()
        return contact.to_dict(), 201

    @app.get("/contacts/<int:contact_id>")
    def get_contact(contact_id):
        contact = Contact.query.get_or_404(contact_id)
        return contact.to_dict()

    @app.put("/contacts/<int:contact_id>")
    def update_contact(contact_id):
        contact = Contact.query.get_or_404(contact_id)
        data = request.get_json()
        if "nickname" in data:
            contact.nickname = data["nickname"]
        if "contact_action" in data:
            contact.contact_action = data["contact_action"]
        db.session.commit()
        return contact.to_dict()

    @app.delete("/contacts/<int:contact_id>")
    def delete_contact(contact_id):
        contact = Contact.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        return {"deleted": True}
    
    # ============= CRUD basique pour les logs d'actions =============

    @app.post("/action_logs")
    def create_action_log():
        data = request.get_json()
        if not data or not data.get("user_id") or not data.get("target_id") or not data.get("action_type"):
            abort(400, description="Missing data")
        log = ActionLog(
            user_id=data["user_id"],
            target_id=data["target_id"],
            action_type=data["action_type"],
            payload=data.get("payload")
        )
        db.session.add(log)
        db.session.commit()
        return log.to_dict(), 201

    @app.get("/action_logs/<int:log_id>")
    def get_action_log(log_id):
        log = ActionLog.query.get_or_404(log_id)
        return log.to_dict()

    @app.put("/action_logs/<int:log_id>")
    def update_action_log(log_id):
        log = ActionLog.query.get_or_404(log_id)
        data = request.get_json()
        if "payload" in data:
            log.payload = data["payload"]
        db.session.commit()
        return log.to_dict()

    @app.delete("/action_logs/<int:log_id>")
    def delete_action_log(log_id):
        log = ActionLog.query.get_or_404(log_id)
        db.session.delete(log)
        db.session.commit()
        return {"deleted": True}
    
    # import provisoire des modèles ici "from . import models (models.py)"
    from . import models
    from flask import jsonify
    
    @app.get("/notes")
    def list_notes():
        notes = models.Note.query.order_by(models.Note.id.asc()).all()
        return jsonify([n.to_dict() for n in notes])
    
    @app.get("/users")
    def list_users():
        users = models.User.query.order_by(models.User.id.asc()).all()
        return jsonify([u.to_dict() for u in users])

    return app
