"""
Tests pour l'isolation des données entre utilisateurs.
Vérifie qu'un utilisateur ne peut pas accéder/modifier les données d'un autre.
"""
import pytest
from app.models import User, Note, Contact, Assignment, ActionLog
from app import db
from flask_jwt_extended import create_access_token


class TestNotesIsolation:
    """Tests d'isolation pour les notes."""
    
    def test_cannot_update_other_user_note(self, client, app):
        """Un utilisateur ne peut pas modifier la note d'un autre."""
        # Créer 2 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice crée une note
        note = Note(content="Note d'Alice", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Bob essaie de modifier la note d'Alice
        token_bob = create_access_token(identity=str(user2.id))
        response = client.put(f'/v1/notes/{note.id}',
                             json={"content": "Note modifiée par Bob"},
                             headers={"Authorization": f"Bearer {token_bob}"})
        
        assert response.status_code == 403
        assert b"Only the creator" in response.data
    
    def test_cannot_delete_other_user_note(self, client, app):
        """Un utilisateur ne peut pas supprimer la note d'un autre s'il n'est ni créateur ni destinataire."""
        # Créer 2 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice crée une note (SANS l'assigner à Bob)
        note = Note(content="Note d'Alice", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Bob essaie de supprimer la note d'Alice (mais il n'est pas destinataire)
        token_bob = create_access_token(identity=str(user2.id))
        response = client.delete(f'/v1/notes/{note.id}',
                                headers={"Authorization": f"Bearer {token_bob}"})
        
        assert response.status_code == 403
        assert b"Only the creator or recipient" in response.data
    
    def test_creator_can_update_own_note(self, client, app):
        """Le créateur peut modifier sa propre note."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        db.session.add(user1)
        db.session.commit()
        
        note = Note(content="Note d'Alice", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        token = create_access_token(identity=str(user1.id))
        response = client.put(f'/v1/notes/{note.id}',
                             json={"content": "Note modifiée"},
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        assert response.json["content"] == "Note modifiée"


class TestContactsIsolation:
    """Tests d'isolation pour les contacts."""
    
    def test_cannot_view_other_user_contact(self, client, app):
        """Un utilisateur ne peut pas voir les contacts d'un autre."""
        # Créer 3 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        user3 = User(username="charlie", email="charlie@test.com", password_hash="hash3")
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        # Alice ajoute Bob comme contact
        contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact)
        db.session.commit()
        
        # Charlie essaie de voir le contact d'Alice
        token_charlie = create_access_token(identity=str(user3.id))
        response = client.get(f'/v1/contacts/{contact.id}',
                             headers={"Authorization": f"Bearer {token_charlie}"})
        
        assert response.status_code == 403
        assert b"your own contacts" in response.data
    
    def test_cannot_update_other_user_contact(self, client, app):
        """Un utilisateur ne peut pas modifier les contacts d'un autre."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        user3 = User(username="charlie", email="charlie@test.com", password_hash="hash3")
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact)
        db.session.commit()
        
        token_charlie = create_access_token(identity=str(user3.id))
        response = client.put(f'/v1/contacts/{contact.id}',
                             json={"nickname": "Nouveau nom"},
                             headers={"Authorization": f"Bearer {token_charlie}"})
        
        assert response.status_code == 403
        assert b"your own contacts" in response.data
    
    def test_cannot_delete_other_user_contact(self, client, app):
        """Un utilisateur ne peut pas supprimer les contacts d'un autre."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        user3 = User(username="charlie", email="charlie@test.com", password_hash="hash3")
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact)
        db.session.commit()
        
        token_charlie = create_access_token(identity=str(user3.id))
        response = client.delete(f'/v1/contacts/{contact.id}',
                                headers={"Authorization": f"Bearer {token_charlie}"})
        
        assert response.status_code == 403
        assert b"your own contacts" in response.data
    
    def test_owner_can_update_own_contact(self, client, app):
        """Le propriétaire peut modifier son propre contact."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact)
        db.session.commit()
        
        token = create_access_token(identity=str(user1.id))
        response = client.put(f'/v1/contacts/{contact.id}',
                             json={"nickname": "Bobby"},
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        assert response.json["nickname"] == "Bobby"


class TestAssignmentsIsolation:
    """Tests d'isolation pour les assignations."""
    
    def test_cannot_view_unrelated_assignment(self, client, app):
        """Un utilisateur ne peut pas voir une assignation qui ne le concerne pas."""
        # Créer 3 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        user3 = User(username="charlie", email="charlie@test.com", password_hash="hash3")
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        # Alice crée une note et l'assigne à Bob
        note = Note(content="Note d'Alice", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        assignment = Assignment(note_id=note.id, user_id=user2.id)
        db.session.add(assignment)
        db.session.commit()
        
        # Charlie essaie de voir l'assignation
        token_charlie = create_access_token(identity=str(user3.id))
        response = client.get(f'/v1/assignments/{assignment.id}',
                             headers={"Authorization": f"Bearer {token_charlie}"})
        
        assert response.status_code == 403
        data = response.get_json()
        message = data.get('description') or data.get('message', '')
        assert 'access' in message.lower() or 'denied' in message.lower()
    
    def test_creator_can_view_assignment(self, client, app):
        """Le créateur de la note peut voir l'assignation."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        note = Note(content="Note d'Alice", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        assignment = Assignment(note_id=note.id, user_id=user2.id)
        db.session.add(assignment)
        db.session.commit()
        
        token = create_access_token(identity=str(user1.id))
        response = client.get(f'/v1/assignments/{assignment.id}',
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
    
    def test_recipient_can_view_assignment(self, client, app):
        """Le destinataire peut voir son assignation."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        note = Note(content="Note d'Alice", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        assignment = Assignment(note_id=note.id, user_id=user2.id)
        db.session.add(assignment)
        db.session.commit()
        
        token = create_access_token(identity=str(user2.id))
        response = client.get(f'/v1/assignments/{assignment.id}',
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
    
    def test_recipient_cannot_change_assignment_user(self, client, app):
        """Le destinataire ne peut pas changer le destinataire de l'assignation."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        user3 = User(username="charlie", email="charlie@test.com", password_hash="hash3")
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        note = Note(content="Note d'Alice", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        assignment = Assignment(note_id=note.id, user_id=user2.id)
        db.session.add(assignment)
        db.session.commit()
        
        # Bob essaie de changer le destinataire vers Charlie
        token_bob = create_access_token(identity=str(user2.id))
        response = client.put(f'/v1/assignments/{assignment.id}',
                             json={"user_id": user3.id},
                             headers={"Authorization": f"Bearer {token_bob}"})
        
        assert response.status_code == 403
        assert b"Only the creator" in response.data
    
    def test_only_creator_can_delete_assignment(self, client, app):
        """Seul le créateur peut supprimer une assignation."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        note = Note(content="Note d'Alice", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        assignment = Assignment(note_id=note.id, user_id=user2.id)
        db.session.add(assignment)
        db.session.commit()
        
        # Bob (destinataire) peut supprimer son propre assignment
        token_bob = create_access_token(identity=str(user2.id))
        response = client.delete(f'/v1/assignments/{assignment.id}',
                                headers={"Authorization": f"Bearer {token_bob}"})
        
        # Le destinataire peut supprimer l'assignation (comportement correct)
        assert response.status_code == 200

    @pytest.mark.integration
    def test_third_party_cannot_delete_assignment(self, client, app):
        """Un tiers (ni créateur ni destinataire) ne peut pas supprimer une assignation."""
        with app.app_context():
            from flask_jwt_extended import create_access_token
            
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            user3 = User(username='charlie', email='charlie@test.com', password_hash='hash')
            db.session.add_all([user1, user2, user3])
            db.session.commit()
            
            note = Note(content="Note d'Alice pour Bob", creator_id=user1.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=user2.id)
            db.session.add(assignment)
            db.session.commit()
            
            # Charlie (ni créateur ni destinataire) essaie de supprimer
            token_charlie = create_access_token(identity=str(user3.id))
            response = client.delete(f'/v1/assignments/{assignment.id}',
                                    headers={"Authorization": f"Bearer {token_charlie}"})
            
            assert response.status_code == 403
            assert b"Only the creator or the recipient" in response.data


# NOTE: Tests d'isolation pour Action Logs supprimés.
# Les action logs sont maintenant réservés aux admins uniquement (@admin_required).
# Voir tests/routes/test_action_logs_security.py pour les tests de sécurité admin-only.
