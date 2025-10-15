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
    def test_list_users_empty(self, client, app):
        """Lister les utilisateurs quand il n'y en a aucun."""
        with app.app_context():
            response = client.get('/v1/users')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data == []

    @pytest.mark.integration
    def test_list_users_with_users(self, client, app):
        """Lister les utilisateurs existants."""
        user_id1 = create_user(app, 'user1', 'user1@test.com', 'pass1')
        user_id2 = create_user(app, 'user2', 'user2@test.com', 'pass2')
        
        with app.app_context():
            response = client.get('/v1/users')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 2
            assert data[0]['username'] == 'user1'
            assert data[1]['username'] == 'user2'
            # Vérifier que les mots de passe ne sont pas exposés
            assert 'password' not in data[0]
            assert 'password_hash' not in data[0]

    # === GET /users/<id> - Récupérer un utilisateur ===

    @pytest.mark.integration
    def test_get_user_success(self, client, app):
        """Récupérer un utilisateur par son ID."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'password')
        
        with app.app_context():
            response = client.get(f'/v1/users/{user_id}')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == user_id
            assert data['username'] == 'user1'
            assert data['email'] == 'user1@test.com'
            # Vérifier que le mot de passe n'est pas exposé
            assert 'password' not in data
            assert 'password_hash' not in data

    @pytest.mark.integration
    def test_get_user_not_found(self, client, app):
        """Récupérer un utilisateur inexistant retourne 404."""
        with app.app_context():
            response = client.get('/v1/users/99999')
            
            assert response.status_code == 404

    # === PUT /users/<id> - Modifier un utilisateur ===

    @pytest.mark.integration
    def test_update_user_username(self, client, app):
        """Modifier le username d'un utilisateur."""
        user_id = create_user(app, 'oldname', 'user@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'username': 'newname'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['username'] == 'newname'

    @pytest.mark.integration
    def test_update_user_email(self, client, app):
        """Modifier l'email d'un utilisateur."""
        user_id = create_user(app, 'user1', 'old@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'email': 'new@test.com'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['email'] == 'new@test.com'

    @pytest.mark.integration
    def test_update_user_password(self, client, app):
        """Modifier le mot de passe d'un utilisateur."""
        user_id = create_user(app, 'user1', 'user@test.com', 'oldpass')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'password': 'newpass'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Vérifier que le mot de passe a bien été changé
            user = User.query.get(user_id)
            assert check_password_hash(user.password_hash, 'newpass')

    @pytest.mark.integration
    def test_update_user_multiple_fields(self, client, app):
        """Modifier plusieurs champs d'un utilisateur."""
        user_id = create_user(app, 'oldname', 'old@test.com', 'oldpass')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'username': 'newname',
                'email': 'new@test.com',
                'password': 'newpass'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['username'] == 'newname'
            assert data['email'] == 'new@test.com'

    @pytest.mark.integration
    def test_update_user_username_empty(self, client, app):
        """Modifier avec username vide échoue."""
        user_id = create_user(app, 'user1', 'user@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'username': ''
            })
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_username_whitespace(self, client, app):
        """Modifier avec username avec espaces seulement échoue."""
        user_id = create_user(app, 'user1', 'user@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'username': '   '
            })
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_username_duplicate(self, client, app):
        """Modifier avec username existant échoue."""
        user_id1 = create_user(app, 'user1', 'user1@test.com', 'password')
        user_id2 = create_user(app, 'user2', 'user2@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id2}', json={
                'username': 'user1'
            })
            
            assert response.status_code == 400
            assert 'already exists' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_email_empty(self, client, app):
        """Modifier avec email vide échoue."""
        user_id = create_user(app, 'user1', 'user@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'email': ''
            })
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_email_whitespace(self, client, app):
        """Modifier avec email avec espaces seulement échoue."""
        user_id = create_user(app, 'user1', 'user@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'email': '   '
            })
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_email_duplicate(self, client, app):
        """Modifier avec email existant échoue."""
        user_id1 = create_user(app, 'user1', 'user1@test.com', 'password')
        user_id2 = create_user(app, 'user2', 'user2@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id2}', json={
                'email': 'user1@test.com'
            })
            
            assert response.status_code == 400
            assert 'already exists' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_password_empty(self, client, app):
        """Modifier avec mot de passe vide échoue."""
        user_id = create_user(app, 'user1', 'user@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'password': ''
            })
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_password_whitespace(self, client, app):
        """Modifier avec mot de passe avec espaces seulement échoue."""
        user_id = create_user(app, 'user1', 'user@test.com', 'password')
        
        with app.app_context():
            response = client.put(f'/v1/users/{user_id}', json={
                'password': '   '
            })
            
            assert response.status_code == 400
            assert 'cannot be empty' in get_error_message(response).lower()

    @pytest.mark.integration
    def test_update_user_not_found(self, client, app):
        """Modifier un utilisateur inexistant retourne 404."""
        with app.app_context():
            response = client.put('/v1/users/99999', json={
                'username': 'newname'
            })
            
            assert response.status_code == 404

    # === DELETE /users/<id> - Supprimer un utilisateur ===

    @pytest.mark.integration
    def test_delete_user_success(self, client, app):
        """Supprimer un utilisateur avec succès."""
        user_id = create_user(app, 'user1', 'user@test.com', 'password')
        
        with app.app_context():
            response = client.delete(f'/v1/users/{user_id}')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['deleted'] is True
            
            # Vérifier que l'utilisateur a été supprimé
            deleted = User.query.get(user_id)
            assert deleted is None

    @pytest.mark.integration
    def test_delete_user_not_found(self, client, app):
        """Supprimer un utilisateur inexistant retourne 404."""
        with app.app_context():
            response = client.delete('/v1/users/99999')
            
            assert response.status_code == 404
