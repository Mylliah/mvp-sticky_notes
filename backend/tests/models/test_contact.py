"""
Tests unitaires complets pour le modèle Contact.
Couvre la création, les contraintes, les relations, les méthodes et les cas limites.
"""

import pytest
from datetime import datetime, timezone, timedelta
from app import db
from app.models import User, Contact


class TestContactModel:
    """Tests pour le modèle Contact."""

    def _create_user(self, username="user", email=None):
        """Crée un utilisateur pour les tests."""
        email = email or f"{username}@test.com"
        user = User(username=username, email=email, password_hash="hash")
        db.session.add(user)
        db.session.commit()
        return user

    # === CREATION ET CONTRAINTES DE BASE ===

    @pytest.mark.unit
    def test_contact_creation_minimal(self, app):
        """Création d'un contact avec les champs obligatoires uniquement."""
        with app.app_context():
            owner = self._create_user("owner")
            friend = self._create_user("friend")

            c = Contact(user_id=owner.id, contact_user_id=friend.id, nickname="Buddy")
            db.session.add(c)
            db.session.commit()

            assert c.id is not None
            assert c.user_id == owner.id
            assert c.contact_user_id == friend.id
            assert c.nickname == "Buddy"
            assert isinstance(c.created_date, datetime)

    @pytest.mark.unit
    def test_contact_creation_all_fields(self, app):
        """Création d'un contact avec tous les champs remplis."""
        with app.app_context():
            owner = self._create_user("john")
            friend = self._create_user("doe")

            c = Contact(
                user_id=owner.id,
                contact_user_id=friend.id,
                nickname="Teammate",
                contact_action="work"
            )
            db.session.add(c)
            db.session.commit()

            assert c.contact_action == "work"
            assert c.created_date is not None
            assert isinstance(c.created_date, datetime)

    @pytest.mark.unit
    def test_contact_required_fields(self, app):
        """Les champs user_id, contact_user_id et nickname sont requis."""
        with app.app_context():
            owner = self._create_user("u1")
            friend = self._create_user("u2")

            # Sans nickname
            db.session.add(Contact(user_id=owner.id, contact_user_id=friend.id, nickname=None))
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

            # Sans user_id
            db.session.add(Contact(user_id=None, contact_user_id=friend.id, nickname="NoOwner"))
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

            # Sans contact_user_id
            db.session.add(Contact(user_id=owner.id, contact_user_id=None, nickname="NoFriend"))
            with pytest.raises(Exception):
                db.session.commit()

    # === RELATIONS ===

    @pytest.mark.unit
    def test_contact_relations(self, app):
        """Test des relations entre Contact et User."""
        with app.app_context():
            owner = self._create_user("owner_rel")
            friend = self._create_user("friend_rel")

            contact = Contact(
                user_id=owner.id,
                contact_user_id=friend.id,
                nickname="Pal",
                contact_action="social"
            )
            db.session.add(contact)
            db.session.commit()

            owner_db = db.session.get(User, owner.id)
            assert len(owner_db.contacts) == 1
            assert owner_db.contacts[0].nickname == "Pal"
            assert owner_db.contacts[0].contact_user.username == friend.username

    @pytest.mark.unit
    def test_cannot_add_self_as_contact(self, app):
        """Un utilisateur peut techniquement s'ajouter lui-même (pas de contrainte CHECK)."""
        with app.app_context():
            user = self._create_user("selfuser")
            contact = Contact(user_id=user.id, contact_user_id=user.id, nickname="Moi-même")
            db.session.add(contact)
            db.session.commit()
            
            # Le modèle n'empêche pas cela, mais la logique métier devrait (dans les routes)
            assert contact.user_id == contact.contact_user_id
            assert contact.id is not None

    @pytest.mark.unit
    def test_duplicate_contact_allowed_or_not(self, app):
        """Deux contacts identiques entre les mêmes users (selon modèle)."""
        with app.app_context():
            owner = self._create_user("dupowner")
            friend = self._create_user("dupfriend")

            c1 = Contact(user_id=owner.id, contact_user_id=friend.id, nickname="First")
            c2 = Contact(user_id=owner.id, contact_user_id=friend.id, nickname="Second")
            db.session.add_all([c1, c2])
            db.session.commit()

            # Le modèle n'impose pas de contrainte unique -> les deux sont créés
            contacts = Contact.query.filter_by(user_id=owner.id).all()
            assert len(contacts) == 2

    # === REPRESENTATION ET SERIALISATION ===

    @pytest.mark.unit
    def test_contact_repr_and_to_dict(self, app):
        """Vérifie __repr__ et to_dict()."""
        with app.app_context():
            owner = self._create_user("owner_repr")
            friend = self._create_user("friend_repr")

            c = Contact(
                user_id=owner.id,
                contact_user_id=friend.id,
                nickname="Workmate",
                contact_action="assist"
            )
            db.session.add(c)
            db.session.commit()

            # Repr
            rep = repr(c)
            assert "<Contact" in rep
            assert str(c.id) in rep
            assert "Workmate" in rep

            # to_dict
            d = c.to_dict()
            assert d["id"] == c.id
            assert d["user_id"] == owner.id
            assert d["contact_user_id"] == friend.id
            assert d["nickname"] == "Workmate"
            assert "created_date" in d
            assert "T" in d["created_date"]  # format ISO8601

    # === RECHERCHES ET FILTRES ===

    @pytest.mark.unit
    def test_contact_query_filters(self, app):
        """Test des filtres simples sur les contacts."""
        with app.app_context():
            owner = self._create_user("queryowner")
            a = self._create_user("usera")
            b = self._create_user("userb")

            c1 = Contact(user_id=owner.id, contact_user_id=a.id, nickname="Teammate", contact_action="work")
            c2 = Contact(user_id=owner.id, contact_user_id=b.id, nickname="Neighbor", contact_action="social")
            db.session.add_all([c1, c2])
            db.session.commit()

            # Rechercher par action
            work_contacts = Contact.query.filter_by(contact_action="work").all()
            assert any("Teammate" in c.nickname for c in work_contacts)

            # Rechercher par owner
            owner_contacts = Contact.query.filter_by(user_id=owner.id).all()
            assert len(owner_contacts) == 2

            # Rechercher par nickname (LIKE)
            neighbor = Contact.query.filter(Contact.nickname.like("%Neigh%")).first()
            assert neighbor.contact_action == "social"

    # === CAS LIMITES ===

    @pytest.mark.unit
    def test_contact_long_nickname(self, app):
        """Test d'un nickname très long (limite de 80 caractères)."""
        with app.app_context():
            owner = self._create_user("long")
            friend = self._create_user("buddy")
            long_nick = "A" * 80
            c = Contact(user_id=owner.id, contact_user_id=friend.id, nickname=long_nick)
            db.session.add(c)
            db.session.commit()
            assert len(c.nickname) == 80

    @pytest.mark.unit
    def test_contact_with_null_action(self, app):
        """contact_action peut être None."""
        with app.app_context():
            owner = self._create_user("nullowner")
            friend = self._create_user("nullfriend")
            c = Contact(user_id=owner.id, contact_user_id=friend.id, nickname="NoAction", contact_action=None)
            db.session.add(c)
            db.session.commit()
            assert c.contact_action is None

    @pytest.mark.unit
    def test_contact_date_format_and_precision(self, app):
        """Vérifie le format ISO et la précision de la date."""
        with app.app_context():
            owner = self._create_user("dateowner")
            friend = self._create_user("datefriend")
            c = Contact(user_id=owner.id, contact_user_id=friend.id, nickname="Timed")
            db.session.add(c)
            db.session.commit()

            iso_str = c.created_date.isoformat()
            assert "T" in iso_str
            diff = datetime.now(timezone.utc).replace(tzinfo=None) - c.created_date.replace(tzinfo=None)
            assert abs(diff) < timedelta(seconds=5)

    @pytest.mark.unit
    def test_contact_delete_user_fails(self, app):
        """Suppression d'un utilisateur lié à un contact doit lever une erreur."""
        with app.app_context():
            owner = self._create_user("todel")
            friend = self._create_user("todel_friend")

            contact = Contact(user_id=owner.id, contact_user_id=friend.id, nickname="Friendship")
            db.session.add(contact)
            db.session.commit()

            db.session.delete(owner)
            with pytest.raises(Exception):
                db.session.commit()
