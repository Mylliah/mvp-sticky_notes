"""
Tests pour les routes de gestion des logs d'actions.
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
    """Tests pour les endpoints de logs d'actions."""

    # === POST /action_logs - Créer un log d'action ===

    @pytest.mark.integration
    def test_create_action_log_success(self, client, app):
        """Créer un log d'action avec succès."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/action_logs', json={
                'user_id': user_id,
                'action_type': 'CREATE',
                'target_id': 1
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['user_id'] == user_id
            assert data['action_type'] == 'CREATE'
            assert data['target_id'] == 1
            assert data['timestamp'] is not None

    @pytest.mark.integration
    def test_create_action_log_with_all_fields(self, client, app):
        """Créer un log d'action avec tous les champs."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/action_logs', json={
                'user_id': user_id,
                'action_type': 'UPDATE',
                'target_id': 123,
                'payload': 'Updated note content'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['action_type'] == 'UPDATE'
            assert data['target_id'] == 123
            assert data['payload'] == 'Updated note content'

    @pytest.mark.integration
    def test_create_action_log_missing_user_id(self, client, app):
        """Créer un log sans user_id échoue."""
        with app.app_context():
            response = client.post('/v1/action_logs', json={
                'action_type': 'CREATE',
                'target_id': 1
            })
            
            assert response.status_code == 400
            message = get_error_message(response)
            assert 'user_id' in message.lower()

    @pytest.mark.integration
    def test_create_action_log_missing_action_type(self, client, app):
        """Créer un log sans action_type échoue."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/action_logs', json={
                'user_id': user_id,
                'target_id': 1
            })
            
            assert response.status_code == 400
            message = get_error_message(response)
            assert 'action_type' in message.lower()
    
    @pytest.mark.integration
    def test_create_action_log_missing_target_id(self, client, app):
        """Créer un log sans target_id échoue."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/action_logs', json={
                'user_id': user_id,
                'action_type': 'CREATE'
            })
            
            assert response.status_code == 400
            message = get_error_message(response)
            assert 'target_id' in message.lower()

    @pytest.mark.integration
    def test_create_action_log_user_not_found(self, client, app):
        """Créer un log avec utilisateur inexistant échoue."""
        with app.app_context():
            response = client.post('/v1/action_logs', json={
                'user_id': 99999,
                'action_type': 'CREATE',
                'target_id': 1
            })
            
            assert response.status_code == 400
            message = get_error_message(response)
            assert 'User not found' in message

    # === GET /action_logs - Lister les logs d'actions ===

    @pytest.mark.integration
    def test_list_action_logs_empty(self, client, app):
        """Lister les logs quand il n'y en a aucun."""
        with app.app_context():
            response = client.get('/v1/action_logs')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['logs'] == []
            assert data['total'] == 0
            assert data['page'] == 1
            assert data['pages'] == 0

    @pytest.mark.integration
    def test_list_action_logs_with_logs(self, client, app):
        """Lister les logs existants."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        log_id1 = create_action_log(app, user_id, 'CREATE')
        log_id2 = create_action_log(app, user_id, 'UPDATE')
        
        with app.app_context():
            response = client.get('/v1/action_logs')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['logs']) == 2
            assert data['total'] == 2
            # Ordre décroissant (plus récent d'abord)
            assert data['logs'][0]['action_type'] == 'UPDATE'
            assert data['logs'][1]['action_type'] == 'CREATE'

    @pytest.mark.integration
    def test_list_action_logs_pagination(self, client, app):
        """Tester la pagination des logs."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer 5 logs
            for i in range(5):
                create_action_log(app, user_id, f'ACTION_{i}')
            
            # Page 1 avec 2 par page
            response = client.get('/v1/action_logs?page=1&per_page=2')
            data = response.get_json()
            
            assert response.status_code == 200
            assert len(data['logs']) == 2
            assert data['total'] == 5
            assert data['page'] == 1
            assert data['per_page'] == 2
            assert data['pages'] == 3

    @pytest.mark.integration
    def test_list_action_logs_filter_by_user(self, client, app):
        """Filtrer les logs par utilisateur."""
        user_id1 = create_user(app, 'user1', 'user1@test.com', 'pass')
        user_id2 = create_user(app, 'user2', 'user2@test.com', 'pass')
        
        with app.app_context():
            create_action_log(app, user_id1, 'CREATE')
            create_action_log(app, user_id1, 'UPDATE')
            create_action_log(app, user_id2, 'DELETE')
            
            response = client.get(f'/v1/action_logs?user_id={user_id1}')
            data = response.get_json()
            
            assert response.status_code == 200
            assert len(data['logs']) == 2
            assert all(log['user_id'] == user_id1 for log in data['logs'])

    @pytest.mark.integration
    def test_list_action_logs_filter_by_action_type(self, client, app):
        """Filtrer les logs par type d'action."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            create_action_log(app, user_id, 'CREATE')
            create_action_log(app, user_id, 'CREATE')
            create_action_log(app, user_id, 'UPDATE')
            
            response = client.get('/v1/action_logs?action_type=CREATE')
            data = response.get_json()
            
            assert response.status_code == 200
            assert len(data['logs']) == 2
            assert all(log['action_type'] == 'CREATE' for log in data['logs'])

    @pytest.mark.integration
    def test_list_action_logs_multiple_filters(self, client, app):
        """Combiner plusieurs filtres."""
        user_id1 = create_user(app, 'user1', 'user1@test.com', 'pass')
        user_id2 = create_user(app, 'user2', 'user2@test.com', 'pass')
        
        with app.app_context():
            create_action_log(app, user_id1, 'CREATE', target_id=1)
            create_action_log(app, user_id1, 'UPDATE', target_id=2)
            create_action_log(app, user_id2, 'CREATE', target_id=3)
            create_action_log(app, user_id1, 'CREATE', target_id=4)
            
            response = client.get(f'/v1/action_logs?user_id={user_id1}&action_type=CREATE')
            data = response.get_json()
            
            assert response.status_code == 200
            assert len(data['logs']) == 2
            assert all(log['user_id'] == user_id1 for log in data['logs'])
            assert all(log['action_type'] == 'CREATE' for log in data['logs'])

    # === GET /action_logs/<id> - Récupérer un log ===

    @pytest.mark.integration
    def test_get_action_log_success(self, client, app):
        """Récupérer un log par son ID."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        log_id = create_action_log(app, user_id, 'CREATE')
        
        with app.app_context():
            response = client.get(f'/v1/action_logs/{log_id}')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == log_id
            assert data['action_type'] == 'CREATE'

    @pytest.mark.integration
    def test_get_action_log_not_found(self, client, app):
        """Récupérer un log inexistant retourne 404."""
        with app.app_context():
            response = client.get('/v1/action_logs/99999')
            
            assert response.status_code == 404

    # === DELETE /action_logs/<id> - Supprimer un log ===

    @pytest.mark.integration
    def test_delete_action_log_success(self, client, app):
        """Supprimer un log avec succès."""
        user_id = create_user(app, 'user1', 'user1@test.com', 'pass')
        log_id = create_action_log(app, user_id, 'CREATE')
        
        with app.app_context():
            response = client.delete(f'/v1/action_logs/{log_id}')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['deleted'] is True
            
            # Vérifier que le log a été supprimé
            deleted = ActionLog.query.get(log_id)
            assert deleted is None

    @pytest.mark.integration
    def test_delete_action_log_not_found(self, client, app):
        """Supprimer un log inexistant retourne 404."""
        with app.app_context():
            response = client.delete('/v1/action_logs/99999')
            
            assert response.status_code == 404

    # === GET /action_logs/stats - Récupérer les statistiques ===

    @pytest.mark.integration
    def test_get_action_log_stats_empty(self, client, app):
        """Récupérer les stats quand il n'y a aucun log."""
        with app.app_context():
            response = client.get('/v1/action_logs/stats')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['action_counts'] == []
            assert data['user_counts'] == []

    @pytest.mark.integration
    def test_get_action_log_stats_with_data(self, client, app):
        """Récupérer les stats avec des logs."""
        user_id1 = create_user(app, 'user1', 'user1@test.com', 'pass')
        user_id2 = create_user(app, 'user2', 'user2@test.com', 'pass')
        
        with app.app_context():
            # user1: 3 CREATE, 2 UPDATE
            create_action_log(app, user_id1, 'CREATE')
            create_action_log(app, user_id1, 'CREATE')
            create_action_log(app, user_id1, 'CREATE')
            create_action_log(app, user_id1, 'UPDATE')
            create_action_log(app, user_id1, 'UPDATE')
            
            # user2: 1 DELETE
            create_action_log(app, user_id2, 'DELETE')
            
            response = client.get('/v1/action_logs/stats')
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Vérifier les comptes par action
            action_counts = {item['action_type']: item['count'] for item in data['action_counts']}
            assert action_counts['CREATE'] == 3
            assert action_counts['UPDATE'] == 2
            assert action_counts['DELETE'] == 1
            
            # Vérifier les comptes par utilisateur
            user_counts = {item['user_id']: item['count'] for item in data['user_counts']}
            assert user_counts[user_id1] == 5
            assert user_counts[user_id2] == 1
