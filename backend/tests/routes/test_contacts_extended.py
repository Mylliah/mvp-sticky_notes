"""
Tests étendus pour les routes Contacts - Couverture complète.
Couvre les filtres de notes partagées et validations edge cases.
"""
import pytest
from app import db
from app.models import User, Note, Assignment, Contact
from flask_jwt_extended import create_access_token


class TestContactNotesFilters:
    """Tests pour les filtres dans get_contact_notes."""
    
    @pytest.mark.integration
    def test_contact_notes_filter_important(self, client, app):
        """Tester le filtre important dans contact notes."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            # Alice ajoute Bob comme contact
            contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname='Bob')
            db.session.add(contact)
            db.session.commit()
            
            # Note importante de Bob à Alice
            note_important = Note(content='Important', creator_id=user2.id, important=True)
            note_normal = Note(content='Normal', creator_id=user2.id, important=False)
            db.session.add_all([note_important, note_normal])
            db.session.commit()
            
            assign1 = Assignment(note_id=note_important.id, user_id=user1.id)
            assign2 = Assignment(note_id=note_normal.id, user_id=user1.id)
            db.session.add_all([assign1, assign2])
            db.session.commit()
            
            token = create_access_token(identity=str(user1.id))
            response = client.get(
                f'/v1/contacts/{contact.id}/notes?filter=important',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            # Devrait ne retourner que les notes importantes
            for note in data['notes']:
                if 'important' in note:
                    assert note['important'] is True
    
    @pytest.mark.integration
    def test_contact_notes_pagination_limits(self, client, app):
        """Tester les limites de pagination."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname='Bob')
            db.session.add(contact)
            db.session.commit()
            
            token = create_access_token(identity=str(user1.id))
            
            # Test per_page > 100 (devrait être limité à 100)
            response = client.get(
                f'/v1/contacts/{contact.id}/notes?per_page=200',
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['per_page'] == 100  # Limité à 100
            
            # Test per_page < 1 (devrait utiliser la valeur par défaut)
            response = client.get(
                f'/v1/contacts/{contact.id}/notes?per_page=0',
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['per_page'] == 20  # Valeur par défaut
            
            # Test page < 1 (devrait utiliser page 1)
            response = client.get(
                f'/v1/contacts/{contact.id}/notes?page=0',
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['page'] == 1  # Minimum page 1
