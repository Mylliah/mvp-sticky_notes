"""
Tests pour la sécurisation des routes users.
"""
import pytest


class TestUsersSecurityRoutes:
    """Tests de sécurité des routes users."""
    
    def test_list_users_requires_auth(self, client):
        """Lister les users nécessite une authentification."""
        response = client.get('/v1/users')
        assert response.status_code == 401
    
    def test_get_user_requires_auth(self, client, user):
        """Récupérer un user nécessite une authentification."""
        response = client.get(f'/v1/users/{user.id}')
        assert response.status_code == 401
    
    def test_update_own_profile(self, client, auth_token, user):
        """Un utilisateur peut modifier son propre profil."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.put(
            f'/v1/users/{user.id}',
            headers=headers,
            json={'username': 'newusername'}
        )
        assert response.status_code == 200
    
    def test_update_other_user_profile_forbidden(self, client, auth_token, user, user2):
        """Un utilisateur ne peut pas modifier le profil d'un autre."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.put(
            f'/v1/users/{user2.id}',
            headers=headers,
            json={'username': 'hackername'}
        )
        assert response.status_code == 403
    
    def test_admin_can_update_any_profile(self, client, admin_token, user):
        """Un admin peut modifier n'importe quel profil."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.put(
            f'/v1/users/{user.id}',
            headers=headers,
            json={'username': 'adminchanged'}
        )
        assert response.status_code == 200
    
    def test_delete_own_account(self, client, auth_token, user):
        """Un utilisateur peut supprimer son propre compte."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.delete(f'/v1/users/{user.id}', headers=headers)
        assert response.status_code == 200
    
    def test_delete_other_user_account_forbidden(self, client, auth_token, user2):
        """Un utilisateur ne peut pas supprimer le compte d'un autre."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.delete(f'/v1/users/{user2.id}', headers=headers)
        assert response.status_code == 403
    
    def test_admin_can_delete_any_account(self, client, admin_token, user):
        """Un admin peut supprimer n'importe quel compte."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.delete(f'/v1/users/{user.id}', headers=headers)
        assert response.status_code == 200
    
    def test_update_requires_auth(self, client, user):
        """Modifier un profil nécessite une authentification."""
        response = client.put(
            f'/v1/users/{user.id}',
            json={'username': 'newname'}
        )
        assert response.status_code == 401
    
    def test_delete_requires_auth(self, client, user):
        """Supprimer un compte nécessite une authentification."""
        response = client.delete(f'/v1/users/{user.id}')
        assert response.status_code == 401
