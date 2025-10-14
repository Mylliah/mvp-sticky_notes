"""
Tests unitaires pour le modèle ActionLog.
"""
import pytest
from datetime import datetime
from app import db
from app.models import User, ActionLog


class TestActionLogModel:

    def _create_sample_user(self, username='actor', email='actor@test.com'):
        user = User(username=username, email=email, password_hash='hash')
        db.session.add(user)
        db.session.commit()
        return user

    @pytest.mark.unit
    def test_action_log_creation_minimal_required_fields(self, app):
        """Créer un ActionLog avec les champs requis."""
        with app.app_context():
            user = self._create_sample_user('act1', 'act1@test.com')

            log = ActionLog(user_id=user.id, target_id=123, action_type='create')
            db.session.add(log)
            db.session.commit()

            assert log.id is not None
            assert log.user_id == user.id
            assert log.target_id == 123
            assert log.action_type == 'create'
            assert log.timestamp is not None
            assert isinstance(log.timestamp, datetime)

    @pytest.mark.unit
    def test_action_log_missing_fields(self, app):
        """user_id and action_type are required."""
        with app.app_context():
            # missing user_id
            log = ActionLog(user_id=None, target_id=1, action_type='x')
            db.session.add(log)
            with pytest.raises(Exception):
                db.session.commit()
            # La transaction est rollbackée sur exception; on doit rollbacker pour réutiliser la session
            db.session.rollback()

            # missing action_type
            user = self._create_sample_user('act2', 'act2@test.com')
            log2 = ActionLog(user_id=user.id, target_id=2, action_type=None)
            db.session.add(log2)
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    @pytest.mark.unit
    def test_action_log_relation_and_to_dict(self, app):
        """Vérifie la relation user.action_logs et la sérialisation."""
        with app.app_context():
            user = self._create_sample_user('act3', 'act3@test.com')
            log = ActionLog(user_id=user.id, target_id=999, action_type='update', payload='{"k": "v"}')
            db.session.add(log)
            db.session.commit()

            # recharger user
            user_db = db.session.get(User, user.id)
            assert any(l.id == log.id for l in user_db.action_logs)

            d = log.to_dict()
            assert d['id'] == log.id
            assert d['user_id'] == user.id
            assert d['action_type'] == 'update'
            assert 'timestamp' in d

            rep = repr(log)
            assert 'ActionLog' in rep
            assert str(log.id) in rep
