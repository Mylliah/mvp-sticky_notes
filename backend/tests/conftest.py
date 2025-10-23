"""
Configuration des tests pour l'application Flask.
Ce module contient les fixtures pytest pour les tests.
"""
import os
import tempfile
import pytest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
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


# Alias pour compatibilité avec les nouveaux tests
@pytest.fixture
def user(app):
    """Créer un utilisateur de test (avec password hashé)."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        yield user
        # Cleanup
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture
def user2(app):
    """Créer un deuxième utilisateur de test."""
    with app.app_context():
        user = User(
            username='testuser2',
            email='test2@example.com',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        yield user
        # Cleanup
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture
def admin_user(app):
    """Créer un utilisateur admin de test."""
    with app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        db.session.refresh(admin)
        yield admin
        # Cleanup
        try:
            db.session.delete(admin)
            db.session.commit()
        except:
            db.session.rollback()


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
            important=False
        )
        db.session.add(note)
        db.session.commit()
        return note


@pytest.fixture
def note(app, user):
    """Créer une note de test."""
    with app.app_context():
        note = Note(
            content='This is a test note',
            creator_id=user.id,
            important=False
        )
        db.session.add(note)
        db.session.commit()
        db.session.refresh(note)
        yield note
        # Cleanup
        try:
            db.session.delete(note)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture
def contact(app, user):
    """Créer un contact de test."""
    with app.app_context():
        contact = Contact(
            nom='Doe',
            prenom='John',
            email='john.doe@example.com',
            user_id=user.id
        )
        db.session.add(contact)
        db.session.commit()
        db.session.refresh(contact)
        yield contact
        # Cleanup
        try:
            db.session.delete(contact)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture
def assignment(app, note, contact):
    """Créer une assignation de test."""
    with app.app_context():
        assignment = Assignment(
            note_id=note.id,
            contact_id=contact.id
        )
        db.session.add(assignment)
        db.session.commit()
        db.session.refresh(assignment)
        yield assignment
        # Cleanup
        try:
            db.session.delete(assignment)
            db.session.commit()
        except:
            db.session.rollback()


@pytest.fixture
def auth_token(app, user):
    """Créer un token JWT pour l'utilisateur de test."""
    with app.app_context():
        return create_access_token(identity=str(user.id))


@pytest.fixture
def admin_token(app, admin_user):
    """Créer un token JWT pour l'admin de test."""
    with app.app_context():
        return create_access_token(identity=str(admin_user.id))


@pytest.fixture
def authenticated_headers(client, sample_user):
    """Fixture pour obtenir les headers d'authentification."""
    # Simuler une connexion pour obtenir un token JWT
    response = client.post('/v1/auth/login', json={
        'email': sample_user.email,
        'password': 'test_password'
    })
    
    if response.status_code == 200:
        token = response.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}
    
    return {}


@pytest.fixture
def auth_headers(app, user):
    """Créer des headers d'authentification avec token JWT."""
    with app.app_context():
        token = create_access_token(identity=str(user.id))
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def test_user(client):
    """Créer un utilisateur et retourner ses infos avec token."""
    user_data = {
        "username": "testuser_search",
        "email": "testsearch@example.com",
        "password": "testpass123"
    }
    response = client.post('/v1/auth/register', json=user_data)
    data = response.get_json()
    
    return {
        "id": data["id"],
        "username": data["username"],
        "email": data["email"],
        "token": data["access_token"]
    }
