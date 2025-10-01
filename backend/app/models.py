# backend/app/models.py
from datetime import datetime
from . import db  # 'db' vient de app/__init__.py

class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Note id={self.id} title={self.title!r}>"
