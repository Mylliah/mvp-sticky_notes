"""
Tests pour les routes d'authentification (register, login).
"""
import pytest
from app import db
from app.models import User


def get_error_message(response):
    """Helper pour extraire le message d'erreur de la réponse."""
    data = response.get_json()
    if data is None:
        return ""
    return data.get('description') or data.get('message') or data.get('error') or str(data)


class TestAuthRoutes:
    """Tests pour les endpoints d'authentification."""

    # === REGISTER ===

    @pytest.mark.integration
    def test_register_success(self, client, app):
        """Enregistrement réussi d'un nouvel utilisateur."""
        with app.app_context():
            response = client.post('/v1/auth/register', json={
                'username': 'newuser',
                'email': 'newuser@test.com',
                'password': 'securepassword123'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['msg'] == 'User created successfully'
            assert data['username'] == 'newuser'
            
            # Vérifier que l'utilisateur existe en DB
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@test.com'
            assert user.password_hash is not None
            assert user.password_hash != 'securepassword123'  # Doit être haché

    @pytest.mark.integration
    def test_register_missing_username(self, client, app):
        """Enregistrement échoue si username manquant."""
        with app.app_context():
            response = client.post('/v1/auth/register', json={
                'email': 'test@test.com',
                'password': 'password123'
            })
            
            assert response.status_code == 400
            assert 'Missing username, email or password' in get_error_message(response)

    @pytest.mark.integration
    def test_register_missing_email(self, client, app):
        """Enregistrement échoue si email manquant."""
        with app.app_context():
            response = client.post('/v1/auth/register', json={
                'username': 'testuser',
                'password': 'password123'
            })
            
            assert response.status_code == 400
            assert 'Missing username, email or password' in get_error_message(response)

    @pytest.mark.integration
    def test_register_missing_password(self, client, app):
        """Enregistrement échoue si password manquant."""
        with app.app_context():
            response = client.post('/v1/auth/register', json={
                'username': 'testuser',
                'email': 'test@test.com'
            })
            
            assert response.status_code == 400
            assert 'Missing username, email or password' in get_error_message(response)

    @pytest.mark.integration
    def test_register_duplicate_username(self, client, app):
        """Enregistrement échoue si username existe déjà."""
        with app.app_context():
            # Créer un premier utilisateur
            user = User(username='existing', email='existing@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            # Tenter de créer un utilisateur avec le même username
            response = client.post('/v1/auth/register', json={
                'username': 'existing',
                'email': 'different@test.com',
                'password': 'password123'
            })
            
            assert response.status_code == 400
            assert 'Username or email already exists' in get_error_message(response)

    @pytest.mark.integration
    def test_register_duplicate_email(self, client, app):
        """Enregistrement échoue si email existe déjà."""
        with app.app_context():
            # Créer un premier utilisateur
            user = User(username='existing', email='existing@test.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            
            # Tenter de créer un utilisateur avec le même email
            response = client.post('/v1/auth/register', json={
                'username': 'different',
                'email': 'existing@test.com',
                'password': 'password123'
            })
            
            assert response.status_code == 400
            assert 'Username or email already exists' in get_error_message(response)

    @pytest.mark.integration
    def test_register_empty_json(self, client, app):
        """Enregistrement échoue si le JSON est vide."""
        with app.app_context():
            response = client.post('/v1/auth/register', json={})
            
            assert response.status_code == 400
            assert 'Missing username, email or password' in get_error_message(response)

    @pytest.mark.integration
    def test_register_no_json(self, client, app):
        """Enregistrement échoue si pas de JSON."""
        with app.app_context():
            response = client.post('/v1/auth/register')
            
            assert response.status_code in [400, 415]  # 400 ou 415 (Unsupported Media Type)

    # === LOGIN ===

    @pytest.mark.integration
    def test_login_success(self, client, app):
        """Login réussi avec credentials valides."""
        with app.app_context():
            # Créer un utilisateur
            from werkzeug.security import generate_password_hash
            user = User(
                username='loginuser',
                email='login@test.com',
                password_hash=generate_password_hash('mypassword')
            )
            db.session.add(user)
            db.session.commit()
            
            # Tenter de se connecter
            response = client.post('/v1/auth/login', json={
                'username': 'loginuser',
                'password': 'mypassword'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'access_token' in data
            assert data['username'] == 'loginuser'
            assert len(data['access_token']) > 0

    @pytest.mark.integration
    def test_login_wrong_password(self, client, app):
        """Login échoue avec mauvais mot de passe."""
        with app.app_context():
            # Créer un utilisateur
            from werkzeug.security import generate_password_hash
            user = User(
                username='testuser',
                email='test@test.com',
                password_hash=generate_password_hash('correctpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            # Tenter de se connecter avec mauvais password
            response = client.post('/v1/auth/login', json={
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 401
            assert 'Invalid credentials' in get_error_message(response)

    @pytest.mark.integration
    def test_login_user_not_exists(self, client, app):
        """Login échoue si utilisateur n'existe pas."""
        with app.app_context():
            response = client.post('/v1/auth/login', json={
                'username': 'nonexistent',
                'password': 'password123'
            })
            
            assert response.status_code == 401
            assert 'Invalid credentials' in get_error_message(response)

    @pytest.mark.integration
    def test_login_missing_username(self, client, app):
        """Login échoue si username manquant."""
        with app.app_context():
            response = client.post('/v1/auth/login', json={
                'password': 'password123'
            })
            
            assert response.status_code == 400
            assert 'Missing username or password' in get_error_message(response)

    @pytest.mark.integration
    def test_login_missing_password(self, client, app):
        """Login échoue si password manquant."""
        with app.app_context():
            response = client.post('/v1/auth/login', json={
                'username': 'testuser'
            })
            
            assert response.status_code == 400
            assert 'Missing username or password' in get_error_message(response)

    @pytest.mark.integration
    def test_login_empty_json(self, client, app):
        """Login échoue si le JSON est vide."""
        with app.app_context():
            response = client.post('/v1/auth/login', json={})
            
            assert response.status_code == 400
            assert 'Missing username or password' in get_error_message(response)

    @pytest.mark.integration
    def test_login_no_json(self, client, app):
        """Login échoue si pas de JSON."""
        with app.app_context():
            response = client.post('/v1/auth/login')
            
            assert response.status_code in [400, 415]

    @pytest.mark.integration
    def test_login_returns_valid_jwt(self, client, app):
        """Le JWT retourné est valide et peut être utilisé."""
        with app.app_context():
            # Créer un utilisateur
            from werkzeug.security import generate_password_hash
            user = User(
                username='jwtuser',
                email='jwt@test.com',
                password_hash=generate_password_hash('password123')
            )
            db.session.add(user)
            db.session.commit()
            
            # Login
            response = client.post('/v1/auth/login', json={
                'username': 'jwtuser',
                'password': 'password123'
            })
            
            token = response.get_json()['access_token']
            
            # Utiliser le token pour accéder à une route protégée (ex: GET /contacts)
            response = client.get('/v1/contacts', headers={
                'Authorization': f'Bearer {token}'
            })
            
            # Doit réussir (200) et non 401 Unauthorized
            assert response.status_code == 200

    @pytest.mark.integration
    def test_register_then_login_workflow(self, client, app):
        """Workflow complet: register puis login."""
        with app.app_context():
            # 1. Register
            register_response = client.post('/v1/auth/register', json={
                'username': 'workflowuser',
                'email': 'workflow@test.com',
                'password': 'mypassword123'
            })
            
            assert register_response.status_code == 201
            
            # 2. Login avec les mêmes credentials
            login_response = client.post('/v1/auth/login', json={
                'username': 'workflowuser',
                'password': 'mypassword123'
            })
            
            assert login_response.status_code == 200
            assert 'access_token' in login_response.get_json()
            assert login_response.get_json()['username'] == 'workflowuser'
