"""
Tests pour les routes de consultation des logs d'actions (lecture seule).

Les logs sont créés automatiquement par le système, donc ces tests
se concentrent uniquement sur la lecture et les statistiques.
"""
import pytest
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, ActionLog


def create_user(app, username, email, password):
    """Helper pour créer un utilisateur."""
    with app.app_context():
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return user.id


def create_action_log(app, user_id, action_type, target_id=1, payload=None):
    """Helper pour créer un log d'action."""
    with app.app_context():
        log = ActionLog(
            user_id=user_id,
            action_type=action_type,
            target_id=target_id,
            payload=payload,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        db.session.commit()
        return log.id


def get_error_message(response):
    """Helper pour extraire le message d'erreur de la réponse."""
    data = response.get_json()
    if data is None:
        return ""
    return data.get('description') or data.get('message') or data.get('error') or str(data)


class TestActionLogsRoutes:
    """Tests pour les endpoints de consultation des logs d'actions (lecture seule)."""

    # NOTE: Pas de tests POST/PUT/DELETE - Les logs sont IMMUABLES et créés automatiquement

    # === GET /action_logs - Lister les logs d'actions ===

    @pytest.mark.integration
    def test_list_action_logs_empty(self, client, app, admin_token):
        """Lister les logs quand il n'y en a aucun."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with app.app_context():
            response = client.get('/v1/action_logs', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['logs'] == []
            assert data['total'] == 0
            assert data['page'] == 1
            assert data['pages'] == 0

    @pytest.mark.integration
    def test_list_action_logs_with_logs(self, client, app, user, admin_token):
        """Lister les logs existants."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        log_id1 = create_action_log(app, user.id, 'CREATE')
        log_id2 = create_action_log(app, user.id, 'UPDATE')
        
        with app.app_context():
            response = client.get('/v1/action_logs', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['logs']) == 2
            assert data['total'] == 2
            # Ordre décroissant (plus récent d'abord)
            assert data['logs'][0]['action_type'] == 'UPDATE'
            assert data['logs'][1]['action_type'] == 'CREATE'

    @pytest.mark.integration
    def test_list_action_logs_pagination(self, client, app, user, admin_token):
        """Tester la pagination des logs."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with app.app_context():
            # Créer 5 logs
            for i in range(5):
                create_action_log(app, user.id, f'ACTION_{i}')
            
            # Page 1 avec 2 par page
            response = client.get('/v1/action_logs?page=1&per_page=2', headers=headers)
            data = response.get_json()
            
            assert response.status_code == 200
            assert len(data['logs']) == 2
            assert data['total'] == 5
            assert data['page'] == 1
            assert data['per_page'] == 2
            assert data['pages'] == 3

    @pytest.mark.integration
    def test_list_action_logs_filter_by_user(self, client, app, user, user2, admin_token):
        """Filtrer les logs par utilisateur."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with app.app_context():
            create_action_log(app, user.id, 'CREATE')
            create_action_log(app, user.id, 'UPDATE')
            create_action_log(app, user2.id, 'DELETE')
            
            response = client.get(f'/v1/action_logs?user_id={user.id}', headers=headers)
            data = response.get_json()
            
            assert response.status_code == 200
            assert len(data['logs']) == 2
            assert all(log['user_id'] == user.id for log in data['logs'])

    @pytest.mark.integration
    def test_list_action_logs_filter_by_action_type(self, client, app, user, admin_token):
        """Filtrer les logs par type d'action."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with app.app_context():
            create_action_log(app, user.id, 'CREATE')
            create_action_log(app, user.id, 'CREATE')
            create_action_log(app, user.id, 'UPDATE')
            
            response = client.get('/v1/action_logs?action_type=CREATE', headers=headers)
            data = response.get_json()
            
            assert response.status_code == 200
            assert len(data['logs']) == 2
            assert all(log['action_type'] == 'CREATE' for log in data['logs'])

    @pytest.mark.integration
    def test_list_action_logs_multiple_filters(self, client, app, user, user2, admin_token):
        """Combiner plusieurs filtres."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with app.app_context():
            create_action_log(app, user.id, 'CREATE', target_id=1)
            create_action_log(app, user.id, 'UPDATE', target_id=2)
            create_action_log(app, user2.id, 'CREATE', target_id=3)
            create_action_log(app, user.id, 'CREATE', target_id=4)
            
            response = client.get(f'/v1/action_logs?user_id={user.id}&action_type=CREATE', headers=headers)
            data = response.get_json()
            
            assert response.status_code == 200
            assert len(data['logs']) == 2
            assert all(log['user_id'] == user.id for log in data['logs'])
            assert all(log['action_type'] == 'CREATE' for log in data['logs'])

    # === GET /action_logs/<id> - Récupérer un log ===

    @pytest.mark.integration
    def test_get_action_log_success(self, client, app, user, admin_token):
        """Récupérer un log par son ID."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        log_id = create_action_log(app, user.id, 'CREATE')
        
        with app.app_context():
            response = client.get(f'/v1/action_logs/{log_id}', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == log_id
            assert data['action_type'] == 'CREATE'

    @pytest.mark.integration
    def test_get_action_log_not_found(self, client, app, admin_token):
        """Récupérer un log inexistant retourne 404."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with app.app_context():
            response = client.get('/v1/action_logs/99999', headers=headers)
            
            assert response.status_code == 404

    # === GET /action_logs/stats - Récupérer les statistiques ===

    @pytest.mark.integration
    def test_get_action_log_stats_empty(self, client, app, admin_token):
        """Récupérer les stats quand il n'y a aucun log."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with app.app_context():
            response = client.get('/v1/action_logs/stats', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['action_counts'] == []
            assert data['user_counts'] == []

    @pytest.mark.integration
    def test_get_action_log_stats_with_data(self, client, app, user, user2, admin_token):
        """Récupérer les stats avec des logs."""
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        with app.app_context():
            # user1: 3 CREATE, 2 UPDATE
            create_action_log(app, user.id, 'CREATE')
            create_action_log(app, user.id, 'CREATE')
            create_action_log(app, user.id, 'CREATE')
            create_action_log(app, user.id, 'UPDATE')
            create_action_log(app, user.id, 'UPDATE')
            
            # user2: 1 DELETE
            create_action_log(app, user2.id, 'DELETE')
            
            response = client.get('/v1/action_logs/stats', headers=headers)
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Vérifier les comptes par action
            action_counts = {item['action_type']: item['count'] for item in data['action_counts']}
            assert action_counts['CREATE'] == 3
            assert action_counts['UPDATE'] == 2
            assert action_counts['DELETE'] == 1
            
            # Vérifier les comptes par utilisateur
            user_counts = {item['user_id']: item['count'] for item in data['user_counts']}
            assert user_counts[user.id] == 5
            assert user_counts[user2.id] == 1
