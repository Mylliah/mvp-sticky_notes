"""
Tests de sécurité pour les routes Action Logs.
Vérifie que seuls les admins peuvent CONSULTER les logs (lecture seule).

Les logs sont créés automatiquement par le système, donc ces tests
vérifient uniquement les permissions de lecture.
"""
import pytest
from flask_jwt_extended import create_access_token
from app.models import User, ActionLog
from app import db


class TestActionLogsAdminOnly:
    """Tests pour vérifier que seuls les admins peuvent CONSULTER les action logs (lecture seule)."""
    
    def test_non_admin_cannot_list_action_logs(self, client, app):
        """Un utilisateur non-admin ne peut pas lister les action logs."""
        with app.app_context():
            # Créer un utilisateur normal (non-admin)
            user = User(username="alice", email="alice@test.com", password_hash="hash", role="user")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Créer un log
            log = ActionLog(
                user_id=user_id,
                action_type="test_action",
                target_id=1,
                payload='{"test": "data"}'
            )
            db.session.add(log)
            db.session.commit()
            
            # Générer token pour utilisateur normal
            token = create_access_token(identity=str(user_id))
            
            # Tenter d'accéder aux logs
            response = client.get(
                '/v1/action_logs',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 403
            assert b'Admin access required' in response.data
    
    def test_admin_can_list_action_logs(self, client, app):
        """Un admin peut lister tous les action logs."""
        with app.app_context():
            # Créer un admin
            admin = User(username="admin", email="admin@test.com", password_hash="hash", role="admin")
            db.session.add(admin)
            db.session.commit()
            admin_id = admin.id
            
            # Créer plusieurs logs
            log1 = ActionLog(user_id=admin_id, action_type="test_action1", target_id=1, payload='{}')
            log2 = ActionLog(user_id=admin_id, action_type="test_action2", target_id=2, payload='{}')
            db.session.add_all([log1, log2])
            db.session.commit()
            
            # Générer token pour admin
            token = create_access_token(identity=str(admin_id))
            
            # Accéder aux logs
            response = client.get(
                '/v1/action_logs',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.json
            assert 'logs' in data
            assert data['total'] >= 2
    
    def test_non_admin_cannot_get_specific_log(self, client, app):
        """Un utilisateur non-admin ne peut pas récupérer un log spécifique."""
        with app.app_context():
            # Créer utilisateur normal
            user = User(username="bob", email="bob@test.com", password_hash="hash", role="user")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Créer un log
            log = ActionLog(user_id=user_id, action_type="test_action", target_id=1, payload='{}')
            db.session.add(log)
            db.session.commit()
            log_id = log.id
            
            # Token utilisateur normal
            token = create_access_token(identity=str(user_id))
            
            # Tenter d'accéder au log
            response = client.get(
                f'/v1/action_logs/{log_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 403
            assert b'Admin access required' in response.data
    
    def test_admin_can_get_specific_log(self, client, app):
        """Un admin peut récupérer un log spécifique."""
        with app.app_context():
            # Créer admin
            admin = User(username="admin2", email="admin2@test.com", password_hash="hash", role="admin")
            db.session.add(admin)
            db.session.commit()
            admin_id = admin.id
            
            # Créer un log
            log = ActionLog(user_id=admin_id, action_type="test_action", target_id=1, payload='{"key": "value"}')
            db.session.add(log)
            db.session.commit()
            log_id = log.id
            
            # Token admin
            token = create_access_token(identity=str(admin_id))
            
            # Accéder au log
            response = client.get(
                f'/v1/action_logs/{log_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.json
            assert data['id'] == log_id
            assert data['action_type'] == 'test_action'
    
    # NOTE: Tests de création manuelle supprimés - Les logs sont créés automatiquement
    # par le système et sont IMMUABLES (pas de POST/PUT/DELETE)
    
    def test_non_admin_cannot_get_stats(self, client, app):
        """Un utilisateur non-admin ne peut pas accéder aux stats."""
        with app.app_context():
            # Créer utilisateur normal
            user = User(username="david", email="david@test.com", password_hash="hash", role="user")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Token utilisateur normal
            token = create_access_token(identity=str(user_id))
            
            # Tenter d'accéder aux stats
            response = client.get(
                '/v1/action_logs/stats',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 403
            assert b'Admin access required' in response.data
    
    def test_admin_can_get_stats(self, client, app):
        """Un admin peut accéder aux stats globales."""
        with app.app_context():
            # Créer admin
            admin = User(username="admin4", email="admin4@test.com", password_hash="hash", role="admin")
            db.session.add(admin)
            db.session.commit()
            admin_id = admin.id
            
            # Créer quelques logs
            log1 = ActionLog(user_id=admin_id, action_type="type1", target_id=1, payload='{}')
            log2 = ActionLog(user_id=admin_id, action_type="type2", target_id=2, payload='{}')
            db.session.add_all([log1, log2])
            db.session.commit()
            
            # Token admin
            token = create_access_token(identity=str(admin_id))
            
            # Accéder aux stats
            response = client.get(
                '/v1/action_logs/stats',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.json
            assert 'action_counts' in data
            assert 'user_counts' in data
