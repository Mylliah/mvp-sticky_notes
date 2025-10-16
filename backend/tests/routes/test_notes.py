"""
Tests pour les routes de gestion des notes.
"""
import pytest
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Note, Assignment


def get_error_message(response):
    """Helper pour extraire le message d'erreur de la réponse."""
    data = response.get_json()
    if data is None:
        return ""
    return data.get('description') or data.get('message') or data.get('error') or str(data)


def create_user_and_login(client, app, username, email, password):
    """Helper pour créer un utilisateur et obtenir son token JWT."""
    with app.app_context():
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    # Login pour obtenir le token
    response = client.post('/v1/auth/login', json={
        'username': username,
        'password': password
    })
    token = response.get_json()['access_token']
    return token, user_id


class TestNotesRoutes:
    """Tests pour les endpoints de notes."""

    # === POST /notes - Créer une note ===

    @pytest.mark.integration
    def test_create_note_success(self, client, app):
        """Créer une note avec succès."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token}'},
                json={'content': 'Ma première note'}
            )
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['content'] == 'Ma première note'
            assert data['creator_id'] == user_id
            assert data['status'] == 'en_cours'
            assert data['important'] is False

    @pytest.mark.integration
    def test_create_note_with_all_fields(self, client, app):
        """Créer une note avec tous les champs."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'content': 'Note importante',
                    'status': 'fait',
                    'important': True
                }
            )
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['content'] == 'Note importante'
            assert data['status'] == 'fait'
            assert data['important'] is True

    @pytest.mark.integration
    def test_create_note_missing_content(self, client, app):
        """Créer une note sans contenu échoue."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token}'},
                json={}
            )
            
            assert response.status_code == 400
            assert 'Missing content' in get_error_message(response)

    @pytest.mark.integration
    def test_create_note_requires_auth(self, client, app):
        """Créer une note nécessite une authentification."""
        with app.app_context():
            response = client.post('/v1/notes', json={
                'content': 'Test'
            })
            
            assert response.status_code == 401

    # === GET /notes - Lister les notes ===

    @pytest.mark.integration
    def test_list_notes_empty(self, client, app):
        """Lister les notes quand il n'y en a aucune."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/notes',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data == []

    @pytest.mark.integration
    def test_list_notes_with_notes(self, client, app):
        """Lister les notes existantes."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer quelques notes
            note1 = Note(content='Note 1', creator_id=user_id)
            note2 = Note(content='Note 2', creator_id=user_id, important=True)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            response = client.get('/v1/notes',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 2
            assert data[0]['content'] == 'Note 1'
            assert data[1]['content'] == 'Note 2'
            assert data[1]['important'] is True

    @pytest.mark.integration
    def test_list_notes_requires_auth(self, client, app):
        """Lister les notes nécessite une authentification."""
        with app.app_context():
            response = client.get('/v1/notes')
            
            assert response.status_code == 401

    # === GET /notes/<id> - Récupérer une note ===

    @pytest.mark.integration
    def test_get_note_success(self, client, app):
        """Récupérer une note par son ID."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test note', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.get(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == note_id
            assert data['content'] == 'Test note'

    @pytest.mark.integration
    def test_get_note_not_found(self, client, app):
        """Récupérer une note inexistante retourne 404."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/notes/99999',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_get_note_requires_auth(self, client, app):
        """Récupérer une note nécessite une authentification."""
        with app.app_context():
            response = client.get('/v1/notes/1')
            
            assert response.status_code == 401

    # === GET /notes/<id>/details - Récupérer les détails ===

    @pytest.mark.integration
    def test_get_note_details_success(self, client, app):
        """Récupérer les détails d'une note."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test note', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.get(f'/v1/notes/{note_id}/details',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == note_id
            assert 'assigned_to' in data

    @pytest.mark.integration
    def test_get_note_details_with_assignment(self, client, app):
        """Récupérer les détails d'une note avec assignation."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test note', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            
            # Créer une assignation
            assignment = Assignment(note_id=note.id, user_id=user_id)
            db.session.add(assignment)
            db.session.commit()
            
            response = client.get(f'/v1/notes/{note.id}/details',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['assigned_to'] == user_id

    @pytest.mark.integration
    def test_get_note_details_not_found(self, client, app):
        """Récupérer les détails d'une note inexistante retourne 404."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/notes/99999/details',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_get_note_details_requires_auth(self, client, app):
        """Récupérer les détails nécessite une authentification."""
        with app.app_context():
            response = client.get('/v1/notes/1/details')
            
            assert response.status_code == 401

    # === PUT /notes/<id> - Modifier une note ===

    @pytest.mark.integration
    def test_update_note_success(self, client, app):
        """Modifier une note avec succès."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Old content', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.put(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'},
                json={'content': 'New content', 'status': 'fait', 'important': True}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['content'] == 'New content'
            assert data['status'] == 'fait'
            assert data['important'] is True
            assert data['update_date'] is not None

    @pytest.mark.integration
    def test_update_note_missing_content(self, client, app):
        """Modifier une note sans contenu échoue."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.put(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'},
                json={'status': 'fait'}
            )
            
            assert response.status_code == 400
            assert 'Missing content' in get_error_message(response)

    @pytest.mark.integration
    def test_update_note_not_found(self, client, app):
        """Modifier une note inexistante retourne 404."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.put('/v1/notes/99999',
                headers={'Authorization': f'Bearer {token}'},
                json={'content': 'Test'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_update_note_requires_auth(self, client, app):
        """Modifier une note nécessite une authentification."""
        with app.app_context():
            response = client.put('/v1/notes/1', json={'content': 'Test'})
            
            assert response.status_code == 401

    # === DELETE /notes/<id> - Supprimer une note (soft delete) ===

    @pytest.mark.integration
    def test_delete_note_success(self, client, app):
        """Supprimer une note (soft delete)."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='To delete', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.delete(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['delete_date'] is not None
            
            # Vérifier que la note existe toujours en DB (soft delete)
            deleted_note = Note.query.get(note_id)
            assert deleted_note is not None
            assert deleted_note.delete_date is not None

    @pytest.mark.integration
    def test_delete_note_not_found(self, client, app):
        """Supprimer une note inexistante retourne 404."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.delete('/v1/notes/99999',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_delete_note_requires_auth(self, client, app):
        """Supprimer une note nécessite une authentification."""
        with app.app_context():
            response = client.delete('/v1/notes/1')
            
            assert response.status_code == 401
