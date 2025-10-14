"""
Tests unitaires pour le modèle Contact.
"""
import pytest
from datetime import datetime, timezone
from app import db
from app.models import User, Contact


class TestContactModel:
    """Tests pour le modèle Contact."""

    def _create_sample_user(self, username='sample', email='sample@test.com'):
        user = User(username=username, email=email, password_hash='hash')
        db.session.add(user)
        db.session.commit()
        return user

    @pytest.mark.unit
    def test_contact_creation_minimal_required_fields(self, app):
        """Créer un contact avec les champs requis."""
        with app.app_context():
            owner = self._create_sample_user('owner', 'owner@test.com')
            contact_user = self._create_sample_user('friend', 'friend@test.com')

            contact = Contact(
                user_id=owner.id,
                contact_user_id=contact_user.id,
                nickname='Ami'
            )
            db.session.add(contact)
            db.session.commit()

            assert contact.id is not None
            assert contact.user_id == owner.id
            assert contact.contact_user_id == contact_user.id
            assert contact.nickname == 'Ami'
            assert contact.created_date is not None
            assert isinstance(contact.created_date, datetime)

    @pytest.mark.unit
    def test_contact_nickname_required(self, app):
        """Le champ nickname est requis."""
        with app.app_context():
            owner = self._create_sample_user('owner2', 'owner2@test.com')
            friend = self._create_sample_user('friend2', 'friend2@test.com')

            contact = Contact(
                user_id=owner.id,
                contact_user_id=friend.id,
                nickname=None
            )
            db.session.add(contact)
            with pytest.raises(Exception):
                db.session.commit()

    @pytest.mark.unit
    def test_contact_relations(self, app):
        """Vérifie que la relation user.contacts fonctionne."""
        with app.app_context():
            owner = self._create_sample_user('owner3', 'owner3@test.com')
            friend = self._create_sample_user('friend3', 'friend3@test.com')

            contact = Contact(
                user_id=owner.id,
                contact_user_id=friend.id,
                nickname='Buddy',
                contact_action='work'
            )
            db.session.add(contact)
            db.session.commit()

            # recharger owner depuis la session pour accéder à la relation
            # owner_db = User.query.get(owner.id) -> à la place : 
            # Utiliser Session.get() (db.session.get) plutôt que Query.get() qui est déprécié
            owner_db = db.session.get(User, owner.id)
            assert len(owner_db.contacts) == 1
            assert owner_db.contacts[0].nickname == 'Buddy'
            assert owner_db.contacts[0].contact_user_id == friend.id

    @pytest.mark.unit
    def test_contact_to_dict_and_repr(self, app):
        """Test to_dict() et __repr__ pour Contact."""
        with app.app_context():
            owner = self._create_sample_user('owner4', 'owner4@test.com')
            friend = self._create_sample_user('friend4', 'friend4@test.com')

            contact = Contact(
                user_id=owner.id,
                contact_user_id=friend.id,
                nickname='Colleague',
                contact_action='assist'
            )
            db.session.add(contact)
            db.session.commit()

            d = contact.to_dict()
            assert d['id'] == contact.id
            assert d['user_id'] == owner.id
            assert d['contact_user_id'] == friend.id
            assert d['nickname'] == 'Colleague'
            assert 'created_date' in d

            rep = repr(contact)
            assert 'Contact' in rep
            assert str(contact.id) in rep
