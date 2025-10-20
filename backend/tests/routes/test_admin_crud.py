"""
Tests pour les routes CRUD admin (support utilisateur).
"""
import pytest
from app import db
from app.models import User, Note, Contact, Assignment


class TestAdminNotesCRUD:
    """Tests CRUD admin pour les notes."""
    
    def test_admin_can_get_any_note(self, client, app, admin_token, user):
        """L'admin peut voir n'importe quelle note."""
        with app.app_context():
            note = Note(content="Test note", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
        response = client.get(f'/v1/admin/notes/{note_id}',
                             headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['content'] == "Test note"
    
    def test_admin_can_update_any_note(self, client, app, admin_token, user):
        """L'admin peut modifier n'importe quelle note."""
        with app.app_context():
            note = Note(content="Original", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
        response = client.put(f'/v1/admin/notes/{note_id}',
                             headers={'Authorization': f'Bearer {admin_token}'},
                             json={'content': 'Updated by admin', 'important': True})
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "Note updated by admin"
        assert data['note']['content'] == "Updated by admin"
        assert data['note']['important'] is True
    
    def test_admin_can_delete_any_note(self, client, app, admin_token, user):
        """L'admin peut supprimer définitivement n'importe quelle note."""
        with app.app_context():
            note = Note(content="To delete", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
        response = client.delete(f'/v1/admin/notes/{note_id}',
                                headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        assert b"permanently deleted by admin" in response.data
        
        # Vérifier que la note est vraiment supprimée
        with app.app_context():
            assert Note.query.get(note_id) is None
    
    def test_non_admin_cannot_use_admin_note_routes(self, client, app, auth_token, user):
        """Un utilisateur normal ne peut pas utiliser les routes admin."""
        with app.app_context():
            note = Note(content="Test", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        # GET
        response = client.get(f'/v1/admin/notes/{note_id}',
                             headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 403
        
        # PUT
        response = client.put(f'/v1/admin/notes/{note_id}',
                             headers={'Authorization': f'Bearer {auth_token}'},
                             json={'content': 'Hack attempt'})
        assert response.status_code == 403
        
        # DELETE
        response = client.delete(f'/v1/admin/notes/{note_id}',
                                headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 403


class TestAdminContactsCRUD:
    """Tests CRUD admin pour les contacts."""
    
    def test_admin_can_list_all_contacts(self, client, app, admin_token, user, user2):
        """L'admin peut lister tous les contacts."""
        with app.app_context():
            contact = Contact(user_id=user.id, contact_user_id=user2.id, nickname="Test")
            db.session.add(contact)
            db.session.commit()
            
        response = client.get('/v1/admin/contacts',
                             headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_admin_can_get_any_contact(self, client, app, admin_token, user, user2):
        """L'admin peut voir n'importe quel contact."""
        with app.app_context():
            contact = Contact(user_id=user.id, contact_user_id=user2.id, nickname="Friend")
            db.session.add(contact)
            db.session.commit()
            contact_id = contact.id
            
        response = client.get(f'/v1/admin/contacts/{contact_id}',
                             headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['nickname'] == "Friend"
    
    def test_admin_can_update_any_contact(self, client, app, admin_token, user, user2):
        """L'admin peut modifier n'importe quel contact."""
        with app.app_context():
            contact = Contact(user_id=user.id, contact_user_id=user2.id, nickname="Old")
            db.session.add(contact)
            db.session.commit()
            contact_id = contact.id
            
        response = client.put(f'/v1/admin/contacts/{contact_id}',
                             headers={'Authorization': f'Bearer {admin_token}'},
                             json={'nickname': 'New nickname'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['contact']['nickname'] == "New nickname"
    
    def test_admin_can_delete_any_contact(self, client, app, admin_token, user, user2):
        """L'admin peut supprimer n'importe quel contact."""
        with app.app_context():
            contact = Contact(user_id=user.id, contact_user_id=user2.id, nickname="Delete")
            db.session.add(contact)
            db.session.commit()
            contact_id = contact.id
            
        response = client.delete(f'/v1/admin/contacts/{contact_id}',
                                headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        
        with app.app_context():
            assert Contact.query.get(contact_id) is None
    
    def test_non_admin_cannot_list_all_contacts(self, client, app, auth_token):
        """Un utilisateur normal ne peut pas lister tous les contacts."""
        response = client.get('/v1/admin/contacts',
                             headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 403


class TestAdminAssignmentsCRUD:
    """Tests CRUD admin pour les assignations."""
    
    def test_admin_can_list_all_assignments(self, client, app, admin_token, user, user2):
        """L'admin peut lister toutes les assignations."""
        with app.app_context():
            note = Note(content="Test", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=user2.id)
            db.session.add(assignment)
            db.session.commit()
            
        response = client.get('/v1/admin/assignments',
                             headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_admin_can_get_any_assignment(self, client, app, admin_token, user, user2):
        """L'admin peut voir n'importe quelle assignation."""
        with app.app_context():
            note = Note(content="Test", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=user2.id, is_read=False)
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
            
        response = client.get(f'/v1/admin/assignments/{assignment_id}',
                             headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_read'] is False
    
    def test_admin_can_update_any_assignment(self, client, app, admin_token, user, user2):
        """L'admin peut modifier n'importe quelle assignation."""
        with app.app_context():
            note = Note(content="Test", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=user2.id, is_read=False)
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
            
        response = client.put(f'/v1/admin/assignments/{assignment_id}',
                             headers={'Authorization': f'Bearer {admin_token}'},
                             json={'is_read': True, 'recipient_priority': True})
        assert response.status_code == 200
        data = response.get_json()
        assert data['assignment']['is_read'] is True
        assert data['assignment']['recipient_priority'] is True
    
    def test_admin_can_delete_any_assignment(self, client, app, admin_token, user, user2):
        """L'admin peut supprimer n'importe quelle assignation."""
        with app.app_context():
            note = Note(content="Test", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=user2.id)
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
            
        response = client.delete(f'/v1/admin/assignments/{assignment_id}',
                                headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == 200
        
        with app.app_context():
            assert Assignment.query.get(assignment_id) is None
    
    def test_non_admin_cannot_list_all_assignments(self, client, app, auth_token):
        """Un utilisateur normal ne peut pas lister toutes les assignations."""
        response = client.get('/v1/admin/assignments',
                             headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 403
