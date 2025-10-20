"""
Tests pour la suppression de notes par créateur ou destinataire avec traçabilité.
"""
import pytest
from flask_jwt_extended import create_access_token
from app.models import Note, User, Assignment, Contact
from app import db


class TestNoteDeletionByCreator:
    """Tests pour la suppression de notes par le créateur."""
    
    def test_creator_can_delete_note(self, client, app):
        """Le créateur peut supprimer sa propre note."""
        with app.app_context():
            # Créer un utilisateur et une note
            user = User(username="alice", email="alice@test.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            
            note = Note(content="Test note", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            user_id = user.id
            
            # Générer token JWT
            token = create_access_token(identity=str(user_id))
            
            # Supprimer la note
            response = client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            
            # Vérifier que delete_date et deleted_by sont présents
            note_deleted = Note.query.get(note_id)
            assert note_deleted.delete_date is not None
            assert note_deleted.deleted_by == user.id
    
    def test_creator_deleted_by_in_details(self, client, app):
        """Le champ deleted_by apparaît dans les détails de la note."""
        with app.app_context():
            # Créer utilisateur et note
            user = User(username="bob", email="bob@test.com", password_hash="hash")
            db.session.add(user)
            db.session.commit()
            
            note = Note(content="Test note", creator_id=user.id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            user_id = user.id
            
            # Générer token et supprimer
            token = create_access_token(identity=str(user_id))
            
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Récupérer les détails
            response = client.get(
                f'/v1/notes/{note_id}/details',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            details = response.json
            assert details['delete_date'] is not None
            assert details['deleted_by'] == user_id


class TestNoteDeletionByRecipient:
    """Tests pour la suppression de notes par le destinataire."""
    
    def test_recipient_can_delete_assigned_note(self, client, app):
        """Le destinataire peut supprimer une note qui lui est assignée."""
        with app.app_context():
            # Créer Alice (créateur) et Bob (destinataire)
            alice = User(username="alice2", email="alice2@test.com", password_hash="hash")
            bob = User(username="bob2", email="bob2@test.com", password_hash="hash")
            db.session.add_all([alice, bob])
            db.session.commit()
            
            # Contacts mutuels
            contact_ab = Contact(user_id=alice.id, contact_user_id=bob.id, nickname="contact")
            contact_ba = Contact(user_id=bob.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ab, contact_ba])
            db.session.commit()
            
            # Alice crée une note
            note = Note(content="Note pour Bob", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            # Alice assigne la note à Bob
            assignment = Assignment(note_id=note.id, user_id=bob.id)
            db.session.add(assignment)
            db.session.commit()
            
            note_id = note.id
            bob_id = bob.id
            
            # Générer token pour Bob
            token_bob = create_access_token(identity=str(bob_id))
            
            # Bob supprime la note
            response = client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            
            assert response.status_code == 200
            
            # Vérifier que delete_date et deleted_by sont présents
            note_deleted = Note.query.get(note_id)
            assert note_deleted.delete_date is not None
            assert note_deleted.deleted_by == bob_id  # Bob a supprimé, pas Alice
    
    def test_recipient_deleted_by_shows_recipient_id(self, client, app):
        """Le champ deleted_by montre l'ID du destinataire qui a supprimé."""
        with app.app_context():
            # Créer Alice et Charlie
            alice = User(username="alice3", email="alice3@test.com", password_hash="hash")
            charlie = User(username="charlie", email="charlie@test.com", password_hash="hash")
            db.session.add_all([alice, charlie])
            db.session.commit()
            
            # Contacts mutuels
            contact_ac = Contact(user_id=alice.id, contact_user_id=charlie.id, nickname="contact")
            contact_ca = Contact(user_id=charlie.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ac, contact_ca])
            db.session.commit()
            
            # Note + assignment
            note = Note(content="Note pour Charlie", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=charlie.id)
            db.session.add(assignment)
            db.session.commit()
            
            note_id = note.id
            charlie_id = charlie.id
            
            # Générer token pour Charlie et supprimer
            token_charlie = create_access_token(identity=str(charlie_id))
            
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_charlie}'}
            )
            
            # Vérifier dans les détails
            response = client.get(
                f'/v1/notes/{note_id}/details',
                headers={'Authorization': f'Bearer {token_charlie}'}
            )
            
            assert response.status_code == 200
            details = response.json
            assert details['deleted_by'] == charlie_id  # Prouve que Charlie a supprimé


class TestNoteDeletionAuthorization:
    """Tests pour les autorisations de suppression."""
    
    def test_non_creator_non_recipient_cannot_delete(self, client, app):
        """Un utilisateur qui n'est ni créateur ni destinataire ne peut pas supprimer."""
        with app.app_context():
            # Créer Alice (créateur), Bob (destinataire), Eve (outsider)
            alice = User(username="alice4", email="alice4@test.com", password_hash="hash")
            bob = User(username="bob4", email="bob4@test.com", password_hash="hash")
            eve = User(username="eve", email="eve@test.com", password_hash="hash")
            db.session.add_all([alice, bob, eve])
            db.session.commit()
            
            # Contacts Alice-Bob (pas Eve)
            contact_ab = Contact(user_id=alice.id, contact_user_id=bob.id, nickname="contact")
            contact_ba = Contact(user_id=bob.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ab, contact_ba])
            db.session.commit()
            
            # Note assignée à Bob
            note = Note(content="Note privée", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=bob.id)
            db.session.add(assignment)
            db.session.commit()
            
            note_id = note.id
            eve_id = eve.id
            
            # Générer token pour Eve
            token_eve = create_access_token(identity=str(eve_id))
            
            # Eve tente de supprimer
            response = client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_eve}'}
            )
            
            assert response.status_code == 403
            assert b'Only the creator or recipient can delete' in response.data
            
            # Vérifier que la note n'est PAS supprimée
            note_not_deleted = Note.query.get(note_id)
            assert note_not_deleted.delete_date is None
            assert note_not_deleted.deleted_by is None


class TestNoteDeletionTraceability:
    """Tests pour la traçabilité complète des suppressions."""
    
    def test_creator_deletion_traceable(self, client, app):
        """Quand le créateur supprime, on sait que c'est lui."""
        with app.app_context():
            alice = User(username="alice5", email="alice5@test.com", password_hash="hash")
            db.session.add(alice)
            db.session.commit()
            
            note = Note(content="Note Alice", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            note_id = note.id
            alice_id = alice.id
            
            # Générer token pour Alice
            token = create_access_token(identity=str(alice_id))
            
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            note_deleted = Note.query.get(note_id)
            assert note_deleted.deleted_by == alice_id
    
    def test_recipient_deletion_different_from_creator(self, client, app):
        """Quand le destinataire supprime, deleted_by ≠ creator_id."""
        with app.app_context():
            alice = User(username="alice6", email="alice6@test.com", password_hash="hash")
            bob = User(username="bob6", email="bob6@test.com", password_hash="hash")
            db.session.add_all([alice, bob])
            db.session.commit()
            
            contact_ab = Contact(user_id=alice.id, contact_user_id=bob.id, nickname="contact")
            contact_ba = Contact(user_id=bob.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ab, contact_ba])
            db.session.commit()
            
            note = Note(content="Note pour Bob", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=bob.id)
            db.session.add(assignment)
            db.session.commit()
            
            note_id = note.id
            alice_id = alice.id
            bob_id = bob.id
            
            # Générer token pour Bob
            token = create_access_token(identity=str(bob_id))
            
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            note_deleted = Note.query.get(note_id)
            assert note_deleted.creator_id == alice_id  # Alice est créateur
            assert note_deleted.deleted_by == bob_id  # Mais Bob a supprimé
            assert note_deleted.deleted_by != note_deleted.creator_id  # Preuve de différence


class TestNoteDeletionConfidentiality:
    """Tests pour la confidentialité du champ deleted_by dans GET /notes/:id."""
    
    def test_creator_sees_deleted_by_info(self, client, app):
        """Le créateur voit deleted_by_username et deleted_by_id quand un destinataire supprime."""
        with app.app_context():
            # Créer Alice (créateur) et Bob (destinataire)
            alice = User(username="alice7", email="alice7@test.com", password_hash="hash")
            bob = User(username="bob7", email="bob7@test.com", password_hash="hash")
            db.session.add_all([alice, bob])
            db.session.commit()
            
            # Contacts mutuels
            contact_ab = Contact(user_id=alice.id, contact_user_id=bob.id, nickname="contact")
            contact_ba = Contact(user_id=bob.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ab, contact_ba])
            db.session.commit()
            
            # Alice crée une note
            note = Note(content="Note pour Bob", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            # Alice assigne à Bob
            assignment = Assignment(note_id=note.id, user_id=bob.id)
            db.session.add(assignment)
            db.session.commit()
            
            note_id = note.id
            alice_id = alice.id
            bob_id = bob.id
            
            # Bob supprime la note
            token_bob = create_access_token(identity=str(bob_id))
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            
            # Alice consulte la note (GET /notes/:id)
            token_alice = create_access_token(identity=str(alice_id))
            response = client.get(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            
            assert response.status_code == 200
            data = response.json
            
            # Alice (créateur) voit deleted_by
            assert 'deleted_by_id' in data
            assert 'deleted_by_username' in data
            assert data['deleted_by_id'] == bob_id
            assert data['deleted_by_username'] == 'bob7'
            assert data['delete_date'] is not None
    
    def test_recipient_does_not_see_deleted_by_info(self, client, app):
        """Le destinataire qui a supprimé ne voit PAS deleted_by_username (confidentialité)."""
        with app.app_context():
            # Créer Alice et Bob
            alice = User(username="alice8", email="alice8@test.com", password_hash="hash")
            bob = User(username="bob8", email="bob8@test.com", password_hash="hash")
            db.session.add_all([alice, bob])
            db.session.commit()
            
            # Contacts
            contact_ab = Contact(user_id=alice.id, contact_user_id=bob.id, nickname="contact")
            contact_ba = Contact(user_id=bob.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ab, contact_ba])
            db.session.commit()
            
            # Note + assignment
            note = Note(content="Note pour Bob", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=bob.id)
            db.session.add(assignment)
            db.session.commit()
            
            note_id = note.id
            bob_id = bob.id
            
            # Bob supprime
            token_bob = create_access_token(identity=str(bob_id))
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            
            # Bob consulte la note (GET /notes/:id)
            response = client.get(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            
            assert response.status_code == 200
            data = response.json
            
            # Bob ne voit PAS deleted_by car il n'est pas le créateur (confidentialité)
            assert 'deleted_by_id' not in data
            assert 'deleted_by_username' not in data
            assert 'deleted_by_creator' not in data  # Il n'a pas supprimé, donc pas de flag créateur
            # Mais il voit que c'est supprimé
            assert data['delete_date'] is not None
    
    def test_other_recipient_does_not_see_deleted_by_info(self, client, app):
        """Un autre destinataire ne voit PAS qui a supprimé (confidentialité inter-destinataires)."""
        with app.app_context():
            # Créer Alice, Bob, Charlie
            alice = User(username="alice9", email="alice9@test.com", password_hash="hash")
            bob = User(username="bob9", email="bob9@test.com", password_hash="hash")
            charlie = User(username="charlie9", email="charlie9@test.com", password_hash="hash")
            db.session.add_all([alice, bob, charlie])
            db.session.commit()
            
            # Contacts Alice-Bob et Alice-Charlie
            contact_ab = Contact(user_id=alice.id, contact_user_id=bob.id, nickname="contact")
            contact_ba = Contact(user_id=bob.id, contact_user_id=alice.id, nickname="contact")
            contact_ac = Contact(user_id=alice.id, contact_user_id=charlie.id, nickname="contact")
            contact_ca = Contact(user_id=charlie.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ab, contact_ba, contact_ac, contact_ca])
            db.session.commit()
            
            # Note assignée à Bob et Charlie
            note = Note(content="Note pour Bob et Charlie", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            assignment_bob = Assignment(note_id=note.id, user_id=bob.id)
            assignment_charlie = Assignment(note_id=note.id, user_id=charlie.id)
            db.session.add_all([assignment_bob, assignment_charlie])
            db.session.commit()
            
            note_id = note.id
            bob_id = bob.id
            charlie_id = charlie.id
            
            # Bob supprime
            token_bob = create_access_token(identity=str(bob_id))
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            
            # Charlie consulte la note
            token_charlie = create_access_token(identity=str(charlie_id))
            response = client.get(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_charlie}'}
            )
            
            assert response.status_code == 200
            data = response.json
            
            # Charlie ne voit PAS que Bob a supprimé (confidentialité)
            assert 'deleted_by_id' not in data
            assert 'deleted_by_username' not in data
            # Mais il voit que c'est supprimé
            assert data['delete_date'] is not None
    
    def test_creator_sees_own_deletion(self, client, app):
        """Le créateur qui supprime sa propre note voit deleted_by."""
        with app.app_context():
            alice = User(username="alice10", email="alice10@test.com", password_hash="hash")
            db.session.add(alice)
            db.session.commit()
            
            note = Note(content="Note Alice", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            note_id = note.id
            alice_id = alice.id
            
            # Alice supprime
            token_alice = create_access_token(identity=str(alice_id))
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            
            # Alice consulte
            response = client.get(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            
            assert response.status_code == 200
            data = response.json
            
            # Alice voit qu'elle a supprimé (elle est créateur)
            assert 'deleted_by_id' in data
            assert 'deleted_by_username' in data
            assert data['deleted_by_id'] == alice_id
            assert data['deleted_by_username'] == 'alice10'
    
    def test_recipient_sees_creator_deletion(self, client, app):
        """Le destinataire voit si le CRÉATEUR a supprimé (signal de fin de tâche)."""
        with app.app_context():
            # Créer Alice (créateur) et Bob (destinataire)
            alice = User(username="alice11", email="alice11@test.com", password_hash="hash")
            bob = User(username="bob11", email="bob11@test.com", password_hash="hash")
            db.session.add_all([alice, bob])
            db.session.commit()
            
            # Contacts
            contact_ab = Contact(user_id=alice.id, contact_user_id=bob.id, nickname="contact")
            contact_ba = Contact(user_id=bob.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ab, contact_ba])
            db.session.commit()
            
            # Note assignée à Bob
            note = Note(content="Acheter du pain", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            assignment = Assignment(note_id=note.id, user_id=bob.id)
            db.session.add(assignment)
            db.session.commit()
            
            note_id = note.id
            alice_id = alice.id
            bob_id = bob.id
            
            # Alice (créateur) supprime la note
            token_alice = create_access_token(identity=str(alice_id))
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            
            # Bob consulte la note
            token_bob = create_access_token(identity=str(bob_id))
            response = client.get(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            
            assert response.status_code == 200
            data = response.json
            
            # Bob voit que le CRÉATEUR a supprimé (signal de fin)
            assert 'deleted_by_creator' in data
            assert data['deleted_by_creator'] is True
            assert 'deleted_by_username' in data
            assert data['deleted_by_username'] == 'alice11'
            assert data['delete_date'] is not None
    
    def test_recipient_does_not_see_other_recipient_deletion(self, client, app):
        """Le destinataire ne voit PAS si un autre destinataire a supprimé (confidentialité)."""
        with app.app_context():
            # Créer Alice, Bob, Charlie
            alice = User(username="alice12", email="alice12@test.com", password_hash="hash")
            bob = User(username="bob12", email="bob12@test.com", password_hash="hash")
            charlie = User(username="charlie12", email="charlie12@test.com", password_hash="hash")
            db.session.add_all([alice, bob, charlie])
            db.session.commit()
            
            # Contacts
            contact_ab = Contact(user_id=alice.id, contact_user_id=bob.id, nickname="contact")
            contact_ba = Contact(user_id=bob.id, contact_user_id=alice.id, nickname="contact")
            contact_ac = Contact(user_id=alice.id, contact_user_id=charlie.id, nickname="contact")
            contact_ca = Contact(user_id=charlie.id, contact_user_id=alice.id, nickname="contact")
            db.session.add_all([contact_ab, contact_ba, contact_ac, contact_ca])
            db.session.commit()
            
            # Note assignée à Bob et Charlie
            note = Note(content="Note pour tous", creator_id=alice.id)
            db.session.add(note)
            db.session.commit()
            
            assignment_bob = Assignment(note_id=note.id, user_id=bob.id)
            assignment_charlie = Assignment(note_id=note.id, user_id=charlie.id)
            db.session.add_all([assignment_bob, assignment_charlie])
            db.session.commit()
            
            note_id = note.id
            bob_id = bob.id
            charlie_id = charlie.id
            
            # Bob (destinataire) supprime
            token_bob = create_access_token(identity=str(bob_id))
            client.delete(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            
            # Charlie consulte
            token_charlie = create_access_token(identity=str(charlie_id))
            response = client.get(
                f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token_charlie}'}
            )
            
            assert response.status_code == 200
            data = response.json
            
            # Charlie ne voit PAS que Bob a supprimé (confidentialité)
            assert 'deleted_by_creator' not in data
            assert 'deleted_by_username' not in data
            assert 'deleted_by_id' not in data
            # Mais il voit que c'est supprimé
            assert data['delete_date'] is not None
