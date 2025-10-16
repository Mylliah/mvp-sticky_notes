"""
Tests pour les routes de gestion des assignations.
"""
import pytest
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Note, Assignment


def create_user(app, username, email, password):
    """Helper pour créer un utilisateur."""
    with app.app_context():
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return user.id


def create_note(app, content, creator_id):
    """Helper pour créer une note."""
    with app.app_context():
        note = Note(content=content, creator_id=creator_id)
        db.session.add(note)
        db.session.commit()
        return note.id


class TestAssignmentsRoutes:
    """Tests pour les endpoints d'assignations."""

    # === POST /assignments - Créer une assignation ===

    @pytest.mark.integration
    def test_create_assignment_success(self, client, app, user, auth_token, note):
        """Créer une assignation avec succès."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.post('/v1/assignments', json={
                'note_id': note.id,
                'user_id': user.id
            }, headers=headers)
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['note_id'] == note.id
            assert data['user_id'] == user.id
            assert data['is_read'] is False

    @pytest.mark.integration
    def test_create_assignment_with_is_read(self, client, app, user, auth_token, note):
        """Créer une assignation avec is_read=True."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.post('/v1/assignments', json={
                'note_id': note.id,
                'user_id': user.id,
                'is_read': True
            }, headers=headers)
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['is_read'] is True

    @pytest.mark.integration
    def test_create_assignment_missing_note_id(self, client, app, user, auth_token):
        """Créer une assignation sans note_id échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.post('/v1/assignments', json={
                'user_id': user.id
            }, headers=headers)
            
            assert response.status_code == 400
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'note_id' in message.lower()

    @pytest.mark.integration
    def test_create_assignment_missing_user_id(self, client, app, user, auth_token, note):
        """Créer une assignation sans user_id échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.post('/v1/assignments', json={
                'note_id': note.id
            }, headers=headers)
            
            assert response.status_code == 400
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'user_id' in message.lower()

    @pytest.mark.integration
    def test_create_assignment_note_not_found(self, client, app, user, auth_token):
        """Créer une assignation avec note inexistante échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.post('/v1/assignments', json={
                'note_id': 99999,
                'user_id': user.id
            }, headers=headers)
            
            assert response.status_code == 400
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'Note not found' in message

    @pytest.mark.integration
    def test_create_assignment_user_not_found(self, client, app, user, auth_token, note):
        """Créer une assignation avec utilisateur inexistant échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.post('/v1/assignments', json={
                'note_id': note.id,
                'user_id': 99999
            }, headers=headers)
            
            assert response.status_code == 400
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'User not found' in message

    @pytest.mark.integration
    def test_create_assignment_duplicate(self, client, app, user, auth_token, note):
        """Créer une assignation en double échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            # Première assignation
            client.post('/v1/assignments', json={
                'note_id': note.id,
                'user_id': user.id
            }, headers=headers)
            
            # Tentative de doublon
            response = client.post('/v1/assignments', json={
                'note_id': note.id,
                'user_id': user.id
            }, headers=headers)
            
            assert response.status_code == 400
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'already exists' in message.lower()

    # === GET /assignments - Lister les assignations ===

    @pytest.mark.integration
    def test_list_assignments_empty(self, client, app, auth_token):
        """Lister les assignations quand il n'y en a aucune."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        with app.app_context():
            response = client.get('/v1/assignments', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data == []

    @pytest.mark.integration
    def test_list_assignments_with_assignments(self, client, app, user, auth_token, note, user2):
        """Lister les assignations existantes."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            # Créer une deuxième note
            note2 = Note(content='Note 2', creator_id=user.id)
            db.session.add(note2)
            db.session.commit()
            
            # Créer des assignations
            assignment1 = Assignment(note_id=note.id, user_id=user.id)
            assignment2 = Assignment(note_id=note2.id, user_id=user.id, is_read=True)
            db.session.add_all([assignment1, assignment2])
            db.session.commit()
            
            response = client.get('/v1/assignments', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 2
            assert data[0]['note_id'] == note.id
            assert data[1]['note_id'] == note2.id
            assert data[1]['is_read'] is True

    # === GET /assignments/<id> - Récupérer une assignation ===

    @pytest.mark.integration
    def test_get_assignment_success(self, client, app, user, auth_token, note):
        """Récupérer une assignation par son ID."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            assignment = Assignment(note_id=note.id, user_id=user.id)
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
            
            response = client.get(f'/v1/assignments/{assignment_id}', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == assignment_id
            assert data['note_id'] == note.id
            assert data['user_id'] == user.id

    @pytest.mark.integration
    def test_get_assignment_not_found(self, client, app, auth_token):
        """Récupérer une assignation inexistante retourne 404."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        with app.app_context():
            response = client.get('/v1/assignments/99999', headers=headers)
            
            assert response.status_code == 404

    # === PUT /assignments/<id> - Modifier une assignation ===

    @pytest.mark.integration
    def test_update_assignment_is_read(self, client, app, user, auth_token, note):
        """Modifier le statut de lecture."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            assignment = Assignment(note_id=note.id, user_id=user.id, is_read=False)
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
            
            response = client.put(f'/v1/assignments/{assignment_id}', json={
                'is_read': True
            }, headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['is_read'] is True

    @pytest.mark.integration
    def test_update_assignment_user_id(self, client, app, user, user2, auth_token, note):
        """Modifier l'utilisateur assigné."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            assignment = Assignment(note_id=note.id, user_id=user.id)
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
            
            response = client.put(f'/v1/assignments/{assignment_id}', json={
                'user_id': user2.id
            }, headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['user_id'] == user2.id

    @pytest.mark.integration
    def test_update_assignment_user_not_found(self, client, app, user, auth_token, note):
        """Modifier avec utilisateur inexistant échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            assignment = Assignment(note_id=note.id, user_id=user.id)
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
            
            response = client.put(f'/v1/assignments/{assignment_id}', json={
                'user_id': 99999
            }, headers=headers)
            
            assert response.status_code == 400
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'User not found' in message

    @pytest.mark.integration
    def test_update_assignment_duplicate_user(self, client, app, user, user2, auth_token, note):
        """Modifier avec un utilisateur déjà assigné échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            # Deux assignations pour la même note
            assignment1 = Assignment(note_id=note.id, user_id=user.id)
            assignment2 = Assignment(note_id=note.id, user_id=user2.id)
            db.session.add_all([assignment1, assignment2])
            db.session.commit()
            assignment1_id = assignment1.id
            
            # Essayer de modifier assignment1 pour qu'il ait le même user que assignment2
            response = client.put(f'/v1/assignments/{assignment1_id}', json={
                'user_id': user2.id
            }, headers=headers)
            
            assert response.status_code == 400
            data = response.get_json()
            message = data.get('description') or data.get('message', '')
            assert 'already exists' in message.lower()

    @pytest.mark.integration
    def test_update_assignment_not_found(self, client, app, auth_token):
        """Modifier une assignation inexistante retourne 404."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put('/v1/assignments/99999', json={
                'is_read': True
            }, headers=headers)
            
            assert response.status_code == 404

    # === DELETE /assignments/<id> - Supprimer une assignation ===

    @pytest.mark.integration
    def test_delete_assignment_success(self, client, app, user, auth_token, note):
        """Supprimer une assignation avec succès."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            assignment = Assignment(note_id=note.id, user_id=user.id)
            db.session.add(assignment)
            db.session.commit()
            assignment_id = assignment.id
            
            response = client.delete(f'/v1/assignments/{assignment_id}', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['deleted'] is True
            
            # Vérifier que l'assignation a été supprimée
            deleted = Assignment.query.get(assignment_id)
            assert deleted is None

    @pytest.mark.integration
    def test_delete_assignment_not_found(self, client, app, auth_token):
        """Supprimer une assignation inexistante retourne 404."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.delete('/v1/assignments/99999', headers=headers)
            
            assert response.status_code == 404
