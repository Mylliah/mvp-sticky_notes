"""
Couche Repository : Accès aux données.
Cette couche encapsule toutes les requêtes SQLAlchemy.
"""
from .note_repository import NoteRepository
from .assignment_repository import AssignmentRepository
from .user_repository import UserRepository
from .contact_repository import ContactRepository
from .action_log_repository import ActionLogRepository

__all__ = [
    'NoteRepository',
    'AssignmentRepository',
    'UserRepository',
    'ContactRepository',
    'ActionLogRepository',
]
