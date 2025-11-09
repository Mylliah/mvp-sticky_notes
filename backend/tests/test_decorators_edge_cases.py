"""
Tests pour les décorateurs et edge cases.
"""
import pytest
from app import db
from app.models import User
from flask_jwt_extended import create_access_token


class TestAdminDecorator:
    """Tests pour le décorateur @admin_required."""
    
    @pytest.mark.integration
    def test_admin_decorator_with_deleted_user(self, client, app):
        """Tester le décorateur avec un utilisateur supprimé."""
        with app.app_context():
            # Créer un admin puis le supprimer
            admin = User(username='deleted_admin', email='deleted@test.com', password_hash='hash', role='admin')
            db.session.add(admin)
            db.session.commit()
            
            admin_id = admin.id
            token = create_access_token(identity=str(admin_id))
            
            # Supprimer l'admin
            db.session.delete(admin)
            db.session.commit()
            
            # Tenter d'utiliser le token
            response = client.get(
                '/v1/admin/users',
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Devrait retourner 404 car l'utilisateur n'existe plus
            assert response.status_code == 404
            assert b'User not found' in response.data


class TestUsersUpdateValidation:
    """Tests pour les validations de mise à jour utilisateur."""
    
    @pytest.mark.integration
    def test_update_other_user_as_non_admin(self, client, app):
        """Un utilisateur normal ne peut pas modifier un autre utilisateur."""
        with app.app_context():
            user1 = User(username='alice', email='alice@test.com', password_hash='hash')
            user2 = User(username='bob', email='bob@test.com', password_hash='hash')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            token = create_access_token(identity=str(user1.id))
            response = client.put(
                f'/v1/users/{user2.id}',
                json={'username': 'modified_bob'},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403
            assert b'not authorized' in response.data or b'Forbidden' in response.data
