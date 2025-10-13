"""
Tests unitaires pour le modèle Note.
Teste toutes les fonctionnalités du modèle Note : création, validation, relations, méthodes, etc.
"""
import pytest
from datetime import datetime
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

    @pytest.mark.unit
    def test_note_creation(self, app):
        """Test la création basique d'une note."""
        with app.app_context():
            user = self._create_sample_user()
            
            note = Note(
                content='Ceci est une note de test',
                creator_id=user.id,
                status='en_cours'
            )
            db.session.add(note)
            db.session.commit()
            
            assert note.id is not None
            assert note.content == 'Ceci est une note de test'
            assert note.creator_id == user.id
            assert note.status == 'en_cours'
            assert note.important is False  # Valeur par défaut
            assert note.created_date is not None
            assert isinstance(note.created_date, datetime)

    @pytest.mark.unit
    def test_note_creation_minimal_required_fields(self, app):
        """Test la création avec seulement les champs requis."""
        with app.app_context():
            user = self._create_sample_user('minimaluser', 'minimal@test.com')
            
            note = Note(
                content='Note minimale',
                creator_id=user.id
            )
            db.session.add(note)
            db.session.commit()
            
            assert note.id is not None
            assert note.content == 'Note minimale'
            assert note.creator_id == user.id
            assert note.status == 'en_cours'  # Valeur par défaut

    @pytest.mark.unit
    def test_note_creation_with_all_fields(self, app):
        """Test la création avec tous les champs optionnels."""
        with app.app_context():
            user = self._create_sample_user('fulluser', 'full@test.com')
            now = datetime.utcnow()
            
            note = Note(
                content='Note complète avec tous les champs',
                creator_id=user.id,
                status='terminé',
                important=True,
                update_date=now,
                read_date=now
            )
            db.session.add(note)
            db.session.commit()
            
            assert note.content == 'Note complète avec tous les champs'
            assert note.status == 'terminé'
            assert note.important is True
            assert note.update_date == now
            assert note.read_date == now

    @pytest.mark.unit
    def test_note_content_required(self, app):
        """Test que le contenu est obligatoire."""
        with app.app_context():
            user = self._create_sample_user('contentuser', 'content@test.com')
            
            note = Note(
                content=None,  # Contenu manquant
                creator_id=user.id
            )
            db.session.add(note)
            
            with pytest.raises(Exception):  # Violation de contrainte NOT NULL
                db.session.commit()

    @pytest.mark.unit
    def test_note_creator_id_required(self, app):
        """Test que creator_id peut être null pour l'instant (design actuel)."""
        with app.app_context():
            note = Note(
                content='Note sans créateur',
                creator_id=None  # Actuellement autorisé par le modèle
            )
            db.session.add(note)
            db.session.commit()
            
            # Le modèle actuel autorise creator_id=None
            assert note.creator_id is None
            assert note.content == 'Note sans créateur'

    @pytest.mark.unit
    def test_note_creator_relationship(self, app):
        """Test la relation avec le créateur (User)."""
        with app.app_context():
            user = self._create_sample_user('relationuser', 'relation@test.com')
            
            note = Note(
                content='Note avec relation créateur',
                creator_id=user.id,
                status='en_cours'
            )
            db.session.add(note)
            db.session.commit()
            
            # Vérifier la relation
            assert note.creator is not None
            assert note.creator.id == user.id
            assert note.creator.username == user.username
            
            # Vérifier la relation inverse (backref)
            assert note in user.notes

    @pytest.mark.unit
    def test_note_assignments_relationship(self, app):
        """Test la relation avec les assignments."""
        with app.app_context():
            creator = self._create_sample_user('creator', 'creator@test.com')
            assigned_user = self._create_sample_user('assigned', 'assigned@test.com')
            
            # Créer une note
            note = Note(
                content='Note avec assignments',
                creator_id=creator.id
            )
            db.session.add(note)
            db.session.commit()
            
            # Créer l'assignment
            assignment = Assignment(
                note_id=note.id,
                user_id=assigned_user.id
            )
            db.session.add(assignment)
            db.session.commit()
            
            # Vérifier la relation
            assert len(note.assignments) == 1
            assert note.assignments[0].user_id == assigned_user.id
            assert note.assignments[0].note_id == note.id

    @pytest.mark.unit
    def test_note_repr(self, app):
        """Test la représentation string du modèle."""
        with app.app_context():
            user = self._create_sample_user('repruser', 'repr@test.com')
            
            note = Note(
                content='Cette note a un contenu très long qui sera tronqué dans la représentation',
                creator_id=user.id,
                status='important',
                important=True
            )
            db.session.add(note)
            db.session.commit()
            
            repr_str = repr(note)
            assert 'Note' in repr_str
            assert f'id={note.id}' in repr_str
            assert 'status=\'important\'' in repr_str
            assert 'important=True' in repr_str
            assert 'Cette note a un contenu très' in repr_str  # Contenu tronqué à 30 caractères

    @pytest.mark.unit
    def test_note_to_dict(self, app):
        """Test la méthode to_dict()."""
        with app.app_context():
            user = self._create_sample_user('dictuser', 'dict@test.com')
            now = datetime.utcnow()
            
            note = Note(
                content='Note pour test to_dict',
                creator_id=user.id,
                status='en_cours',
                important=True,
                update_date=now
            )
            db.session.add(note)
            db.session.commit()
            
            note_dict = note.to_dict()
            
            # Vérifier que tous les champs sont présents
            expected_fields = [
                'id', 'content', 'status', 'important', 
                'created_date', 'update_date', 'delete_date', 
                'read_date', 'creator_id'
            ]
            for field in expected_fields:
                assert field in note_dict
            
            # Vérifier les valeurs
            assert note_dict['id'] == note.id
            assert note_dict['content'] == 'Note pour test to_dict'
            assert note_dict['status'] == 'en_cours'
            assert note_dict['important'] is True
            assert note_dict['creator_id'] == user.id
            assert note_dict['created_date'] is not None
            assert note_dict['update_date'] is not None
            assert note_dict['delete_date'] is None
            assert note_dict['read_date'] is None

    @pytest.mark.unit
    def test_note_to_details_dict(self, app):
        """Test la méthode to_details_dict()."""
        with app.app_context():
            creator = self._create_sample_user('detailscreator', 'detailscreator@test.com')
            
            note = Note(
                content='Note pour test details',
                creator_id=creator.id,
                status='terminé',
                important=False
            )
            db.session.add(note)
            db.session.commit()
            
            # Test sans assignment
            details_dict = note.to_details_dict()
            assert 'id' in details_dict
            assert 'assigned_to' in details_dict
            assert 'assigned_date' in details_dict
            assert 'status' in details_dict
            assert 'important' in details_dict
            assert details_dict['assigned_to'] is None
            assert details_dict['assigned_date'] is None
            
            # Test avec assignment
            assigned_user = self._create_sample_user('detailsassigned', 'detailsassigned@test.com')
            
            assignment = Assignment(
                note_id=note.id,
                user_id=assigned_user.id
            )
            db.session.add(assignment)
            db.session.commit()
            
            details_dict_with_assignment = note.to_details_dict(assignment)
            assert details_dict_with_assignment['assigned_to'] == assigned_user.id
            assert details_dict_with_assignment['assigned_date'] is not None

    @pytest.mark.unit
    def test_note_to_summary_dict(self, app):
        """Test la méthode to_summary_dict()."""
        with app.app_context():
            user = self._create_sample_user('summaryuser', 'summary@test.com')
            
            note = Note(
                content='Cette note a un contenu assez long pour tester la fonctionnalité de preview qui doit tronquer le texte',
                creator_id=user.id,
                status='en_cours',
                important=True
            )
            db.session.add(note)
            db.session.commit()
            
            summary_dict = note.to_summary_dict()
            
            # Vérifier que tous les champs sont présents
            expected_fields = [
                'id', 'status', 'important', 'preview', 
                'creator', 'assigned_display', 'created_date'
            ]
            for field in expected_fields:
                assert field in summary_dict
            
            # Vérifier les valeurs
            assert summary_dict['id'] == note.id
            assert summary_dict['status'] == 'en_cours'
            assert summary_dict['important'] is True
            assert summary_dict['creator'] == user.username
            assert summary_dict['created_date'] is not None
            
            # Vérifier que le preview est tronqué
            assert len(summary_dict['preview']) <= 33  # 30 caractères + "..."
            assert summary_dict['preview'].endswith('...')

    @pytest.mark.unit
    def test_note_summary_dict_short_content(self, app):
        """Test to_summary_dict avec contenu court (pas de troncature)."""
        with app.app_context():
            user = self._create_sample_user('shortuser', 'short@test.com')
            
            note = Note(
                content='Court',
                creator_id=user.id
            )
            db.session.add(note)
            db.session.commit()
            
            summary_dict = note.to_summary_dict()
            
            # Le contenu court ne doit pas être tronqué
            assert summary_dict['preview'] == 'Court'
            assert not summary_dict['preview'].endswith('...')

    @pytest.mark.unit
    def test_note_status_values(self, app):
        """Test différentes valeurs de statut."""
        with app.app_context():
            statuses = ['en_cours', 'terminé', 'suspendu', 'annulé']
            
            for i, status in enumerate(statuses):
                user = self._create_sample_user(f'statususer{i}', f'status{i}@test.com')
                note = Note(
                    content=f'Note avec statut {status}',
                    creator_id=user.id,
                    status=status
                )
                db.session.add(note)
                db.session.commit()
                
                assert note.status == status

    @pytest.mark.unit
    def test_note_important_flag(self, app):
        """Test le flag important."""
        with app.app_context():
            user1 = self._create_sample_user('importantuser1', 'important1@test.com')
            user2 = self._create_sample_user('importantuser2', 'important2@test.com')
            
            # Note importante
            note_important = Note(
                content='Note importante',
                creator_id=user1.id,
                important=True
            )
            db.session.add(note_important)
            db.session.commit()
            
            assert note_important.important is True
            
            # Note normale
            note_normale = Note(
                content='Note normale',
                creator_id=user2.id,
                important=False
            )
            db.session.add(note_normale)
            db.session.commit()
            
            assert note_normale.important is False

    @pytest.mark.unit
    def test_note_dates_management(self, app):
        """Test la gestion des différentes dates."""
        with app.app_context():
            user = self._create_sample_user('dateuser', 'date@test.com')
            now = datetime.utcnow()
            
            note = Note(
                content='Note avec gestion des dates',
                creator_id=user.id
            )
            db.session.add(note)
            db.session.commit()
            
            # created_date doit être définie automatiquement
            assert note.created_date is not None
            assert isinstance(note.created_date, datetime)
            
            # Mettre à jour les autres dates
            note.update_date = now
            note.read_date = now
            note.delete_date = now
            db.session.commit()
            
            assert note.update_date == now
            assert note.read_date == now
            assert note.delete_date == now

    @pytest.mark.unit
    def test_note_query_by_creator(self, app):
        """Test la recherche de notes par créateur."""
        with app.app_context():
            user = self._create_sample_user('queryuser', 'query@test.com')
            
            # Créer plusieurs notes pour le même utilisateur
            note1 = Note(content='Note 1', creator_id=user.id)
            note2 = Note(content='Note 2', creator_id=user.id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            # Rechercher les notes du créateur
            user_notes = Note.query.filter_by(creator_id=user.id).all()
            assert len(user_notes) == 2
            
            note_contents = [n.content for n in user_notes]
            assert 'Note 1' in note_contents
            assert 'Note 2' in note_contents

    @pytest.mark.unit
    def test_note_query_by_status(self, app):
        """Test la recherche de notes par statut."""
        with app.app_context():
            user1 = self._create_sample_user('statusquery1', 'statusquery1@test.com')
            user2 = self._create_sample_user('statusquery2', 'statusquery2@test.com')
            
            # Créer des notes avec différents statuts
            note_en_cours = Note(content='En cours', creator_id=user1.id, status='en_cours')
            note_terminee = Note(content='Terminée', creator_id=user2.id, status='terminé')
            db.session.add_all([note_en_cours, note_terminee])
            db.session.commit()
            
            # Rechercher par statut
            notes_en_cours = Note.query.filter_by(status='en_cours').all()
            notes_terminees = Note.query.filter_by(status='terminé').all()
            
            assert len(notes_en_cours) >= 1  # Au moins une note en cours
            assert len(notes_terminees) >= 1  # Au moins une note terminée
            
            # Trouver nos notes spécifiques
            note_en_cours_found = next((n for n in notes_en_cours if n.content == 'En cours'), None)
            note_terminee_found = next((n for n in notes_terminees if n.content == 'Terminée'), None)
            
            assert note_en_cours_found is not None
            assert note_terminee_found is not None

    @pytest.mark.unit
    def test_note_query_important_only(self, app):
        """Test la recherche de notes importantes uniquement."""
        with app.app_context():
            user1 = self._create_sample_user('importantquery1', 'importantquery1@test.com')
            user2 = self._create_sample_user('importantquery2', 'importantquery2@test.com')
            
            # Créer des notes importantes et normales
            note_importante = Note(content='Importante', creator_id=user1.id, important=True)
            note_normale = Note(content='Normale', creator_id=user2.id, important=False)
            db.session.add_all([note_importante, note_normale])
            db.session.commit()
            
            # Rechercher les notes importantes
            notes_importantes = Note.query.filter_by(important=True).all()
            
            assert len(notes_importantes) >= 1  # Au moins une note importante
            
            # Trouver notre note spécifique
            note_importante_found = next((n for n in notes_importantes if n.content == 'Importante'), None)
            assert note_importante_found is not None

    @pytest.mark.unit
    def test_multiple_notes_creation(self, app):
        """Test la création de plusieurs notes."""
        with app.app_context():
            user = self._create_sample_user('multipleuser', 'multiple@test.com')
            
            notes = []
            for i in range(5):
                note = Note(
                    content=f'Note de test {i}',
                    creator_id=user.id,
                    status='en_cours'
                )
                notes.append(note)
            
            db.session.add_all(notes)
            db.session.commit()
            
            # Vérifier que toutes les notes sont créées
            all_notes = Note.query.filter_by(creator_id=user.id).all()
            assert len(all_notes) == 5
            
            contents = [n.content for n in all_notes]
            for i in range(5):
                assert f'Note de test {i}' in contents