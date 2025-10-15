"""
Tests pour les routes de gestion des contacts.
"""
import pytest
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Contact


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
        'username': username,
        'password': password
    })
    token = response.get_json()['access_token']
    return token, user_id


class TestContactsRoutes:
    """Tests pour les endpoints de contacts."""

    # === GET /contacts - Liste des contacts ===

    @pytest.mark.integration
    def test_list_contacts_includes_self(self, client, app):
        """IMPORTANT: Vérifie que l'utilisateur se voit lui-même en premier dans sa liste de contacts."""
        token, user_id = create_user_and_login(client, app, 'testuser', 'test@test.com', 'password123')
        
        with app.app_context():
            response = client.get('/v1/contacts', headers={
                'Authorization': f'Bearer {token}'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Vérifier que la liste n'est pas vide
            assert len(data) >= 1
            
            # Vérifier que le premier élément est l'utilisateur lui-même
            first_contact = data[0]
            assert first_contact['is_self'] is True
            assert first_contact['nickname'] == 'Moi'
            assert first_contact['username'] == 'testuser'
            assert first_contact['id'] == user_id

    @pytest.mark.integration
    def test_list_contacts_with_added_contacts(self, client, app):
        """Liste contient l'utilisateur lui-même + ses contacts ajoutés."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass123')
        
        with app.app_context():
            # Créer d'autres utilisateurs
            user2 = User(username='user2', email='user2@test.com', password_hash='hash')
            user3 = User(username='user3', email='user3@test.com', password_hash='hash')
            db.session.add_all([user2, user3])
            db.session.commit()
            
            # Ajouter des contacts
            response = client.post('/v1/contacts', 
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'user2', 'nickname': 'Ami 1'}
            )
            assert response.status_code == 201
            
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'user3', 'nickname': 'Ami 2'}
            )
            assert response.status_code == 201
            
            # Récupérer la liste
            response = client.get('/v1/contacts', headers={
                'Authorization': f'Bearer {token}'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Vérifier qu'on a 3 éléments (soi-même + 2 contacts)
            assert len(data) == 3
            
            # Vérifier que le premier est soi-même
            assert data[0]['is_self'] is True
            assert data[0]['nickname'] == 'Moi'
            
            # Vérifier les contacts ajoutés
            assert data[1]['is_self'] is False
            assert data[1]['nickname'] == 'Ami 1'
            assert data[2]['is_self'] is False
            assert data[2]['nickname'] == 'Ami 2'

    @pytest.mark.integration
    def test_list_contacts_empty_for_new_user(self, client, app):
        """Un nouvel utilisateur voit uniquement lui-même dans sa liste."""
        token, user_id = create_user_and_login(client, app, 'newuser', 'new@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/contacts', headers={
                'Authorization': f'Bearer {token}'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Doit avoir exactement 1 élément (lui-même)
            assert len(data) == 1
            assert data[0]['is_self'] is True
            assert data[0]['nickname'] == 'Moi'

    @pytest.mark.integration
    def test_list_contacts_requires_auth(self, client, app):
        """GET /contacts nécessite une authentification."""
        with app.app_context():
            response = client.get('/v1/contacts')
            
            assert response.status_code == 401  # Unauthorized

    @pytest.mark.integration
    def test_list_contacts_isolation(self, client, app):
        """Chaque utilisateur voit UNIQUEMENT ses propres contacts."""
        token1, user1_id = create_user_and_login(client, app, 'alice', 'alice@test.com', 'pass1')
        token2, user2_id = create_user_and_login(client, app, 'bob', 'bob@test.com', 'pass2')
        
        with app.app_context():
            # Alice ajoute Bob comme contact
            client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token1}'},
                json={'contact_username': 'bob', 'nickname': 'Bob Contact'}
            )
            
            # Vérifier la liste d'Alice (elle-même + Bob)
            response = client.get('/v1/contacts', headers={
                'Authorization': f'Bearer {token1}'
            })
            alice_contacts = response.get_json()
            assert len(alice_contacts) == 2
            assert alice_contacts[0]['username'] == 'alice'
            assert alice_contacts[1]['username'] == 'bob'
            
            # Vérifier la liste de Bob (lui-même uniquement, pas Alice)
            response = client.get('/v1/contacts', headers={
                'Authorization': f'Bearer {token2}'
            })
            bob_contacts = response.get_json()
            assert len(bob_contacts) == 1  # Bob ne voit que lui-même
            assert bob_contacts[0]['username'] == 'bob'

    # === POST /contacts - Ajouter un contact ===

    @pytest.mark.integration
    def test_create_contact_success(self, client, app):
        """Ajouter un contact existant avec succès."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer un autre utilisateur
            user2 = User(username='user2', email='user2@test.com', password_hash='hash')
            db.session.add(user2)
            db.session.commit()
            
            # Ajouter user2 comme contact
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'user2', 'nickname': 'Mon Ami'}
            )
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['nickname'] == 'Mon Ami'
            assert data['contact_user_id'] == user2.id

    @pytest.mark.integration
    def test_create_contact_cannot_add_self(self, client, app):
        """IMPORTANT: Un utilisateur NE PEUT PAS s'ajouter lui-même comme contact."""
        token, _ = create_user_and_login(client, app, 'testuser', 'test@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'testuser', 'nickname': 'Moi-même'}
            )
            
            assert response.status_code == 400
            assert 'Cannot add yourself as contact' in get_error_message(response)

    @pytest.mark.integration
    def test_create_contact_user_not_found(self, client, app):
        """Ajouter un contact inexistant échoue."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'nonexistent', 'nickname': 'Ghost'}
            )
            
            assert response.status_code == 404
            assert 'User not found' in get_error_message(response)

    @pytest.mark.integration
    def test_create_contact_duplicate(self, client, app):
        """Ajouter un contact déjà existant échoue."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            user2 = User(username='user2', email='user2@test.com', password_hash='hash')
            db.session.add(user2)
            db.session.commit()
            
            # Ajouter une première fois
            client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'user2', 'nickname': 'Ami'}
            )
            
            # Tenter d'ajouter à nouveau
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'user2', 'nickname': 'Ami 2'}
            )
            
            assert response.status_code == 400
            assert 'Contact already exists' in get_error_message(response)

    @pytest.mark.integration
    def test_create_contact_missing_fields(self, client, app):
        """Ajouter un contact sans les champs requis échoue."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Sans contact_username
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'nickname': 'Ami'}
            )
            assert response.status_code == 400
            assert 'Missing contact_username or nickname' in get_error_message(response)
            
            # Sans nickname
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'user2'}
            )
            assert response.status_code == 400
            assert 'Missing contact_username or nickname' in get_error_message(response)

    @pytest.mark.integration
    def test_create_contact_requires_auth(self, client, app):
        """POST /contacts nécessite une authentification."""
        with app.app_context():
            response = client.post('/v1/contacts', json={
                'contact_username': 'someone',
                'nickname': 'Test'
            })
            
            assert response.status_code == 401

    # === GET /contacts/assignable - Utilisateurs assignables ===

    @pytest.mark.integration
    def test_list_assignable_users_includes_self(self, client, app):
        """Liste assignable contient l'utilisateur lui-même en premier."""
        token, user_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            response = client.get('/v1/contacts/assignable', headers={
                'Authorization': f'Bearer {token}'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Au moins 1 élément (soi-même)
            assert len(data) >= 1
            
            # Le premier doit être soi-même
            assert data[0]['is_self'] is True
            assert data[0]['nickname'] == 'Moi'
            assert data[0]['id'] == user_id

    @pytest.mark.integration
    def test_list_assignable_users_with_contacts(self, client, app):
        """Liste assignable = soi-même + contacts."""
        token, _ = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer et ajouter un contact
            user2 = User(username='user2', email='user2@test.com', password_hash='hash')
            db.session.add(user2)
            db.session.commit()
            
            client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'user2', 'nickname': 'Contact'}
            )
            
            # Récupérer la liste assignable
            response = client.get('/v1/contacts/assignable', headers={
                'Authorization': f'Bearer {token}'
            })
            
            data = response.get_json()
            assert len(data) == 2
            assert data[0]['is_self'] is True
            assert data[1]['is_self'] is False
            assert data[1]['username'] == 'user2'

    @pytest.mark.integration
    def test_list_assignable_requires_auth(self, client, app):
        """GET /contacts/assignable nécessite une authentification."""
        with app.app_context():
            response = client.get('/v1/contacts/assignable')
            
            assert response.status_code == 401

    # === GET /contacts/<id> - Récupérer un contact spécifique ===

    @pytest.mark.integration
    def test_get_contact_success(self, client, app):
        """Récupérer un contact par son ID."""
        token, user1_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            # Créer un autre utilisateur et l'ajouter comme contact
            user2 = User(username='user2', email='user2@test.com', password_hash='hash')
            db.session.add(user2)
            db.session.commit()
            
            # Ajouter le contact
            contact = Contact(
                user_id=user1_id,
                contact_user_id=user2.id,
                nickname='Mon Contact'
            )
            db.session.add(contact)
            db.session.commit()
            contact_id = contact.id
            
            # Récupérer le contact
            response = client.get(f'/v1/contacts/{contact_id}')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['id'] == contact_id
            assert data['nickname'] == 'Mon Contact'
            assert data['contact_user_id'] == user2.id

    @pytest.mark.integration
    def test_get_contact_not_found(self, client, app):
        """Récupérer un contact inexistant retourne 404."""
        with app.app_context():
            response = client.get('/v1/contacts/99999')
            
            assert response.status_code == 404

    # === PUT /contacts/<id> - Modifier un contact ===

    @pytest.mark.integration
    def test_update_contact_success(self, client, app):
        """Modifier un contact existant."""
        token, user1_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            user2 = User(username='user2', email='user2@test.com', password_hash='hash')
            db.session.add(user2)
            db.session.commit()
            
            contact = Contact(
                user_id=user1_id,
                contact_user_id=user2.id,
                nickname='Old Nickname'
            )
            db.session.add(contact)
            db.session.commit()
            contact_id = contact.id
            
            # Modifier le contact
            response = client.put(f'/v1/contacts/{contact_id}', json={
                'nickname': 'New Nickname',
                'contact_action': 'work'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['nickname'] == 'New Nickname'
            assert data['contact_action'] == 'work'

    @pytest.mark.integration
    def test_update_contact_not_found(self, client, app):
        """Modifier un contact inexistant retourne 404."""
        with app.app_context():
            response = client.put('/v1/contacts/99999', json={
                'nickname': 'Test'
            })
            
            assert response.status_code == 404

    # === DELETE /contacts/<id> - Supprimer un contact ===

    @pytest.mark.integration
    def test_delete_contact_success(self, client, app):
        """Supprimer un contact existant."""
        token, user1_id = create_user_and_login(client, app, 'user1', 'user1@test.com', 'pass')
        
        with app.app_context():
            user2 = User(username='user2', email='user2@test.com', password_hash='hash')
            db.session.add(user2)
            db.session.commit()
            
            contact = Contact(
                user_id=user1_id,
                contact_user_id=user2.id,
                nickname='To Delete'
            )
            db.session.add(contact)
            db.session.commit()
            contact_id = contact.id
            
            # Supprimer le contact
            response = client.delete(f'/v1/contacts/{contact_id}')
            
            assert response.status_code == 200
            
            # Vérifier que le contact n'existe plus
            deleted_contact = Contact.query.get(contact_id)
            assert deleted_contact is None

    @pytest.mark.integration
    def test_delete_contact_not_found(self, client, app):
        """Supprimer un contact inexistant retourne 404."""
        with app.app_context():
            response = client.delete('/v1/contacts/99999')
            
            assert response.status_code == 404
