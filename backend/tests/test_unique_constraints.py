"""
Tests pour les contraintes UNIQUE en base de données.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from app.models import User, Contact, Assignment, Note
from app import db


class TestContactUniqueConstraint:
    """Tests pour la contrainte UNIQUE sur Contact (user_id, contact_user_id)."""
    
    def test_cannot_add_same_contact_twice(self, app):
        """On ne peut pas ajouter deux fois le même contact."""
        # Créer 2 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice ajoute Bob
        contact1 = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact1)
        db.session.commit()
        
        # Alice essaie de re-ajouter Bob
        contact2 = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob Again")
        db.session.add(contact2)
        
        # Devrait lever IntegrityError à cause de la contrainte UNIQUE
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()
    
    def test_can_add_reciprocal_contacts(self, app):
        """On peut ajouter des contacts réciproques (Alice->Bob et Bob->Alice)."""
        # Créer 2 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice ajoute Bob
        contact1 = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact1)
        db.session.commit()
        
        # Bob ajoute Alice (inverse, donc OK)
        contact2 = Contact(user_id=user2.id, contact_user_id=user1.id, nickname="Alice")
        db.session.add(contact2)
        db.session.commit()
        
        # Les deux devraient exister
        assert Contact.query.count() == 2
    
    def test_can_add_different_contacts_for_same_user(self, app):
        """Un utilisateur peut avoir plusieurs contacts différents."""
        # Créer 3 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        user3 = User(username="charlie", email="charlie@test.com", password_hash="hash3")
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        # Alice ajoute Bob
        contact1 = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact1)
        db.session.commit()
        
        # Alice ajoute Charlie (différent de Bob, donc OK)
        contact2 = Contact(user_id=user1.id, contact_user_id=user3.id, nickname="Charlie")
        db.session.add(contact2)
        db.session.commit()
        
        # Les deux devraient exister
        assert Contact.query.filter_by(user_id=user1.id).count() == 2


class TestAssignmentUniqueConstraint:
    """Tests pour la contrainte UNIQUE sur Assignment (note_id, user_id)."""
    
    def test_cannot_assign_same_note_to_user_twice(self, app):
        """On ne peut pas assigner deux fois la même note au même utilisateur."""
        # Créer un utilisateur
        user = User(username="alice", email="alice@test.com", password_hash="hash1")
        db.session.add(user)
        db.session.commit()
        
        # Créer une note
        note = Note(content="Test note", creator_id=user.id)
        db.session.add(note)
        db.session.commit()
        
        # Première assignation
        assignment1 = Assignment(note_id=note.id, user_id=user.id, is_read=False)
        db.session.add(assignment1)
        db.session.commit()
        
        # Deuxième assignation (doublon)
        assignment2 = Assignment(note_id=note.id, user_id=user.id, is_read=True)
        db.session.add(assignment2)
        
        # Devrait lever IntegrityError à cause de la contrainte UNIQUE
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()
    
    def test_can_assign_same_note_to_different_users(self, app):
        """On peut assigner la même note à plusieurs utilisateurs différents."""
        # Créer 2 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Créer une note
        note = Note(content="Test note", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Assigner à Alice
        assignment1 = Assignment(note_id=note.id, user_id=user1.id)
        db.session.add(assignment1)
        db.session.commit()
        
        # Assigner à Bob (différent utilisateur, donc OK)
        assignment2 = Assignment(note_id=note.id, user_id=user2.id)
        db.session.add(assignment2)
        db.session.commit()
        
        # Les deux devraient exister
        assert Assignment.query.filter_by(note_id=note.id).count() == 2
    
    def test_can_assign_different_notes_to_same_user(self, app):
        """On peut assigner plusieurs notes différentes au même utilisateur."""
        # Créer un utilisateur
        user = User(username="alice", email="alice@test.com", password_hash="hash1")
        db.session.add(user)
        db.session.commit()
        
        # Créer 2 notes
        note1 = Note(content="Note 1", creator_id=user.id)
        note2 = Note(content="Note 2", creator_id=user.id)
        db.session.add_all([note1, note2])
        db.session.commit()
        
        # Assigner note1 à Alice
        assignment1 = Assignment(note_id=note1.id, user_id=user.id)
        db.session.add(assignment1)
        db.session.commit()
        
        # Assigner note2 à Alice (différente note, donc OK)
        assignment2 = Assignment(note_id=note2.id, user_id=user.id)
        db.session.add(assignment2)
        db.session.commit()
        
        # Les deux devraient exister
        assert Assignment.query.filter_by(user_id=user.id).count() == 2
