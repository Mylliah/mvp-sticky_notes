"""
Tests pour les routes de gestion des utilisateurs.
"""
import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User


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


def get_error_message(response):
    """Helper pour extraire le message d'erreur de la réponse."""
    data = response.get_json()
    if data is None:
        return ""
    return data.get('description') or data.get('message') or data.get('error') or str(data)


class TestUsersRoutes:
    """Tests pour les endpoints d'utilisateurs."""

    # === GET /users - Lister les utilisateurs ===

    @pytest.mark.integration
    def test_list_users_empty(self, client, app, user, auth_token):
        """Lister les utilisateurs quand il n'y en a qu'un (le user authentifié)."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        with app.app_context():
            response = client.get('/v1/users', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 1  # Le user lui-même

    @pytest.mark.integration
    def test_list_users_with_users(self, client, app, user, auth_token, user2):
        """Lister les utilisateurs existants."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.get('/v1/users', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) >= 2  # Au moins user et user2
            # Vérifier que les mots de passe ne sont pas exposés
            assert 'password' not in data[0]
            assert 'password_hash' not in data[0]

    # === GET /users/<id> - Récupérer un utilisateur ===

    @pytest.mark.integration
    def test_get_user_success(self, client, app, user, auth_token):
        """Récupérer un utilisateur par son ID."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.get(f'/v1/users/{user.id}', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == user.id
            assert data['username'] == 'testuser'
            assert data['email'] == 'test@example.com'
            # Vérifier que le mot de passe n'est pas exposé
            assert 'password' not in data
            assert 'password_hash' not in data

    @pytest.mark.integration
    def test_get_user_not_found(self, client, app, auth_token):
        """Récupérer un utilisateur inexistant retourne 404."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        with app.app_context():
            response = client.get('/v1/users/99999', headers=headers)
            
            assert response.status_code == 404

    # === PUT /users/<id> - Modifier un utilisateur ===

    @pytest.mark.integration
    def test_update_user_username(self, client, app, user, auth_token):
        """Modifier le username d'un utilisateur."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'username': 'newname'
            }, headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['username'] == 'newname'

    @pytest.mark.integration
    def test_update_user_email(self, client, app, user, auth_token):
        """Modifier l'email d'un utilisateur."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'email': 'new@test.com'
            }, headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['email'] == 'new@test.com'

    @pytest.mark.integration
    def test_update_user_password(self, client, app, user, auth_token):
        """Modifier le mot de passe d'un utilisateur."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'password': 'newpass'
            }, headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Vérifier que le mot de passe a bien été changé
            updated_user = User.query.get(user.id)
            assert check_password_hash(updated_user.password_hash, 'newpass')

    @pytest.mark.integration
    def test_update_user_multiple_fields(self, client, app, user, auth_token):
        """Modifier plusieurs champs d'un utilisateur."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'username': 'newname',
                'email': 'new@test.com',
                'password': 'newpass'
            }, headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['username'] == 'newname'
            assert data['email'] == 'new@test.com'

    @pytest.mark.integration
    def test_update_user_username_empty(self, client, app, user, auth_token):
        """Modifier avec username vide échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'username': ''
            }, headers=headers)
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_username_whitespace(self, client, app, user, auth_token):
        """Modifier avec username avec espaces seulement échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'username': '   '
            }, headers=headers)
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_username_duplicate(self, client, app, user, user2, auth_token):
        """Modifier avec username existant échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'username': 'testuser2'  # username de user2
            }, headers=headers)
            
            assert response.status_code == 400
            assert 'already exists' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_email_empty(self, client, app, user, auth_token):
        """Modifier avec email vide échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'email': ''
            }, headers=headers)
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_email_whitespace(self, client, app, user, auth_token):
        """Modifier avec email avec espaces seulement échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'email': '   '
            }, headers=headers)
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_email_duplicate(self, client, app, user, user2, auth_token):
        """Modifier avec email existant échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'email': 'test2@example.com'  # email de user2
            }, headers=headers)
            
            assert response.status_code == 400
            assert 'already exists' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_password_empty(self, client, app, user, auth_token):
        """Modifier avec mot de passe vide échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'password': ''
            }, headers=headers)
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_password_whitespace(self, client, app, user, auth_token):
        """Modifier avec mot de passe avec espaces seulement échoue."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.put(f'/v1/users/{user.id}', json={
                'password': '   '
            }, headers=headers)
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_not_found(self, client, app, auth_token):
        """Modifier un utilisateur inexistant retourne 404."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        with app.app_context():
            response = client.put('/v1/users/99999', json={
                'username': 'newname'
            }, headers=headers)
            
            assert response.status_code == 404

    # === DELETE /users/<id> - Supprimer un utilisateur ===

    @pytest.mark.integration
    def test_delete_user_success(self, client, app, user, auth_token):
        """Supprimer un utilisateur avec succès."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        
        with app.app_context():
            response = client.delete(f'/v1/users/{user.id}', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['deleted'] is True
            
            # Vérifier que l'utilisateur a été supprimé
            deleted = User.query.get(user.id)
            assert deleted is None

    @pytest.mark.integration
    def test_delete_user_not_found(self, client, app, auth_token):
        """Supprimer un utilisateur inexistant retourne 404."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        with app.app_context():
            response = client.delete('/v1/users/99999', headers=headers)
            
            assert response.status_code == 404
