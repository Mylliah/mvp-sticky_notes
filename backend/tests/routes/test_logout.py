"""
Tests pour l'endpoint POST /auth/logout
"""
import pytest
from app.models import ActionLog


class TestLogout:
    """Tests pour la déconnexion"""
    
    def test_logout_success(self, client, auth_headers, user):
        """Test déconnexion avec token valide"""
        response = client.post('/v1/auth/logout', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'msg' in data
        assert data['msg'] == "Successfully logged out"
    
    def test_logout_requires_auth(self, client):
        """Test que logout nécessite un token"""
        response = client.post('/v1/auth/logout')
        assert response.status_code == 401
    
    def test_logout_with_invalid_token(self, client):
        """Test logout avec token invalide"""
        headers = {'Authorization': 'Bearer invalid_token_123'}
        response = client.post('/v1/auth/logout', headers=headers)
        assert response.status_code in [401, 422]
    
    def test_logout_logs_action(self, client, auth_headers, user, app):
        """Test que la déconnexion est loggée"""
        with app.app_context():
            # Compter les logs avant
            initial_count = ActionLog.query.filter_by(
                user_id=user.id,
                action_type="user_logout"
            ).count()
            
            # Se déconnecter
            response = client.post('/v1/auth/logout', headers=auth_headers)
            assert response.status_code == 200
            
            # Vérifier qu'un log a été créé
            final_count = ActionLog.query.filter_by(
                user_id=user.id,
                action_type="user_logout"
            ).count()
            assert final_count == initial_count + 1
    
    def test_logout_multiple_times(self, client, auth_headers):
        """Test déconnexion multiple (le token reste valide jusqu'à expiration)"""
        # Première déconnexion
        response1 = client.post('/v1/auth/logout', headers=auth_headers)
        assert response1.status_code == 200
        
        # Deuxième déconnexion avec le même token (devrait fonctionner car JWT stateless)
        response2 = client.post('/v1/auth/logout', headers=auth_headers)
        assert response2.status_code == 200
    
    def test_logout_then_access_protected_route(self, client, auth_headers):
        """Test qu'après logout le token reste valide (JWT stateless)"""
        # Se déconnecter
        response = client.post('/v1/auth/logout', headers=auth_headers)
        assert response.status_code == 200
        
        # Tenter d'accéder à une route protégée
        # Devrait fonctionner car JWT est stateless (pas de blacklist pour l'instant)
        response = client.get('/v1/auth/me', headers=auth_headers)
        assert response.status_code == 200


class TestLogoutWorkflow:
    """Tests de workflows complets avec logout"""
    
    def test_login_logout_login_workflow(self, client, user):
        """Test du cycle complet login -> logout -> login"""
        # Login
        login_response = client.post('/v1/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        assert login_response.status_code == 200
        token1 = login_response.get_json()['access_token']
        
        # Logout
        logout_response = client.post('/v1/auth/logout', 
                                      headers={'Authorization': f'Bearer {token1}'})
        assert logout_response.status_code == 200
        
        # Re-login
        login_response2 = client.post('/v1/auth/login', json={
            'email': user.email,
            'password': 'password123'
        })
        assert login_response2.status_code == 200
        token2 = login_response2.get_json()['access_token']
        
        # Les tokens sont différents
        assert token1 != token2
    
    def test_register_auto_login_logout(self, client):
        """Test register (auto-login) puis logout"""
        # Register
        register_response = client.post('/v1/auth/register', json={
            'username': 'newuser_logout',
            'email': 'newuser_logout@example.com',
            'password': 'password123'
        })
        assert register_response.status_code == 201
        token = register_response.get_json()['access_token']
        
        # Logout immédiatement après registration
        logout_response = client.post('/v1/auth/logout',
                                      headers={'Authorization': f'Bearer {token}'})
        assert logout_response.status_code == 200
