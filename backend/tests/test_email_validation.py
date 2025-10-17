"""
Tests pour la validation stricte des emails.
"""
import pytest
from app.models import User
from app import db


class TestEmailValidation:
    """Tests pour la validation des emails avec email-validator."""
    
    def test_valid_email_accepted(self, app):
        """Un email valide est accepté."""
        user = User(username="test", email="test@example.com", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        
        assert user.email == "test@example.com"
    
    def test_email_normalized_to_lowercase(self, app):
        """Les emails sont normalisés en minuscules."""
        user = User(username="test", email="TEST@EXAMPLE.COM", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        
        assert user.email == "test@example.com"
    
    def test_invalid_email_rejected(self, app):
        """Un email invalide est rejeté."""
        with pytest.raises(ValueError) as exc_info:
            user = User(username="test", email="not-an-email", password_hash="hash")
            db.session.add(user)
            db.session.commit()
        
        assert "Format d'email invalide" in str(exc_info.value)
        db.session.rollback()
    
    def test_email_without_at_rejected(self, app):
        """Un email sans @ est rejeté."""
        with pytest.raises(ValueError):
            user = User(username="test", email="notemail.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
        
        db.session.rollback()
    
    def test_email_without_domain_rejected(self, app):
        """Un email sans domaine est rejeté."""
        with pytest.raises(ValueError):
            user = User(username="test", email="test@", password_hash="hash")
            db.session.add(user)
            db.session.commit()
        
        db.session.rollback()
    
    def test_email_with_multiple_at_rejected(self, app):
        """Un email avec plusieurs @ est rejeté."""
        with pytest.raises(ValueError):
            user = User(username="test", email="test@@example.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
        
        db.session.rollback()
    
    def test_empty_email_rejected(self, app):
        """Un email vide est rejeté."""
        with pytest.raises(ValueError) as exc_info:
            user = User(username="test", email="", password_hash="hash")
            db.session.add(user)
            db.session.commit()
        
        assert "vide" in str(exc_info.value).lower()
        db.session.rollback()
    
    def test_whitespace_only_email_rejected(self, app):
        """Un email avec seulement des espaces est rejeté."""
        with pytest.raises(ValueError):
            user = User(username="test", email="   ", password_hash="hash")
            db.session.add(user)
            db.session.commit()
        
        db.session.rollback()
    
    def test_email_with_spaces_trimmed(self, app):
        """Les espaces autour de l'email sont supprimés."""
        user = User(username="test", email="  test@example.com  ", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        
        assert user.email == "test@example.com"
    
    def test_complex_valid_email_accepted(self, app):
        """Un email complexe mais valide est accepté."""
        user = User(username="test", email="user.name+tag@example.co.uk", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        
        assert user.email == "user.name+tag@example.co.uk"


class TestEmailValidationInRegistration:
    """Tests pour la validation des emails dans la route d'enregistrement."""
    
    def test_registration_with_valid_email(self, client, app):
        """L'enregistrement avec un email valide fonctionne."""
        response = client.post('/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        assert response.status_code == 201
        assert response.json['email'] == 'test@example.com'
    
    def test_registration_with_invalid_email(self, client, app):
        """L'enregistrement avec un email invalide échoue."""
        response = client.post('/v1/auth/register', json={
            'username': 'testuser',
            'email': 'not-an-email',
            'password': 'Password123!'
        })
        
        assert response.status_code == 400
        assert b'Invalid email format' in response.data or b'email' in response.data.lower()
    
    def test_registration_normalizes_email(self, client, app):
        """L'enregistrement normalise l'email."""
        response = client.post('/v1/auth/register', json={
            'username': 'testuser',
            'email': 'TEST@EXAMPLE.COM',
            'password': 'Password123!'
        })
        
        assert response.status_code == 201
        assert response.json['email'] == 'test@example.com'
    
    def test_registration_with_email_missing_domain(self, client, app):
        """L'enregistrement avec un email sans domaine échoue."""
        response = client.post('/v1/auth/register', json={
            'username': 'testuser',
            'email': 'test@',
            'password': 'Password123!'
        })
        
        assert response.status_code == 400
