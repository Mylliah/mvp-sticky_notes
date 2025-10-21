"""
Module d'initialisation pour les modèles de données.
Centralise l'import de tous les modèles pour faciliter leur utilisation.
"""

from .note import Note
from .user import User
from .assignment import Assignment
from .contact import Contact
from .action_log import ActionLog

# Export de tous les modèles pour faciliter l'import
__all__ = ['Note', 'User', 'Assignment', 'Contact', 'ActionLog']