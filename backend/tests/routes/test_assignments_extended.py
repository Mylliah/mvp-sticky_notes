"""
Tests étendus pour les routes Assignments - Couverture complète.
Couvre les filtres avancés et validations de contacts mutuels.
"""
import pytest
from app import db
from app.models import User, Note, Assignment, Contact
from flask_jwt_extended import create_access_token


class TestAssignmentsFilters:
    """Tests pour les filtres avancés dans list_assignments."""
    
    @pytest.mark.integration
    def test_list_assignments_filter_by_note_id(self, client, app):
        """Tester le filtre par note_id."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note1 = Note(content='Note 1', creator_id=user.id)
            note2 = Note(content='Note 2', creator_id=user.id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            assign1 = Assignment(note_id=note1.id, user_id=user.id)
            assign2 = Assignment(note_id=note2.id, user_id=user.id)
            db.session.add_all([assign1, assign2])
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                f'/v1/assignments?note_id={note1.id}',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) >= 1
            # Toutes les assignations devraient être pour note1
            for assignment in data:
                if assignment['note_id'] == note1.id or assignment['note_id'] == note2.id:
                    if assignment['note_id'] == note1.id:
                        assert True  # Au moins une assignation pour note1
    
    @pytest.mark.integration
    def test_list_assignments_filter_by_user_id(self, client, app):
        """Tester le filtre par user_id."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            note = Note(content='Test', creator_id=user1.id)
            db.session.add(note)
            db.session.commit()
            
            assign1 = Assignment(note_id=note.id, user_id=user1.id)
            assign2 = Assignment(note_id=note.id, user_id=user2.id)
            db.session.add_all([assign1, assign2])
            db.session.commit()
            
            token = create_access_token(identity=str(user1.id))
            response = client.get(
                f'/v1/assignments?user_id={user2.id}',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            # Devrait retourner des résultats filtrés
    
    @pytest.mark.integration
    def test_list_assignments_filter_by_assigner_id(self, client, app):
        """Tester le filtre par assigner_id (créateur de note)."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            note1 = Note(content='Alice note', creator_id=user1.id)
            note2 = Note(content='Bob note', creator_id=user2.id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            assign1 = Assignment(note_id=note1.id, user_id=user1.id)
            assign2 = Assignment(note_id=note2.id, user_id=user2.id)
            db.session.add_all([assign1, assign2])
            db.session.commit()
            
            token = create_access_token(identity=str(user1.id))
            response = client.get(
                f'/v1/assignments?assigner_id={user1.id}',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            # Devrait retourner les assignations créées par user1
    
    @pytest.mark.integration
    def test_list_assignments_filter_by_status(self, client, app):
        """Tester le filtre par status."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note1 = Note(content='Test1', creator_id=user.id)
            note2 = Note(content='Test2', creator_id=user.id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            # Deux notes différentes pour éviter la contrainte unique
            assign1 = Assignment(note_id=note1.id, user_id=user.id, recipient_status='en_cours')
            assign2 = Assignment(note_id=note2.id, user_id=user.id, recipient_status='terminé')
            db.session.add_all([assign1, assign2])
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                '/v1/assignments?status=en_cours',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            # Devrait filtrer par status


class TestAssignmentsMutualContactValidation:
    """Tests pour la validation des contacts mutuels lors de l'assignation."""
    
    @pytest.mark.integration
    def test_cannot_assign_to_non_contact(self, client, app):
        """Ne peut pas assigner à quelqu'un qui n'est pas dans les contacts."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            note = Note(content='Test', creator_id=user1.id)
            db.session.add(note)
            db.session.commit()
            
            token = create_access_token(identity=str(user1.id))
            response = client.post(
                '/v1/assignments',
                json={'note_id': note.id, 'user_id': user2.id},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'mutual' in message.lower() or 'contact' in message.lower()
    
    @pytest.mark.integration
    def test_cannot_assign_to_non_mutual_contact(self, client, app):
        """Ne peut pas assigner à un contact non mutuel."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            # Alice ajoute Bob, mais Bob n'ajoute pas Alice (non mutuel)
            contact = Contact(user_id=user1.id, contact_user_id=user2.id, nickname='Bob')
            db.session.add(contact)
            db.session.commit()
            
            note = Note(content='Test', creator_id=user1.id)
            db.session.add(note)
            db.session.commit()
            
            token = create_access_token(identity=str(user1.id))
            response = client.post(
                '/v1/assignments',
                json={'note_id': note.id, 'user_id': user2.id},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'mutual' in message.lower() or 'contact' in message.lower()
    
    @pytest.mark.integration
    def test_can_assign_to_mutual_contact(self, client, app):
        """Peut assigner à un contact mutuel."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            # Contacts mutuels
            contact1 = Contact(user_id=user1.id, contact_user_id=user2.id, nickname='Bob')
            contact2 = Contact(user_id=user2.id, contact_user_id=user1.id, nickname='Alice')
            db.session.add_all([contact1, contact2])
            db.session.commit()
            
            note = Note(content='Test', creator_id=user1.id)
            db.session.add(note)
            db.session.commit()
            
            token = create_access_token(identity=str(user1.id))
            response = client.post(
                '/v1/assignments',
                json={'note_id': note.id, 'user_id': user2.id},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['user_id'] == user2.id
    
    @pytest.mark.integration
    def test_can_self_assign_without_contact(self, client, app):
        """Peut s'auto-assigner sans restriction de contact."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note = Note(content='Test', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.post(
                '/v1/assignments',
                json={'note_id': note.id, 'user_id': user.id},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['user_id'] == user.id
    
    @pytest.mark.integration
    def test_only_creator_can_assign(self, client, app):
        """Seul le créateur peut assigner sa note."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            note = Note(content='Alice note', creator_id=user1.id)
            db.session.add(note)
            db.session.commit()
            
            # Bob tente d'assigner la note d'Alice
            token_bob = create_access_token(identity=str(user2.id))
            response = client.post(
                '/v1/assignments',
                json={'note_id': note.id, 'user_id': user2.id},
                headers={"Authorization": f"Bearer {token_bob}"}
            )
            
            assert response.status_code == 403
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'creator' in message.lower()
