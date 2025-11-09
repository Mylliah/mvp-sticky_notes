"""
Services pour la logique métier de l'application.
"""
from .note_service import NoteService
from .auth_service import AuthService
from .contact_service import ContactService
from .assignment_service import AssignmentService
from .user_service import UserService

__all__ = ['NoteService', 'AuthService', 'ContactService', 'AssignmentService', 'UserService']
