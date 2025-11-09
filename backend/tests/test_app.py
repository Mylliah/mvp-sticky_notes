"""
Tests pour les routes de base de l'application et les handlers d'erreur.
"""
import pytest
from flask_jwt_extended import create_access_token
from datetime import timedelta


class TestAppBasics:
    """Tests pour les routes de base et la gestion d'erreurs globale."""
    
    def test_health_check(self, client):
        """La route /health devrait retourner un statut OK."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
    
    def test_invalid_route_returns_404(self, client):
        """Une route inexistante devrait retourner 404."""
        response = client.get('/route/qui/nexiste/pas')
        assert response.status_code == 404
    
    def test_expired_token_handled(self, client, app):
        """Un token JWT expiré devrait retourner 401 avec message approprié."""
        with app.app_context():
            # Créer un token qui expire immédiatement
            expired_token = create_access_token(
                identity='999',  # identity doit être une string
                expires_delta=timedelta(seconds=-1)  # Déjà expiré
            )
        
        response = client.get('/v1/notes',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        # Notre custom handler retourne "Token expired"
        assert data['error'] == 'Token expired'
    
    def test_invalid_token_handled(self, client):
        """Un token JWT invalide devrait retourner 401."""
        response = client.get('/v1/notes',
            headers={'Authorization': 'Bearer token_completement_invalide'}
        )
        assert response.status_code == 401
        data = response.get_json()
        # Notre custom handler retourne format standard avec 'error' et 'message'
        assert 'error' in data
        assert data['error'] == 'Invalid token'
    
    def test_missing_token_handled(self, client):
        """Une requête sans token sur une route protégée devrait retourner 401."""
        response = client.get('/v1/notes')
        assert response.status_code == 401
        data = response.get_json()
        # Notre custom handler retourne format standard avec 'error' et 'message'
        assert 'error' in data
        assert data['error'] == 'Missing authorization'
