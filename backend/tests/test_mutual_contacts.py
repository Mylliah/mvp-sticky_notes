"""
Tests pour la réciprocité des contacts et l'auto-marquage is_read.
"""
import pytest
from app.models import User, Contact, Note, Assignment
from app import db


class TestMutualContacts:
    """Tests pour la vérification de réciprocité des contacts."""
    
    def test_contact_is_mutual_returns_true_when_reciprocal(self, app):
        """Un contact est mutuel si les deux utilisateurs se sont ajoutés."""
        # Créer 2 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice ajoute Bob
        contact1 = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact1)
        db.session.commit()
        
        # Bob ajoute Alice
        contact2 = Contact(user_id=user2.id, contact_user_id=user1.id, nickname="Alice")
        db.session.add(contact2)
        db.session.commit()
        
        # Vérifier que les deux contacts sont mutuels
        assert contact1.is_mutual() is True
        assert contact2.is_mutual() is True
    
    def test_contact_is_mutual_returns_false_when_not_reciprocal(self, app):
        """Un contact n'est pas mutuel si l'autre ne l'a pas ajouté."""
        # Créer 2 utilisateurs
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Seulement Alice ajoute Bob (Bob ne l'a pas ajoutée)
        contact1 = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact1)
        db.session.commit()
        
        # Le contact n'est pas mutuel
        assert contact1.is_mutual() is False
    
    def test_contact_to_dict_includes_is_mutual(self, app):
        """to_dict() inclut le champ is_mutual."""
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact)
        db.session.commit()
        
        result = contact.to_dict()
        assert "is_mutual" in result
        assert result["is_mutual"] is False


class TestMutualContactsAPI:
    """Tests API pour la réciprocité des contacts."""
    
    def test_get_contacts_includes_is_mutual_field(self, client, app):
        """GET /contacts inclut is_mutual pour chaque contact."""
        # Créer users
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice ajoute Bob (pas mutuel)
        contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact)
        db.session.commit()
        
        # Login Alice
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user1.id))
        
        # GET /contacts
        response = client.get('/v1/contacts', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        
        contacts = response.json
        # Trouver Bob dans la liste (pas "Moi")
        bob_contact = [c for c in contacts if c.get("nickname") == "Bob"][0]
        assert bob_contact["is_mutual"] is False
    
    def test_get_assignable_includes_is_mutual_field(self, client, app):
        """GET /contacts/assignable inclut is_mutual."""
        # Créer users
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice ajoute Bob
        contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact)
        db.session.commit()
        
        # Login Alice
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user1.id))
        
        # GET /contacts/assignable
        response = client.get('/v1/contacts/assignable', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        
        assignable = response.json
        # Trouver Bob (pas "Moi")
        bob = [a for a in assignable if a.get("nickname") == "Bob"][0]
        assert "is_mutual" in bob
        assert bob["is_mutual"] is False
    
    def test_cannot_assign_note_to_non_mutual_contact(self, client, app):
        """On ne peut pas assigner une note à un contact non mutuel."""
        # Créer users
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice ajoute Bob (non mutuel)
        contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        db.session.add(contact)
        db.session.commit()
        
        # Alice crée une note
        note = Note(content="Test note", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Login Alice
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user1.id))
        
        # Essayer d'assigner à Bob (non mutuel) → devrait échouer
        response = client.post('/v1/assignments',
                              json={"note_id": note.id, "user_id": user2.id},
                              headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 403
        assert b"contact has not added you back" in response.data
    
    def test_can_assign_note_to_mutual_contact(self, client, app):
        """On peut assigner une note à un contact mutuel."""
        # Créer users
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice ajoute Bob
        contact1 = Contact(user_id=user1.id, contact_user_id=user2.id, nickname="Bob")
        # Bob ajoute Alice (mutuel)
        contact2 = Contact(user_id=user2.id, contact_user_id=user1.id, nickname="Alice")
        db.session.add_all([contact1, contact2])
        db.session.commit()
        
        # Alice crée une note
        note = Note(content="Test note", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Login Alice
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user1.id))
        
        # Assigner à Bob (mutuel) → devrait réussir
        response = client.post('/v1/assignments',
                              json={"note_id": note.id, "user_id": user2.id},
                              headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 201
        assert response.json["user_id"] == user2.id
    
    def test_can_self_assign_without_mutual_contact(self, client, app):
        """On peut s'auto-assigner sans vérification de réciprocité."""
        # Créer user
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        db.session.add(user1)
        db.session.commit()
        
        # Alice crée une note
        note = Note(content="Test note", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Login Alice
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user1.id))
        
        # S'auto-assigner → devrait réussir
        response = client.post('/v1/assignments',
                              json={"note_id": note.id, "user_id": user1.id},
                              headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 201


class TestAutoMarkAsRead:
    """Tests pour le marquage automatique is_read=True."""
    
    def test_opening_note_marks_assignment_as_read(self, client, app):
        """Ouvrir une note marque automatiquement is_read=True."""
        # Créer users
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice crée une note
        note = Note(content="Test note", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Alice assigne à Bob (is_read=False par défaut)
        assignment = Assignment(note_id=note.id, user_id=user2.id, is_read=False)
        db.session.add(assignment)
        db.session.commit()
        
        assert assignment.is_read is False
        
        # Bob se connecte et ouvre la note
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user2.id))
        
        response = client.get(f'/v1/notes/{note.id}',
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        
        # Vérifier que is_read est passé à True
        db.session.refresh(assignment)
        assert assignment.is_read is True
    
    def test_opening_note_sets_read_date(self, client, app):
        """Ouvrir une note met à jour read_date."""
        # Créer users
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice crée une note
        note = Note(content="Test note", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        assert note.read_date is None
        
        # Alice assigne à Bob
        assignment = Assignment(note_id=note.id, user_id=user2.id, is_read=False)
        db.session.add(assignment)
        db.session.commit()
        
        # Bob ouvre la note
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user2.id))
        
        response = client.get(f'/v1/notes/{note.id}',
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        
        # Vérifier que read_date est défini
        db.session.refresh(note)
        assert note.read_date is not None
    
    def test_opening_already_read_note_does_not_change_is_read(self, client, app):
        """Ouvrir une note déjà lue ne change pas is_read."""
        # Créer users
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice crée une note
        note = Note(content="Test note", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Alice assigne à Bob (déjà lu)
        assignment = Assignment(note_id=note.id, user_id=user2.id, is_read=True)
        db.session.add(assignment)
        db.session.commit()
        
        # Bob ouvre la note (déjà lue)
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user2.id))
        
        response = client.get(f'/v1/notes/{note.id}',
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        
        # is_read reste True
        db.session.refresh(assignment)
        assert assignment.is_read is True
    
    def test_creator_opening_own_note_does_not_affect_assignment(self, client, app):
        """Le créateur qui ouvre sa propre note n'affecte pas les assignations."""
        # Créer users
        user1 = User(username="alice", email="alice@test.com", password_hash="hash1")
        user2 = User(username="bob", email="bob@test.com", password_hash="hash2")
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Alice crée une note
        note = Note(content="Test note", creator_id=user1.id)
        db.session.add(note)
        db.session.commit()
        
        # Alice assigne à Bob (is_read=False)
        assignment = Assignment(note_id=note.id, user_id=user2.id, is_read=False)
        db.session.add(assignment)
        db.session.commit()
        
        # Alice (créatrice) ouvre sa propre note
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user1.id))
        
        response = client.get(f'/v1/notes/{note.id}',
                             headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 200
        
        # L'assignation de Bob reste is_read=False
        db.session.refresh(assignment)
        assert assignment.is_read is False
