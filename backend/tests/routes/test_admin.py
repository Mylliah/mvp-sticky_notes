"""
Tests pour les routes admin.
"""
import pytest


class TestAdminRoutes:
    """Tests des routes admin."""
    
    def test_list_users_as_admin(self, client, admin_token, user):
        """Un admin peut lister tous les utilisateurs."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.get('/v1/admin/users', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Au moins admin + user
    
    def test_list_users_as_regular_user(self, client, auth_token):
        """Un utilisateur normal ne peut pas lister tous les users (admin)."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/v1/admin/users', headers=headers)
        assert response.status_code == 403
    
    def test_list_users_without_auth(self, client):
        """Sans authentification, accès refusé."""
        response = client.get('/v1/admin/users')
        assert response.status_code == 401
    
    def test_list_all_notes_as_admin(self, client, admin_token, note):
        """Un admin peut lister toutes les notes."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.get('/v1/admin/notes', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_list_all_notes_as_regular_user(self, client, auth_token):
        """Un utilisateur normal ne peut pas lister toutes les notes."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/v1/admin/notes', headers=headers)
        assert response.status_code == 403
    
    def test_get_stats_as_admin(self, client, admin_token, user, note):
        """Un admin peut obtenir les statistiques."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.get('/v1/admin/stats', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_users' in data
        assert 'total_notes' in data
        assert 'total_contacts' in data
        assert 'total_assignments' in data
        assert data['total_users'] >= 2
        assert data['total_notes'] >= 1
    
    def test_get_stats_as_regular_user(self, client, auth_token):
        """Un utilisateur normal ne peut pas obtenir les stats."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/v1/admin/stats', headers=headers)
        assert response.status_code == 403
    
    def test_delete_user_as_admin(self, client, admin_token, user2):
        """Un admin peut supprimer n'importe quel utilisateur."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.delete(f'/v1/admin/users/{user2.id}', headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'User deleted'
    
    def test_delete_user_as_regular_user(self, client, auth_token, user2):
        """Un utilisateur normal ne peut pas supprimer via admin route."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.delete(f'/v1/admin/users/{user2.id}', headers=headers)
        assert response.status_code == 403
    
    def test_delete_nonexistent_user_as_admin(self, client, admin_token):
        """Supprimer un utilisateur inexistant retourne 404."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.delete('/v1/admin/users/999999', headers=headers)
        assert response.status_code == 404
    
    def test_update_user_role_as_admin(self, client, admin_token, user2):
        """Un admin peut changer le rôle d'un utilisateur."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.put(
            f'/v1/admin/users/{user2.id}/role',
            headers=headers,
            json={'role': 'admin'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['role'] == 'admin'
        assert data['message'] == 'User role updated'
    
    def test_update_user_role_as_regular_user(self, client, auth_token, user2):
        """Un utilisateur normal ne peut pas changer les rôles."""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.put(
            f'/v1/admin/users/{user2.id}/role',
            headers=headers,
            json={'role': 'admin'}
        )
        assert response.status_code == 403
    
    def test_update_user_role_invalid_role(self, client, admin_token, user2):
        """Un rôle invalide est rejeté."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.put(
            f'/v1/admin/users/{user2.id}/role',
            headers=headers,
            json={'role': 'superadmin'}
        )
        assert response.status_code == 400
    
    def test_update_user_role_missing_role(self, client, admin_token, user2):
        """Un changement de rôle sans le champ 'role' est rejeté."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.put(
            f'/v1/admin/users/{user2.id}/role',
            headers=headers,
            json={}
        )
        assert response.status_code == 400
    
    def test_update_nonexistent_user_role(self, client, admin_token):
        """Changer le rôle d'un utilisateur inexistant retourne 404."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = client.put(
            '/v1/admin/users/999999/role',
            headers=headers,
            json={'role': 'admin'}
        )
        assert response.status_code == 404
