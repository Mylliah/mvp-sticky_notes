"""
Tests unitaires pour le modèle Assignment.
"""
import pytest
from datetime import datetime
from app import db
from app.models import User, Note, Assignment


class TestAssignmentModel:
    """Tests pour le modèle Assignment."""

    def _create_sample_user(self, username='sample', email='sample@test.com'):
        user = User(username=username, email=email, password_hash='hash')
        db.session.add(user)
        db.session.commit()
        return user

    def _create_sample_note(self, user_id, content='Sample note'):
        note = Note(content=content, creator_id=user_id, status='en_cours')
        db.session.add(note)
        db.session.commit()
        return note

    @pytest.mark.unit
    def test_assignment_creation_minimal_required_fields(self, app):
        """Créer une assignation avec les champs requis."""
        with app.app_context():
            user = self._create_sample_user('assigner', 'assigner@test.com')
            note = self._create_sample_note(user.id)

            assignment = Assignment(note_id=note.id, user_id=user.id)
            db.session.add(assignment)
            db.session.commit()

            assert assignment.id is not None
            assert assignment.note_id == note.id
            assert assignment.user_id == user.id
            assert assignment.assigned_date is not None
            assert isinstance(assignment.assigned_date, datetime)
            assert assignment.is_read is False

    @pytest.mark.unit
    def test_assignment_note_user_required(self, app):
        """Both note_id and user_id are required."""
        with app.app_context():
            assign = Assignment(note_id=None, user_id=None)
            db.session.add(assign)
            with pytest.raises(Exception):
                db.session.commit()

    @pytest.mark.unit
    def test_assignment_relations(self, app):
        """Vérifie la relation assignment.user et assignment.note."""
        with app.app_context():
            user = self._create_sample_user('assrel', 'assrel@test.com')
            note = self._create_sample_note(user.id, 'Rel note')

            assignment = Assignment(note_id=note.id, user_id=user.id)
            db.session.add(assignment)
            db.session.commit()

            # recharger user/note depuis la session
            user_db = db.session.get(User, user.id)
            note_db = db.session.get(Note, note.id)

            assert any(a.id == assignment.id for a in user_db.assignments)
            assert any(a.id == assignment.id for a in note_db.assignments)

    @pytest.mark.unit
    def test_assignment_to_dict_and_repr(self, app):
        """Test to_dict() et __repr__ pour Assignment."""
        with app.app_context():
            user = self._create_sample_user('assrepr', 'assrepr@test.com')
            note = self._create_sample_note(user.id, 'Repr note')

            assignment = Assignment(note_id=note.id, user_id=user.id, is_read=True)
            db.session.add(assignment)
            db.session.commit()

            d = assignment.to_dict()
            assert d['id'] == assignment.id
            assert d['note_id'] == note.id
            assert d['user_id'] == user.id
            assert d['is_read'] is True

            rep = repr(assignment)
            assert 'Assignment' in rep
            assert str(assignment.id) in rep
