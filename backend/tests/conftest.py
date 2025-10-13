"""
Configuration des tests pour l'application Flask.
Ce module contient les fixtures pytest pour les tests.
"""
import os
import tempfile
import pytest
from app import create_app, db
from app.models import User, Note, Contact, Assignment, ActionLog


@pytest.fixture
def app():
    """Fixture pour créer une instance de l'application Flask de test."""
    # Créer un fichier de base de données temporaire
    db_fd, db_path = tempfile.mkstemp()
    
    # Configuration de test
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'SECRET_KEY': 'test-secret-key'
    }
    
    # Créer l'app avec la config de test
    app = create_app(test_config)
    
    # Créer les tables de test
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Nettoyer
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Fixture pour créer un client de test."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture pour créer un runner de commandes CLI."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Fixture pour créer un utilisateur de test."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_users(app):
    """Fixture pour créer plusieurs utilisateurs de test."""
    with app.app_context():
        users = []
        for i in range(3):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password_hash=f'hashed_password{i}'
            )
            db.session.add(user)
            users.append(user)
        db.session.commit()
        return users


@pytest.fixture
def sample_note(app, sample_user):
    """Fixture pour créer une note de test."""
    with app.app_context():
        note = Note(
            content='Test note content',
            creator_id=sample_user.id,
            status='en_cours',
            important=False
        )
        db.session.add(note)
        db.session.commit()
        return note


@pytest.fixture
def authenticated_headers(client, sample_user):
    """Fixture pour obtenir les headers d'authentification."""
    # Simuler une connexion pour obtenir un token JWT
    response = client.post('/v1/auth/login', json={
        'username': sample_user.username,
        'password': 'test_password'
    })
    
    if response.status_code == 200:
        token = response.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}
    
    return {}