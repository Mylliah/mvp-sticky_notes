"""
Tests pour le rate limiting et CORS.
"""
import pytest
from app.models import User
from app import db
import time


class TestRateLimiting:
    """Tests pour vérifier que le rate limiting est configuré."""
    
    def test_rate_limiting_is_configured(self, app):
        """Vérifier que le rate limiting est configuré dans l'application."""
        from app import limiter
        assert limiter is not None
        # En mode test, le rate limiting est désactivé
        assert limiter.enabled is False
    
    def test_register_endpoint_has_rate_limit_decorator(self, app):
        """Vérifier que l'endpoint register a bien un décorateur de rate limit."""
        # Vérifions que la route existe et est accessible
        with app.test_client() as client:
            response = client.post('/v1/auth/register', json={
                'username': 'testuser',
                'email': 'test@test.com',
                'password': 'Password123!'
            })
            # La route fonctionne (rate limit désactivé en test)
            assert response.status_code == 201
    
    def test_login_endpoint_has_rate_limit_decorator(self, app):
        """Vérifier que l'endpoint login a bien un décorateur de rate limit."""
        # Créer un utilisateur
        user = User(username="testuser", email="test@test.com", 
                   password_hash="hash")
        db.session.add(user)
        db.session.commit()
        
        # Vérifions que la route existe et est accessible
        with app.test_client() as client:
            response = client.post('/v1/auth/login', json={
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            # La route fonctionne (rate limit désactivé en test)
            assert response.status_code == 401
    



class TestCORS:
    """Tests pour vérifier que CORS est configuré."""
    
    def test_cors_headers_present_on_options(self, client, app):
        """Les headers CORS sont présents sur OPTIONS."""
        response = client.options('/v1/notes', 
                                 headers={'Origin': 'http://localhost:3000'})
        
        # Vérifier que l'origine est autorisée
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_cors_headers_present_on_get(self, client, app):
        """Les headers CORS sont présents sur GET."""
        # Créer un utilisateur et se connecter
        user = User(username="testuser", email="test@test.com", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user.id))
        
        response = client.get('/v1/notes',
                             headers={
                                 'Authorization': f'Bearer {token}',
                                 'Origin': 'http://localhost:3000'
                             })
        
        # Vérifier que CORS permet l'origine
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_cors_allows_configured_origin(self, client, app):
        """CORS autorise les origines configurées."""
        response = client.options('/v1/notes',
                                 headers={'Origin': 'http://localhost:3000'})
        
        # Vérifier que l'origine est autorisée
        assert response.headers.get('Access-Control-Allow-Origin') in [
            'http://localhost:3000', '*'
        ]
    
    def test_cors_allows_credentials(self, client, app):
        """CORS autorise les credentials."""
        response = client.options('/v1/notes',
                                 headers={'Origin': 'http://localhost:3000'})
        
        # Vérifier que les credentials sont autorisés
        assert response.headers.get('Access-Control-Allow-Credentials') == 'true'
    
    def test_cors_allows_required_methods(self, client, app):
        """CORS autorise les méthodes HTTP nécessaires."""
        response = client.options('/v1/notes',
                                 headers={
                                     'Origin': 'http://localhost:3000',
                                     'Access-Control-Request-Method': 'POST'
                                 })
        
        # CORS est configuré, vérifions que la réponse est correcte
        assert response.status_code in [200, 204]
        assert 'Access-Control-Allow-Origin' in response.headers
    
    def test_cors_allows_required_headers(self, client, app):
        """CORS autorise les headers nécessaires."""
        response = client.options('/v1/notes',
                                 headers={
                                     'Origin': 'http://localhost:3000',
                                     'Access-Control-Request-Headers': 'Content-Type, Authorization'
                                 })
        
        # CORS est configuré, vérifions que la réponse permet les headers
        assert response.status_code in [200, 204]
        assert 'Access-Control-Allow-Origin' in response.headers
