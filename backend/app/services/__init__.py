"""
Couche Service : Logique métier.
Cette couche contient toute la logique métier de l'application.
"""
from .note_service import NoteService
from .auth_service import AuthService

__all__ = [
    'NoteService',
    'AuthService',
]
