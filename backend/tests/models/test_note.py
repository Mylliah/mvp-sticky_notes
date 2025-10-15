"""
Tests unitaires complets pour le modèle Note.
Couvre toutes les fonctionnalités, relations, conversions, cas limites et intégrité.
"""

import pytest
from datetime import datetime, timezone, timedelta
from app import db
from app.models import User, Note, Assignment, Contact


class TestNoteModel:
    """Tests pour le modèle Note."""

    def _create_sample_user(self, username='testuser', email='test@example.com'):
        """Helper pour créer un utilisateur de test."""
        user = User(
            username=username,
            email=email,
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        return user

    # === TESTS DE BASE ===

    @pytest.mark.unit
    def test_note_creation(self, app):
        """Création basique d'une note."""
        with app.app_context():
            user = self._create_sample_user()
            note = Note(content='Ceci est une note', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            assert note.id is not None
            assert note.status == 'en_cours'
            assert isinstance(note.created_date, datetime)

    @pytest.mark.unit
    def test_note_default_values(self, app):
        """Vérifie les valeurs par défaut à la création."""
        with app.app_context():
            user = self._create_sample_user('default', 'def@test.com')
            note = Note(content='Valeurs par défaut', creator_id=user.id)
            db.session.add(note)
            db.session.commit()

            assert note.status == 'en_cours'
            assert note.important is False
            assert note.update_date is None
            assert note.read_date is None
            assert note.delete_date is None

    # === VALIDATIONS ===

    @pytest.mark.unit
    def test_note_content_required(self, app):
        """Le contenu doit être obligatoire."""
        with app.app_context():
            user = self._create_sample_user('missing', 'missing@test.com')
            note = Note(content=None, creator_id=user.id)
            db.session.add(note)
            with pytest.raises(Exception):
                db.session.commit()

    @pytest.mark.unit
    def test_note_creator_required(self, app):
        """Le champ creator_id est obligatoire."""
        with app.app_context():
            note = Note(content='Sans créateur', creator_id=None)
            db.session.add(note)
            with pytest.raises(Exception):
                db.session.commit()

    @pytest.mark.unit
    def test_note_invalid_status(self, app):
        """Un statut inconnu doit être accepté (aucune contrainte DB)."""
        with app.app_context():
            user = self._create_sample_user('weirdstatus', 'weird@test.com')
            note = Note(content='Statut étrange', creator_id=user.id, status='inconnu')
            db.session.add(note)
            db.session.commit()
            assert note.status == 'inconnu'

    # === RELATIONS ===

    @pytest.mark.unit
    def test_note_creator_relationship(self, app):
        """Relation avec le créateur et backref notes."""
        with app.app_context():
            user = self._create_sample_user('reluser', 'rel@test.com')
            note = Note(content='Note avec user', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            assert note.creator == user
            assert note in user.notes

    @pytest.mark.unit
    def test_note_assignments_relationship(self, app):
        """Relation note ↔ assignments."""
        with app.app_context():
            creator = self._create_sample_user('creator', 'c@test.com')
            assigned_user = self._create_sample_user('assigned', 'a@test.com')
            note = Note(content='Note assignée', creator_id=creator.id)
            db.session.add(note)
            db.session.commit()

            assignment = Assignment(note_id=note.id, user_id=assigned_user.id)
            db.session.add(assignment)
            db.session.commit()

            assert len(note.assignments) == 1
            assert note.assignments[0].user_id == assigned_user.id

    @pytest.mark.unit
    def test_note_deletion_cascade_creator(self, app):
        """Suppression du créateur est empêchée car creator_id est NOT NULL."""
        with app.app_context():
            user = self._create_sample_user('todelete', 'del@test.com')
            note = Note(content='Persiste après user delete', creator_id=user.id)
            db.session.add(note)
            db.session.commit()

            # Tenter de supprimer le créateur doit lever une IntegrityError
            db.session.delete(user)
            with pytest.raises(Exception):  # IntegrityError en SQLite
                db.session.commit()
            
            db.session.rollback()
            # La note et l'utilisateur existent toujours
            assert db.session.get(Note, note.id) is not None
            assert db.session.get(User, user.id) is not None

    # === MÉTHODES ===

    @pytest.mark.unit
    def test_repr_truncates_content(self, app):
        """Test de __repr__ avec troncature du contenu."""
        with app.app_context():
            user = self._create_sample_user()
            long_content = "X" * 100
            note = Note(content=long_content, creator_id=user.id, important=True, status="done")
            db.session.add(note)
            db.session.commit()
            rep = repr(note)
            assert len(rep) < 150
            assert long_content[:30] in rep

    @pytest.mark.unit
    def test_to_dict_date_formats(self, app):
        """Test du format ISO des dates dans to_dict()."""
        with app.app_context():
            user = self._create_sample_user()
            now = datetime.now(timezone.utc)
            note = Note(
                content='Dates test',
                creator_id=user.id,
                created_date=now,
                update_date=now,
                read_date=now,
                delete_date=now
            )
            db.session.add(note)
            db.session.commit()
            d = note.to_dict()
            assert d['created_date'].endswith('Z') or 'T' in d['created_date']

    @pytest.mark.unit
    def test_to_details_dict_with_assignment(self, app):
        """Test de to_details_dict() avec un Assignment lié."""
        with app.app_context():
            creator = self._create_sample_user('creator', 'c@test.com')
            assignee = self._create_sample_user('assignee', 'a@test.com')

            note = Note(content='Avec assign', creator_id=creator.id)
            db.session.add(note)
            db.session.commit()

            assignment = Assignment(note_id=note.id, user_id=assignee.id)
            db.session.add(assignment)
            db.session.commit()

            d = note.to_details_dict(assignment)
            assert d['assigned_to'] == assignee.id
            assert d['assigned_date'] is not None

    @pytest.mark.unit
    def test_to_summary_dict_all_contacts(self, app):
        """Test de to_summary_dict() avec tous les contacts assignés."""
        with app.app_context():
            creator = self._create_sample_user('creator', 'creator@test.com')
            u1 = self._create_sample_user('u1', 'u1@test.com')
            u2 = self._create_sample_user('u2', 'u2@test.com')

            # Ajouter contacts pour le créateur
            contact1 = Contact(user_id=creator.id, contact_user_id=u1.id, nickname='Contact 1')
            contact2 = Contact(user_id=creator.id, contact_user_id=u2.id, nickname='Contact 2')
            db.session.add_all([contact1, contact2])
            db.session.commit()

            note = Note(content='Note all contacts', creator_id=creator.id)
            db.session.add(note)
            db.session.commit()

            # Ajouter assignments pour tous les contacts
            db.session.add_all([
                Assignment(note_id=note.id, user_id=u1.id),
                Assignment(note_id=note.id, user_id=u2.id),
            ])
            db.session.commit()

            summary = note.to_summary_dict(current_user_id=creator.id)
            assert summary['assigned_display'] in ('à All', 'à All + moi')

    @pytest.mark.unit
    def test_to_summary_dict_truncation_and_display(self, app):
        """Vérifie la troncature du preview et le format assigned_display."""
        with app.app_context():
            creator = self._create_sample_user('sumuser', 'sum@test.com')
            users = [
                self._create_sample_user(f'u{i}', f'u{i}@test.com') for i in range(5)
            ]
            note = Note(content='x' * 100, creator_id=creator.id)
            db.session.add(note)
            db.session.commit()

            # Ajouter plusieurs assignments
            for u in users:
                db.session.add(Assignment(note_id=note.id, user_id=u.id))
            db.session.commit()

            s = note.to_summary_dict()
            assert s['preview'].endswith('...')
            assert len(s['assigned_display']) > 0

    @pytest.mark.unit
    def test_note_with_finished_date(self, app):
        """Test le champ finished_date s’il est présent dynamiquement."""
        with app.app_context():
            creator = self._create_sample_user('fin', 'fin@test.com')
            note = Note(content='Avec finished_date', creator_id=creator.id)
            note.finished_date = datetime.now(timezone.utc)
            db.session.add(note)
            db.session.commit()
            d = note.to_details_dict()
            assert d['finished_date'] is not None

    # === REQUÊTES ET RECHERCHES ===

    @pytest.mark.unit
    def test_query_filters(self, app):
        """Test de plusieurs filtres de requêtes."""
        with app.app_context():
            user = self._create_sample_user('query', 'query@test.com')
            n1 = Note(content='N1', creator_id=user.id, important=True)
            n2 = Note(content='N2', creator_id=user.id, important=False)
            n3 = Note(content='N3', creator_id=user.id, status='done')
            db.session.add_all([n1, n2, n3])
            db.session.commit()

            assert len(Note.query.filter_by(creator_id=user.id).all()) == 3
            assert Note.query.filter_by(important=True).first().content == 'N1'
            assert Note.query.filter(Note.status == 'done').first().content == 'N3'

    # === CAS LIMITES ET ROBUSTESSE ===

    @pytest.mark.unit
    def test_note_empty_string_content(self, app):
        """Un contenu vide (chaîne vide) est autorisé mais pas None."""
        with app.app_context():
            user = self._create_sample_user('empty', 'empty@test.com')
            note = Note(content='', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            assert note.content == ''

    @pytest.mark.unit
    def test_note_delete_date_marks_soft_delete(self, app):
        """Une note avec delete_date simulant une suppression logique."""
        with app.app_context():
            user = self._create_sample_user('softdel', 'soft@test.com')
            note = Note(content='Supprimée logiquement', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            note.delete_date = datetime.now(timezone.utc)
            db.session.commit()
            assert note.delete_date is not None

    @pytest.mark.unit
    def test_note_datetime_precision(self, app):
        """Vérifie la précision des datetime (UTC)."""
        with app.app_context():
            user = self._create_sample_user('time', 'time@test.com')
            note = Note(content='Timing', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            # SQLite stocke datetime sans timezone, on doit comparer en naive
            diff = datetime.now(timezone.utc).replace(tzinfo=None) - note.created_date
            assert diff.total_seconds() < 5

    @pytest.mark.unit
    def test_note_invalid_type_raises(self, app):
        """Fournir un type invalide pour 'important' doit lever une erreur."""
        with app.app_context():
            user = self._create_sample_user('bool', 'bool@test.com')
            note = Note(content='Mauvais type', creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            # Important doit être un bool, donc affectation d’un int ou str testée
            note.important = "yes"
            with pytest.raises(Exception):
                db.session.commit()
