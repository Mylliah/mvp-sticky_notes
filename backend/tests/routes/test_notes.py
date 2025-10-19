"""
Tests pour les routes de gestion des notes.
"""
import pytest
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Note, Assignment


def get_error_message(response):
    """Helper pour extraire le message d'erreur de la réponse."""
    data = response.get_json()
    if data is None:
        return ""
    return data.get('description') or data.get('message') or data.get('error') or str(data)


def create_user_and_login(client, app, username, email, password):
    """Helper pour créer un utilisateur et obtenir son token JWT."""
    with app.app_context():
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    # Login pour obtenir le token
    response = client.post('/v1/auth/login', json={
        'email': email,
        'password': password
    })
    token = response.get_json()['access_token']
    return token, user_id


class TestNotesRoutes:
    """Tests pour les endpoints de notes."""

    # === POST /notes - Créer une note ===

    @pytest.mark.integration
    def test_create_note_success(self, client, app):
        """Créer une note avec succès."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token}'},
                json={'content': 'Ma première note'}
            )
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['content'] == 'Ma première note'
            assert data['creator_id'] == user_id
            assert data['important'] is False

    @pytest.mark.integration
    def test_create_note_with_all_fields(self, client, app):
        """Créer une note avec tous les champs."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'content': 'Note importante',
                    'important': True
                }
            )
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['content'] == 'Note importante'
            assert data['important'] is True

    @pytest.mark.integration
    def test_create_note_missing_content(self, client, app):
        """Créer une note sans contenu échoue."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token}'},
                json={}
            )
            
            assert response.status_code == 400
            assert 'Missing content' in get_error_message(response)

    @pytest.mark.integration
    def test_create_note_requires_auth(self, client, app):
        """Créer une note nécessite une authentification."""
        with app.app_context():
            response = client.post('/v1/notes', json={
                'content': 'Test'
            })
            
            assert response.status_code == 401

    # === GET /notes - Lister les notes ===

    @pytest.mark.integration
    def test_list_notes_empty(self, client, app):
        """Lister les notes quand il n'y en a aucune."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/notes',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['notes'] == []
            assert data['total'] == 0
            assert data['page'] == 1
            assert data['per_page'] == 20

    @pytest.mark.integration
    def test_list_notes_with_notes(self, client, app):
        """Lister les notes existantes."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer quelques notes
            note1 = Note(content='Note 1', creator_id=user_id)
            note2 = Note(content='Note 2', creator_id=user_id, important=True)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            response = client.get('/v1/notes',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 2
            assert data['total'] == 2
            # Les notes sont maintenant triées par date décroissante (plus récente en premier)
            assert data['notes'][0]['content'] == 'Note 2'
            assert data['notes'][1]['content'] == 'Note 1'
            assert data['notes'][0]['important'] is True

    @pytest.mark.integration
    def test_list_notes_requires_auth(self, client, app):
        """Lister les notes nécessite une authentification."""
        with app.app_context():
            response = client.get('/v1/notes')
            
            assert response.status_code == 401

    # === GET /notes/<id> - Récupérer une note ===

    @pytest.mark.integration
    def test_get_note_success(self, client, app):
        """Récupérer une note par son ID."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test note', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.get(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == note_id
            assert data['content'] == 'Test note'

    @pytest.mark.integration
    def test_get_note_not_found(self, client, app):
        """Récupérer une note inexistante retourne 404."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/notes/99999',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_get_note_requires_auth(self, client, app):
        """Récupérer une note nécessite une authentification."""
        with app.app_context():
            response = client.get('/v1/notes/1')
            
            assert response.status_code == 401

    # === GET /notes/<id>/details - Récupérer les détails ===

    @pytest.mark.integration
    def test_get_note_details_success(self, client, app):
        """Récupérer les détails d'une note."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test note', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.get(f'/v1/notes/{note_id}/details',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == note_id
            assert 'assigned_to' in data

    @pytest.mark.integration
    def test_get_note_details_with_assignment(self, client, app):
        """Récupérer les détails d'une note avec assignation."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test note', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            
            # Créer une assignation
            assignment = Assignment(note_id=note.id, user_id=user_id)
            db.session.add(assignment)
            db.session.commit()
            
            response = client.get(f'/v1/notes/{note.id}/details',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['assigned_to'] == user_id

    @pytest.mark.integration
    def test_get_note_details_not_found(self, client, app):
        """Récupérer les détails d'une note inexistante retourne 404."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/notes/99999/details',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_get_note_details_requires_auth(self, client, app):
        """Récupérer les détails nécessite une authentification."""
        with app.app_context():
            response = client.get('/v1/notes/1/details')
            
            assert response.status_code == 401

    # === PUT /notes/<id> - Modifier une note ===

    @pytest.mark.integration
    def test_update_note_success(self, client, app):
        """Modifier une note avec succès."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Old content', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.put(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'},
                json={'content': 'New content', 'important': True}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['content'] == 'New content'
            assert data['important'] is True
            assert data['update_date'] is not None

    @pytest.mark.integration
    def test_update_note_missing_content(self, client, app):
        """Modifier une note sans contenu échoue."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.put(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'},
                json={'important': False}
            )
            
            assert response.status_code == 400
            assert 'Missing content' in get_error_message(response)

    @pytest.mark.integration
    def test_update_note_not_found(self, client, app):
        """Modifier une note inexistante retourne 404."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.put('/v1/notes/99999',
                headers={'Authorization': f'Bearer {token}'},
                json={'content': 'Test'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_update_note_requires_auth(self, client, app):
        """Modifier une note nécessite une authentification."""
        with app.app_context():
            response = client.put('/v1/notes/1', json={'content': 'Test'})
            
            assert response.status_code == 401

    # === DELETE /notes/<id> - Supprimer une note (soft delete) ===

    @pytest.mark.integration
    def test_delete_note_success(self, client, app):
        """Supprimer une note (soft delete)."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='To delete', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.delete(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['delete_date'] is not None
            
            # Vérifier que la note existe toujours en DB (soft delete)
            deleted_note = Note.query.get(note_id)
            assert deleted_note is not None
            assert deleted_note.delete_date is not None

    @pytest.mark.integration
    def test_delete_note_not_found(self, client, app):
        """Supprimer une note inexistante retourne 404."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.delete('/v1/notes/99999',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_delete_note_requires_auth(self, client, app):
        """Supprimer une note nécessite une authentification."""
        with app.app_context():
            response = client.delete('/v1/notes/1')
            
            assert response.status_code == 401

    # === GET /notes avec filtres et tri ===

    @pytest.mark.integration
    def test_list_notes_filter_important(self, client, app):
        """Filtrer les notes marquées importantes par le créateur."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note1 = Note(content='Important note', creator_id=user_id, important=True)
            note2 = Note(content='Normal note', creator_id=user_id, important=False)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            response = client.get('/v1/notes?filter=important',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 1
            assert data['notes'][0]['content'] == 'Important note'
            assert data['notes'][0]['important'] is True

    @pytest.mark.integration
    def test_list_notes_filter_important_by_me(self, client, app):
        """Filtrer les notes marquées prioritaires par le destinataire."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note1 = Note(content='Priority note', creator_id=user_id)
            note2 = Note(content='Normal note', creator_id=user_id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            # Créer des assignations
            from app.models import Assignment
            assignment1 = Assignment(note_id=note1.id, user_id=user_id, recipient_priority=True)
            assignment2 = Assignment(note_id=note2.id, user_id=user_id, recipient_priority=False)
            db.session.add_all([assignment1, assignment2])
            db.session.commit()
            
            response = client.get('/v1/notes?filter=important_by_me',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 1
            assert data['notes'][0]['content'] == 'Priority note'

    @pytest.mark.integration
    def test_list_notes_filter_unread(self, client, app):
        """Filtrer les notes non lues."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note1 = Note(content='Unread note', creator_id=user_id)
            note2 = Note(content='Read note', creator_id=user_id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            # Créer des assignations
            from app.models import Assignment
            assignment1 = Assignment(note_id=note1.id, user_id=user_id, is_read=False)
            assignment2 = Assignment(note_id=note2.id, user_id=user_id, is_read=True)
            db.session.add_all([assignment1, assignment2])
            db.session.commit()
            
            response = client.get('/v1/notes?filter=unread',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 1
            assert data['notes'][0]['content'] == 'Unread note'

    @pytest.mark.integration
    def test_list_notes_filter_received(self, client, app):
        """Filtrer les notes reçues (assignées mais pas créées par l'utilisateur)."""
        token1, user1_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer un deuxième utilisateur
            from werkzeug.security import generate_password_hash
            user2 = User(
                username='user2',
                email='user2@test.com',
                password_hash=generate_password_hash('pass')
            )
            db.session.add(user2)
            db.session.commit()
            user2_id = user2.id
            
            # Créer des notes
            note1 = Note(content='Received note', creator_id=user2_id)  # Créée par user2
            note2 = Note(content='Sent note', creator_id=user1_id)  # Créée par user1
            db.session.add_all([note1, note2])
            db.session.commit()
            
            # Assigner note1 à user1 (reçue)
            from app.models import Assignment
            assignment = Assignment(note_id=note1.id, user_id=user1_id)
            db.session.add(assignment)
            db.session.commit()
            
            response = client.get('/v1/notes?filter=received',
                headers={'Authorization': f'Bearer {token1}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 1
            assert data['notes'][0]['content'] == 'Received note'

    @pytest.mark.integration
    def test_list_notes_filter_sent(self, client, app):
        """Filtrer les notes envoyées (créées par l'utilisateur)."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer un deuxième utilisateur
            from werkzeug.security import generate_password_hash
            user2 = User(
                username='user2',
                email='user2@test.com',
                password_hash=generate_password_hash('pass')
            )
            db.session.add(user2)
            db.session.commit()
            
            # Créer des notes
            note1 = Note(content='Sent note', creator_id=user_id)  # Créée par user1
            note2 = Note(content='Received note', creator_id=user2.id)  # Créée par user2
            db.session.add_all([note1, note2])
            db.session.commit()
            
            # Assigner note2 à user1
            from app.models import Assignment
            assignment = Assignment(note_id=note2.id, user_id=user_id)
            db.session.add(assignment)
            db.session.commit()
            
            response = client.get('/v1/notes?filter=sent',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 1
            assert data['notes'][0]['content'] == 'Sent note'

    @pytest.mark.integration
    def test_list_notes_sort_date_asc(self, client, app):
        """Trier les notes par date croissante."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note1 = Note(content='Old note', creator_id=user_id)
            note2 = Note(content='New note', creator_id=user_id)
            db.session.add_all([note1, note2])
            db.session.commit()
            
            response = client.get('/v1/notes?sort=date_asc',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 2
            assert data['notes'][0]['content'] == 'Old note'
            assert data['notes'][1]['content'] == 'New note'

    @pytest.mark.integration
    def test_list_notes_sort_important_first(self, client, app):
        """Trier les notes avec les importantes en premier."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note1 = Note(content='Normal note', creator_id=user_id, important=False)
            note2 = Note(content='Important note', creator_id=user_id, important=True)
            note3 = Note(content='Another normal', creator_id=user_id, important=False)
            db.session.add_all([note1, note2, note3])
            db.session.commit()
            
            response = client.get('/v1/notes?sort=important_first',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 3
            assert data['notes'][0]['content'] == 'Important note'
            assert data['notes'][0]['important'] is True

    # === Tests de pagination ===

    @pytest.mark.integration
    def test_list_notes_pagination_default(self, client, app):
        """Test pagination avec valeurs par défaut (page=1, per_page=20)."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer 5 notes
            for i in range(5):
                note = Note(content=f'Note {i+1}', creator_id=user_id)
                db.session.add(note)
            db.session.commit()
            
            response = client.get('/v1/notes',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 5
            assert data['total'] == 5
            assert data['page'] == 1
            assert data['per_page'] == 20
            assert data['pages'] == 1
            assert data['has_next'] is False
            assert data['has_prev'] is False

    @pytest.mark.integration
    def test_list_notes_pagination_custom_per_page(self, client, app):
        """Test pagination avec per_page personnalisé."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer 10 notes
            for i in range(10):
                note = Note(content=f'Note {i+1}', creator_id=user_id)
                db.session.add(note)
            db.session.commit()
            
            # Demander 3 notes par page
            response = client.get('/v1/notes?per_page=3',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 3
            assert data['total'] == 10
            assert data['page'] == 1
            assert data['per_page'] == 3
            assert data['pages'] == 4
            assert data['has_next'] is True
            assert data['has_prev'] is False

    @pytest.mark.integration
    def test_list_notes_pagination_page_2(self, client, app):
        """Test pagination page 2."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer 10 notes
            for i in range(10):
                note = Note(content=f'Note {i+1}', creator_id=user_id)
                db.session.add(note)
            db.session.commit()
            
            # Demander page 2 avec 3 notes par page
            response = client.get('/v1/notes?page=2&per_page=3',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 3
            assert data['total'] == 10
            assert data['page'] == 2
            assert data['per_page'] == 3
            assert data['pages'] == 4
            assert data['has_next'] is True
            assert data['has_prev'] is True

    @pytest.mark.integration
    def test_list_notes_pagination_last_page(self, client, app):
        """Test pagination dernière page (incomplète)."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer 10 notes
            for i in range(10):
                note = Note(content=f'Note {i+1}', creator_id=user_id)
                db.session.add(note)
            db.session.commit()
            
            # Demander page 4 (dernière) avec 3 notes par page
            response = client.get('/v1/notes?page=4&per_page=3',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['notes']) == 1  # Seulement 1 note sur la dernière page
            assert data['total'] == 10
            assert data['page'] == 4
            assert data['per_page'] == 3
            assert data['pages'] == 4
            assert data['has_next'] is False
            assert data['has_prev'] is True

    @pytest.mark.integration
    def test_list_notes_pagination_max_per_page(self, client, app):
        """Test que per_page est limité à 100 max."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer 5 notes
            for i in range(5):
                note = Note(content=f'Note {i+1}', creator_id=user_id)
                db.session.add(note)
            db.session.commit()
            
            # Demander 200 notes par page (devrait être limité à 100)
            response = client.get('/v1/notes?per_page=200',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['per_page'] == 100  # Limité à 100

    @pytest.mark.integration
    def test_list_notes_pagination_invalid_values(self, client, app):
        """Test que les valeurs invalides sont corrigées."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            note = Note(content='Test', creator_id=user_id)
            db.session.add(note)
            db.session.commit()
            
            # page=0 devrait être corrigé à 1
            response = client.get('/v1/notes?page=0',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['page'] == 1
            
            # per_page=-5 devrait être corrigé à 20
            response = client.get('/v1/notes?per_page=-5',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['per_page'] == 20

    # === GET /notes/<id>/assignments - Vue créateur sur les destinataires ===

    @pytest.mark.integration
    def test_get_note_assignments_as_creator(self, client, app):
        """Le créateur peut voir tous les destinataires et leurs statuts."""
        token, creator_id = create_user_and_login(client, app, 'creator', 'creator@test.com', 'pass')
        
        with app.app_context():
            # Créer des destinataires
            user1 = User(username='user1', email='user1@test.com', password_hash=generate_password_hash('pass'))
            user2 = User(username='user2', email='user2@test.com', password_hash=generate_password_hash('pass'))
            user3 = User(username='user3', email='user3@test.com', password_hash=generate_password_hash('pass'))
            db.session.add_all([user1, user2, user3])
            db.session.commit()
            
            # Créer une note
            note = Note(content='Test note', creator_id=creator_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            # Créer des assignations avec différents statuts
            assignment1 = Assignment(note_id=note_id, user_id=user1.id, is_read=True)
            assignment2 = Assignment(note_id=note_id, user_id=user2.id, is_read=False)
            assignment3 = Assignment(note_id=note_id, user_id=user3.id, is_read=True, recipient_priority=True)
            db.session.add_all([assignment1, assignment2, assignment3])
            db.session.commit()
            
            response = client.get(f'/v1/notes/{note_id}/assignments',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Vérifier la structure
            assert data['note_id'] == note_id
            assert data['creator_id'] == creator_id
            assert data['total_recipients'] == 3
            assert data['read_count'] == 2  # user1 et user3 ont lu
            
            # Vérifier les assignations
            assert len(data['assignments']) == 3
            
            # Vérifier les détails
            usernames = [a['username'] for a in data['assignments']]
            assert 'user1' in usernames
            assert 'user2' in usernames
            assert 'user3' in usernames
            
            # Vérifier les statuts is_read
            read_statuses = {a['username']: a['is_read'] for a in data['assignments']}
            assert read_statuses['user1'] is True
            assert read_statuses['user2'] is False
            assert read_statuses['user3'] is True
            
            # Vérifier que recipient_priority n'est PAS exposé (privé)
            for assignment in data['assignments']:
                assert 'recipient_priority' not in assignment

    @pytest.mark.integration
    def test_get_note_assignments_forbidden_not_creator(self, client, app):
        """Un destinataire ne peut pas voir les autres destinataires."""
        token_creator, creator_id = create_user_and_login(client, app, 'creator', 'creator@test.com', 'pass')
        token_user, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer une note
            note = Note(content='Test note', creator_id=creator_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            # Assigner à user1
            assignment = Assignment(note_id=note_id, user_id=user_id)
            db.session.add(assignment)
            db.session.commit()
            
            # user1 essaie d'accéder aux assignations
            response = client.get(f'/v1/notes/{note_id}/assignments',
                headers={'Authorization': f'Bearer {token_user}'}
            )
            
            assert response.status_code == 403
            assert 'Only the creator can view all assignments' in get_error_message(response)

    @pytest.mark.integration
    def test_get_note_assignments_not_found(self, client, app):
        """Erreur 404 si la note n'existe pas."""
        token, _ = create_user_and_login(client, app, 'creator', 'creator@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/notes/99999/assignments',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404

    @pytest.mark.integration
    def test_get_note_assignments_empty(self, client, app):
        """Le créateur peut voir une note sans destinataires."""
        token, creator_id = create_user_and_login(client, app, 'creator', 'creator@test.com', 'pass')
        
        with app.app_context():
            # Créer une note sans assignation
            note = Note(content='Test note', creator_id=creator_id)
            db.session.add(note)
            db.session.commit()
            note_id = note.id
            
            response = client.get(f'/v1/notes/{note_id}/assignments',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['total_recipients'] == 0
            assert data['read_count'] == 0
            assert len(data['assignments']) == 0
