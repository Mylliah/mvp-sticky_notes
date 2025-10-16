"""
Configuration pytest et fixtures partagées.
"""
import pytest
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models import User, Note, Contact, Assignment


@pytest.fixture(scope='session')
def app():
    """Créer l'application Flask pour les tests."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@db:5432/test_db'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Client de test Flask."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner pour les tests."""
    return app.test_cli_runner()


@pytest.fixture
def user(app):
    """Créer un utilisateur de test."""
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
        db.session.delete(user)
        db.session.commit()


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
        db.session.delete(admin)
        db.session.commit()


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
def note(app, user):
    """Créer une note de test."""
    with app.app_context():
        note = Note(
            title='Test Note',
            content='This is a test note',
            statut='en_cours',
            important=False,
            user_id=user.id
        )
        db.session.add(note)
        db.session.commit()
        db.session.refresh(note)
        yield note
        # Cleanup
        db.session.delete(note)
        db.session.commit()


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
        db.session.delete(contact)
        db.session.commit()


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
        db.session.delete(assignment)
        db.session.commit()
