"""
Tests étendus pour les routes Notes - Couverture complète.
Couvre les paramètres alternatifs, filtres avancés, et endpoints orphans/history.
"""
import pytest
from app import db
from app.models import User, Note, Assignment, ActionLog
from flask_jwt_extended import create_access_token
import json


class TestNotesExtendedFilters:
    """Tests pour les paramètres de filtrage et tri alternatifs."""
    
    @pytest.mark.integration
    def test_filter_by_creator_id(self, client, app):
        """Tester le filtre creator_id."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            note1 = Note(content='Note Alice', creator_id=user1.id)
            note2 = Note(content='Note Bob', creator_id=user2.id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            # Alice peut voir toutes les notes avec filtre creator_id
            token = create_access_token(identity=str(user1.id))
            response = client.get(
                f'/v1/notes?creator_id={user1.id}',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['total'] == 1
            assert data['notes'][0]['content'] == 'Note Alice'
    
    @pytest.mark.integration
    def test_filter_by_important_boolean(self, client, app):
        """Tester le filtre important direct (booléen)."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note1 = Note(content='Important', creator_id=user.id, important=True)
            note2 = Note(content='Normal', creator_id=user.id, important=False)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            
            # Filtre important=true
            response = client.get(
                '/v1/notes?important=true',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['total'] == 1
            assert data['notes'][0]['important'] is True
    
    @pytest.mark.integration
    def test_sort_by_created_date_asc(self, client, app):
        """Tester le tri avec sort_by et sort_order."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note1 = Note(content='First', creator_id=user.id)
            note2 = Note(content='Second', creator_id=user.id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                '/v1/notes?sort_by=created_date&sort_order=asc',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 2
            assert data['notes'][0]['content'] == 'First'
    
    @pytest.mark.integration
    def test_sort_by_important(self, client, app):
        """Tester le tri par important avec sort_by."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note1 = Note(content='Normal', creator_id=user.id, important=False)
            note2 = Note(content='Important', creator_id=user.id, important=True)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                '/v1/notes?sort_by=important',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['notes'][0]['important'] is True
    
    @pytest.mark.integration
    def test_sort_by_invalid_fallback(self, client, app):
        """Tester que sort_by invalide utilise le tri par défaut."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note = Note(content='Test', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                '/v1/notes?sort_by=invalid_sort',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            # Ne doit pas crasher, utilise le tri par défaut
    
    @pytest.mark.integration
    def test_filter_in_progress(self, client, app):
        """Tester le filtre in_progress."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note = Note(content='In Progress', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(
                note_id=note.id,
                user_id=user.id,
                recipient_status='en_cours'
            )
            db.session.add(assignment)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                '/v1/notes?filter=in_progress',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['total'] >= 1
    
    @pytest.mark.integration
    def test_filter_completed(self, client, app):
        """Tester le filtre completed."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note = Note(content='Completed', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(
                note_id=note.id,
                user_id=user.id,
                recipient_status='terminé'
            )
            db.session.add(assignment)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                '/v1/notes?filter=completed',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['total'] >= 1


class TestNotesContentValidation:
    """Tests pour la validation du contenu."""
    
    @pytest.mark.integration
    def test_create_note_content_too_long(self, client, app):
        """Tester la limite de 5000 caractères."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            long_content = 'A' * 5001  # Dépasse la limite
            
            response = client.post(
                '/v1/notes',
                json={'content': long_content},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 400
            assert b'Content too long' in response.data


class TestOrphanNotes:
    """Tests pour l'endpoint /notes/orphans."""
    
    @pytest.mark.integration
    def test_get_orphan_notes_empty(self, client, app):
        """Tester l'endpoint orphans quand il n'y a pas de notes orphelines."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            # Créer une note avec assignation (pas orpheline)
            note = Note(content='Assigned note', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=user.id)
            db.session.add(assignment)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                '/v1/notes/orphans',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 0
            assert len(data['notes']) == 0
    
    @pytest.mark.integration
    def test_get_orphan_notes_with_orphans(self, client, app):
        """Tester l'endpoint orphans avec des notes sans assignation."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            # Note orpheline (sans assignation)
            orphan_note = Note(content='Orphan note', creator_id=user.id)
            db.session.add(orphan_note)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                '/v1/notes/orphans',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['count'] == 1
            assert data['notes'][0]['is_orphan'] is True
            assert data['notes'][0]['content'] == 'Orphan note'


class TestNotesDeletionHistory:
    """Tests pour l'endpoint /notes/:id/deletion-history."""
    
    @pytest.mark.integration
    def test_deletion_history_only_creator(self, client, app):
        """Seul le créateur peut voir l'historique de suppressions."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            note = Note(content='Test note', creator_id=user1.id)
            db.session.add(note)
            db.session.commit()
            
            # Bob tente d'accéder à l'historique
            token_bob = create_access_token(identity=str(user2.id))
            response = client.get(
                f'/v1/notes/{note.id}/deletion-history',
                headers={"Authorization": f"Bearer {token_bob}"}
            )
            
            assert response.status_code == 403
            assert b'Only the creator' in response.data
    
    @pytest.mark.integration
    def test_deletion_history_with_logs(self, client, app):
        """Tester l'historique avec des suppressions enregistrées."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            recipient = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user, recipient])
            db.session.commit()
            
            note = Note(content='Test note', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            # Créer un log de suppression d'assignation
            action_log = ActionLog(
                user_id=recipient.id,
                action_type="assignment_deleted",
                target_id=999,  # ID fictif
                payload=json.dumps({
                    "note_id": note.id,
                    "assigned_user_id": recipient.id
                })
            )
            db.session.add(action_log)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                f'/v1/notes/{note.id}/deletion-history',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'deletions' in data
            assert len(data['deletions']) == 1
            assert data['deletions'][0]['username'] == 'bob'
    
    @pytest.mark.integration
    def test_deletion_history_empty(self, client, app):
        """Tester l'historique vide."""
        with app.app_context():
            user = User(username='alice', email='alice@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            note = Note(content='Test note', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            
            token = create_access_token(identity=str(user.id))
            response = client.get(
                f'/v1/notes/{note.id}/deletion-history',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['deletions'] == []
