"""
Tests unitaires pour le modèle User.
Teste toutes les fonctionnalités du modèle User : création, validation, relations, etc.
"""
import pytest
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User, Note, Contact, Assignment


class TestUserModel:
    """Tests pour le modèle User."""

    @pytest.mark.unit
    def test_user_creation(self, app):
        """Test la création basique d'un utilisateur."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('password123')
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password_hash is not None
            assert user.created_date is not None
            assert isinstance(user.created_date, datetime)

    @pytest.mark.unit
    def test_user_creation_minimal_required_fields(self, app):
        """Test la création avec seulement les champs requis."""
        with app.app_context():
            user = User(
                username='minimal',
                email='minimal@test.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'minimal'
            assert user.email == 'minimal@test.com'

    @pytest.mark.unit
    def test_user_username_unique_constraint(self, app):
        """Test que le username doit être unique."""
        with app.app_context():
            # Créer le premier utilisateur
            user1 = User(
                username='duplicate',
                email='user1@test.com',
                password_hash='hash1'
            )
            db.session.add(user1)
            db.session.commit()
            
            # Essayer de créer un deuxième avec le même username
            user2 = User(
                username='duplicate',  # Même username
                email='user2@test.com',
                password_hash='hash2'
            )
            db.session.add(user2)
            
            with pytest.raises(Exception):  # Violation de contrainte unique
                db.session.commit()

    @pytest.mark.unit
    def test_user_email_unique_constraint(self, app):
        """Test que l'email doit être unique."""
        with app.app_context():
            # Créer le premier utilisateur
            user1 = User(
                username='user1',
                email='duplicate@test.com',
                password_hash='hash1'
            )
            db.session.add(user1)
            db.session.commit()
            
            # Essayer de créer un deuxième avec le même email
            user2 = User(
                username='user2',
                email='duplicate@test.com',  # Même email
                password_hash='hash2'
            )
            db.session.add(user2)
            
            with pytest.raises(Exception):  # Violation de contrainte unique
                db.session.commit()

    @pytest.mark.unit
    def test_user_password_hashing(self, app):
        """Test le hachage des mots de passe."""
        with app.app_context():
            password = 'supersecret123'
            hashed = generate_password_hash(password)
            
            user = User(
                username='hashtest',
                email='hash@test.com',
                password_hash=hashed
            )
            db.session.add(user)
            db.session.commit()
            
            # Le mot de passe haché ne doit pas être le mot de passe en clair
            assert user.password_hash != password
            
            # Mais on doit pouvoir vérifier le mot de passe
            assert check_password_hash(user.password_hash, password)
            assert not check_password_hash(user.password_hash, 'wrongpassword')

    @pytest.mark.unit
    def test_user_to_dict(self, app):
        """Test la méthode to_dict()."""
        with app.app_context():
            user = User(
                username='dicttest',
                email='dict@test.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            # Vérifier que tous les champs sont présents
            assert 'id' in user_dict
            assert 'username' in user_dict
            assert 'email' in user_dict
            assert 'created_date' in user_dict
            
            # Vérifier les valeurs
            assert user_dict['id'] == user.id
            assert user_dict['username'] == 'dicttest'
            assert user_dict['email'] == 'dict@test.com'
            assert user_dict['created_date'] is not None
            
            # Le mot de passe ne doit PAS être dans le dict
            assert 'password_hash' not in user_dict
            assert 'password' not in user_dict

    @pytest.mark.unit
    def test_user_repr(self, app):
        """Test la représentation string du modèle."""
        with app.app_context():
            user = User(
                username='reprtest',
                email='repr@test.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            repr_str = repr(user)
            assert 'User' in repr_str
            assert f'id={user.id}' in repr_str
            assert 'reprtest' in repr_str

    @pytest.mark.unit
    def test_user_contacts_relationship(self, app):
        """Test la relation avec les contacts."""
        with app.app_context():
            # Créer deux utilisateurs
            user1 = User(
                username='user1',
                email='user1@test.com',
                password_hash='hash1'
            )
            user2 = User(
                username='user2',
                email='user2@test.com',
                password_hash='hash2'
            )
            db.session.add_all([user1, user2])
            db.session.commit()
            
            # user1 ajoute user2 à ses contacts
            contact = Contact(
                user_id=user1.id,
                contact_user_id=user2.id,
                nickname='Mon ami',
                contact_action='collaboration'
            )
            db.session.add(contact)
            db.session.commit()
            
            # Vérifier la relation
            assert len(user1.contacts) == 1
            assert user1.contacts[0].nickname == 'Mon ami'
            assert user1.contacts[0].contact_user_id == user2.id

    @pytest.mark.unit
    def test_user_created_notes_relationship(self, app):
        """Test la relation avec les notes créées."""
        with app.app_context():
            user = User(
                username='creator',
                email='creator@test.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Créer des notes
            note1 = Note(
                content='Note 1',
                creator_id=user.id
            )
            note2 = Note(
                content='Note 2',
                creator_id=user.id
            )
            db.session.add_all([note1, note2])
            db.session.commit()
            
            # Vérifier la relation (à travers les assignments ou query directe)
            created_notes = Note.query.filter_by(creator_id=user.id).all()
            assert len(created_notes) == 2
            assert created_notes[0].content in ['Note 1', 'Note 2']
            assert created_notes[1].content in ['Note 1', 'Note 2']

    @pytest.mark.unit
    def test_user_assignments_relationship(self, app):
        """Test la relation avec les assignments."""
        with app.app_context():
            # Créer utilisateur et note
            user = User(
                username='assignee',
                email='assignee@test.com',
                password_hash='hashed_password'
            )
            creator = User(
                username='creator',
                email='creator@test.com',
                password_hash='hashed_password'
            )
            db.session.add_all([user, creator])
            db.session.commit()
            
            note = Note(
                content='Note assignée',
                creator_id=creator.id
            )
            db.session.add(note)
            db.session.commit()
            
            # Créer assignment
            assignment = Assignment(
                note_id=note.id,
                user_id=user.id
            )
            db.session.add(assignment)
            db.session.commit()
            
            # Vérifier la relation via query
            user_assignments = Assignment.query.filter_by(user_id=user.id).all()
            assert len(user_assignments) == 1
            assert user_assignments[0].note_id == note.id

    @pytest.mark.unit
    def test_user_validation_empty_username(self, app):
        """Test validation avec username vide."""
        with app.app_context():
            # La validation doit se déclencher dès la création de l'objet
            with pytest.raises(ValueError, match="Le nom d'utilisateur ne peut pas être vide"):
                user = User(
                    username='',  # Username vide
                    email='empty@test.com',
                    password_hash='hashed_password'
                )

    @pytest.mark.unit
    def test_user_validation_empty_email(self, app):
        """Test validation avec email vide."""
        with app.app_context():
            with pytest.raises(ValueError, match="L'email ne peut pas être vide"):
                user = User(
                    username='emailtest',
                    email='',  # Email vide
                    password_hash='hashed_password'
                )

    @pytest.mark.unit
    def test_user_validation_long_username(self, app):
        """Test validation avec username trop long."""
        with app.app_context():
            long_username = 'a' * 100  # Username très long (limite: 80)
            with pytest.raises(ValueError, match="Le nom d'utilisateur ne peut pas dépasser 80 caractères"):
                user = User(
                    username=long_username,
                    email='long@test.com',
                    password_hash='hashed_password'
                )

    @pytest.mark.unit
    def test_user_validation_long_email(self, app):
        """Test validation avec email trop long."""
        with app.app_context():
            long_email = 'a' * 115 + '@test.com'  # Email trop long : 115 + 9 = 124 caractères (> 120)
            # email-validator détecte que la partie locale est trop longue (max 64)
            with pytest.raises(ValueError, match="Format d'email invalide"):
                user = User(
                    username='emaillong',
                    email=long_email,
                    password_hash='hashed_password'
                )

    @pytest.mark.unit
    def test_user_query_by_username(self, app):
        """Test la recherche d'utilisateur par username."""
        with app.app_context():
            user = User(
                username='findme',
                email='findme@test.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Rechercher par username
            found_user = User.query.filter_by(username='findme').first()
            assert found_user is not None
            assert found_user.email == 'findme@test.com'
            
            # Recherche qui ne trouve rien
            not_found = User.query.filter_by(username='notexist').first()
            assert not_found is None

    @pytest.mark.unit
    def test_user_query_by_email(self, app):
        """Test la recherche d'utilisateur par email."""
        with app.app_context():
            user = User(
                username='emailfind',
                email='findbyemail@test.com',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Rechercher par email
            found_user = User.query.filter_by(email='findbyemail@test.com').first()
            assert found_user is not None
            assert found_user.username == 'emailfind'

    @pytest.mark.unit
    def test_multiple_users_creation(self, app):
        """Test la création de plusieurs utilisateurs."""
        with app.app_context():
            users = []
            for i in range(5):
                user = User(
                    username=f'user{i}',
                    email=f'user{i}@test.com',
                    password_hash=f'hashed_password{i}'
                )
                users.append(user)
            
            db.session.add_all(users)
            db.session.commit()
            
            # Vérifier que tous les utilisateurs sont créés
            all_users = User.query.all()
            assert len(all_users) == 5
            
            usernames = [u.username for u in all_users]
            for i in range(5):
                assert f'user{i}' in usernames

    @pytest.mark.unit
    def test_user_validation_short_username(self, app):
        """Test validation avec username trop court."""
        with app.app_context():
            with pytest.raises(ValueError, match="Le nom d'utilisateur doit contenir au moins 2 caractères"):
                user = User(
                    username='a',  # Trop court (< 2 caractères)
                    email='short@test.com',
                    password_hash='hashed_password'
                )

    @pytest.mark.unit
    def test_user_validation_invalid_email_format(self, app):
        """Test validation avec format d'email invalide."""
        with app.app_context():
            # Email sans @
            with pytest.raises(ValueError, match="Format d'email invalide"):
                user1 = User(
                    username='testuser1',
                    email='invalidemail',
                    password_hash='hashed_password'
                )
            
            # Email sans domaine
            with pytest.raises(ValueError, match="Format d'email invalide"):
                user2 = User(
                    username='testuser2',
                    email='invalid@',
                    password_hash='hashed_password'
                )

    @pytest.mark.unit
    def test_user_validation_whitespace_trimming(self, app):
        """Test que les espaces en début/fin sont supprimés."""
        with app.app_context():
            user = User(
                username='  trimtest  ',
                email='  TRIM@TEST.COM  ',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            # Vérifier que les espaces ont été supprimés et l'email mis en minuscules
            assert user.username == 'trimtest'
            assert user.email == 'trim@test.com'

    @pytest.mark.unit
    def test_username_length_bounds(self, app):
        with app.app_context():
            # 80 => OK
            u_ok = User(username='x'*80, email='u80@test.com', password_hash='h')
            db.session.add(u_ok)
            db.session.commit()

            # 81 => KO
            with pytest.raises(ValueError, match="ne peut pas dépasser 80"):
                User(username='x'*81, email='u81@test.com', password_hash='h')

    @pytest.mark.unit
    def test_email_length_bounds(self, app):
        with app.app_context():
            # email-validator limite la partie locale à 64 caractères (RFC 5321)
            # Test avec un email valide de longueur raisonnable
            domain = "@example.com"
            e_valid = "test.user" + domain  # ~20 caractères, bien en dessous de 64
            u_ok = User(username="evalid", email=e_valid, password_hash="h")
            db.session.add(u_ok); db.session.commit()

            # Test avec partie locale trop longue (>64)
            e_toolong = "a" * 65 + domain
            with pytest.raises(ValueError, match="Format d'email invalide"):
                User(username="etoolong", email=e_toolong, password_hash="h")

    @pytest.mark.unit
    def test_email_case_insensitive_uniqueness(self, app):
        with app.app_context():
            u1 = User(username='U1', email='FOO@BAR.COM', password_hash='x')
            db.session.add(u1)
            db.session.commit()

            u2 = User(username='U2', email='foo@bar.com', password_hash='y')
            db.session.add(u2)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    @pytest.mark.unit
    def test_trim_and_lower_on_update(self, app):
        with app.app_context():
            u = User(username='John', email='John.DOE@Mail.COM', password_hash='h')
            db.session.add(u); db.session.commit()

            # Update avec espaces + casse
            u.username = "   Johnny   "
            u.email = "  JOHNNY@MAIL.com  "
            db.session.commit()

            assert u.username == "Johnny"
            assert u.email == "johnny@mail.com"

    # ---------- PASSWORD HELPERS & VALIDATIONS ----------

    @pytest.mark.unit
    def test_set_password_and_check_password(self, app):
        with app.app_context():
            u = User(username='pw', email='pw@test.com', password_hash='init')
            db.session.add(u); db.session.commit()

            u.set_password('P@ssw0rd!')
            db.session.commit()

            assert u.password_hash != 'P@ssw0rd!'
            assert u.check_password('P@ssw0rd!') is True
            assert u.check_password('nope') is False

    @pytest.mark.unit
    def test_password_hash_blank_raises(self, app):
        with app.app_context():
            with pytest.raises(ValueError, match="Le mot de passe ne peut pas être vide"):
                User(username='testuser', email='a@test.com', password_hash='   ')

    # ---------- DATES / TIMEZONE ----------

    @pytest.mark.unit
    def test_created_date_is_timezone_aware_utc(self, app):
        with app.app_context():
            u = User(username='tz', email='tz@test.com', password_hash='h')
            db.session.add(u)
            db.session.commit()

            # Cas SQLAlchemy avec timezone=True
            if u.created_date.tzinfo is not None:
                assert u.created_date.utcoffset() == timezone.utc.utcoffset(u.created_date)
            # Cas SQLite pas de timezone
            else:
                assert isinstance(u.created_date, datetime)  # au moins un datetime naïf

    # ---------- UNICITÉS & EXCEPTIONS PRÉCISES ----------

    @pytest.mark.unit
    def test_username_unique_integrity_error(self, app):
        with app.app_context():
            db.session.add(User(username='dup', email='dup1@test.com', password_hash='h'))
            db.session.commit()

            db.session.add(User(username='dup', email='dup2@test.com', password_hash='h'))
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    @pytest.mark.unit
    def test_email_unique_integrity_error(self, app):
        with app.app_context():
            db.session.add(User(username='u1', email='uniq@test.com', password_hash='h'))
            db.session.commit()

            db.session.add(User(username='u2', email='uniq@test.com', password_hash='h'))
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    # ---------- INTÉGRITÉ RÉFÉRENTIELLE (FK) ----------

    @pytest.mark.unit
    def test_contact_fk_integrity(self, app):
        """
        Nécessite PRAGMA foreign_keys=ON en SQLite (activé dans create_app).
        On tente de créer un Contact avec des FK inexistantes -> IntegrityError attendu.
        """
        from app.models import Contact  # évite import circular si configuration varie
        with app.app_context():
            ghost = Contact(user_id=999999, contact_user_id=888888, nickname="ghost")
            db.session.add(ghost)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    # ---------- MISE À JOUR : CONTRAINTES ET VALIDATIONS ----------

    @pytest.mark.unit
    def test_update_username_to_existing_raises(self, app):
        with app.app_context():
            u1 = User(username="alice", email="alice@test.com", password_hash="h")
            u2 = User(username="bob", email="bob@test.com", password_hash="h")
            db.session.add_all([u1, u2]); db.session.commit()

            u2.username = "alice"  # collision
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    @pytest.mark.unit
    def test_update_email_invalid_format_raises(self, app):
        with app.app_context():
            u = User(username="fmt", email="fmt@test.com", password_hash="h")
            db.session.add(u); db.session.commit()

            # Déclenche @validates('email') à la mise à jour
            with pytest.raises(ValueError, match="Format d'email invalide"):
                u.email = "invalid@"
