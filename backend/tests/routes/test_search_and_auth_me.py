"""
Tests pour les fonctionnalités MUST HAVE :
- Recherche textuelle dans les notes (GET /notes?q=)
- Endpoint GET /auth/me
"""
import pytest
from app.models import User, Note, Assignment


class TestSearchNotes:
    """Tests pour la recherche textuelle dans les notes"""
    
    def test_search_notes_by_content(self, client, auth_headers):
        """Test recherche de notes par contenu"""
        # Créer plusieurs notes avec différents contenus
        response1 = client.post('/v1/notes', 
                                json={"content": "Acheter du lait et du pain"},
                                headers=auth_headers)
        assert response1.status_code == 201
        
        response2 = client.post('/v1/notes',
                                json={"content": "Réunion avec le client demain"},
                                headers=auth_headers)
        assert response2.status_code == 201
        
        response3 = client.post('/v1/notes',
                                json={"content": "Appeler le médecin pour rendez-vous"},
                                headers=auth_headers)
        assert response3.status_code == 201
        
        # Rechercher "lait" - devrait trouver seulement la première note
        response = client.get('/v1/notes?q=lait', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert 'lait' in data['notes'][0]['content'].lower()
    
    def test_search_notes_case_insensitive(self, client, auth_headers):
        """Test que la recherche est insensible à la casse"""
        # Créer une note
        response = client.post('/v1/notes',
                               json={"content": "URGENT: Finir le RAPPORT"},
                               headers=auth_headers)
        assert response.status_code == 201
        
        # Rechercher en minuscules
        response = client.get('/v1/notes?q=urgent', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert 'URGENT' in data['notes'][0]['content']
        
        # Rechercher en majuscules
        response = client.get('/v1/notes?q=RAPPORT', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
    
    def test_search_notes_partial_match(self, client, auth_headers):
        """Test recherche avec correspondance partielle"""
        # Créer une note
        response = client.post('/v1/notes',
                               json={"content": "Développement de l'application"},
                               headers=auth_headers)
        assert response.status_code == 201
        
        # Rechercher avec un mot partiel
        response = client.get('/v1/notes?q=développ', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
    
    def test_search_notes_no_results(self, client, auth_headers):
        """Test recherche sans résultats"""
        # Créer une note
        response = client.post('/v1/notes',
                               json={"content": "Note de test"},
                               headers=auth_headers)
        assert response.status_code == 201
        
        # Rechercher quelque chose qui n'existe pas
        response = client.get('/v1/notes?q=inexistant123', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 0
        assert len(data['notes']) == 0
    
    def test_search_notes_empty_query(self, client, auth_headers):
        """Test recherche avec query vide retourne toutes les notes"""
        # Créer deux notes
        client.post('/v1/notes', json={"content": "Note 1"}, headers=auth_headers)
        client.post('/v1/notes', json={"content": "Note 2"}, headers=auth_headers)
        
        # Recherche avec query vide
        response = client.get('/v1/notes?q=', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
    
    def test_search_notes_with_spaces(self, client, auth_headers):
        """Test recherche avec des espaces (recherche un seul mot)"""
        # Créer une note
        response = client.post('/v1/notes',
                               json={"content": "Acheter du pain et du lait"},
                               headers=auth_headers)
        assert response.status_code == 201
        
        # Rechercher avec un seul mot de la phrase
        response = client.get('/v1/notes?q=pain', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1
    
    def test_search_combined_with_filters(self, client, auth_headers):
        """Test recherche combinée avec filtres"""
        # Créer des notes
        response1 = client.post('/v1/notes',
                                json={"content": "Tâche urgente à faire", "important": True},
                                headers=auth_headers)
        assert response1.status_code == 201
        
        response2 = client.post('/v1/notes',
                                json={"content": "Tâche normale à faire", "important": False},
                                headers=auth_headers)
        assert response2.status_code == 201
        
        # Rechercher "tâche" avec filtre important
        response = client.get('/v1/notes?q=tâche&filter=important', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert data['notes'][0]['important'] is True
    
    def test_search_combined_with_sorting(self, client, auth_headers):
        """Test recherche combinée avec tri"""
        # Créer des notes
        client.post('/v1/notes', json={"content": "Note A"}, headers=auth_headers)
        client.post('/v1/notes', json={"content": "Note B"}, headers=auth_headers)
        
        # Rechercher avec tri ascendant
        response = client.get('/v1/notes?q=Note&sort=date_asc', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
        # Vérifier que le tri est appliqué
        assert data['notes'][0]['content'] == "Note A"
    
    def test_search_with_pagination(self, client, auth_headers):
        """Test recherche avec pagination"""
        # Créer plusieurs notes contenant "test"
        for i in range(5):
            client.post('/v1/notes',
                       json={"content": f"Test note numéro {i}"},
                       headers=auth_headers)
        
        # Rechercher avec pagination
        response = client.get('/v1/notes?q=test&per_page=2&page=1', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 5
        assert len(data['notes']) == 2
        assert data['page'] == 1
        assert data['pages'] == 3


class TestAuthMe:
    """Tests pour l'endpoint GET /auth/me"""
    
    def test_get_me_success(self, client, test_user):
        """Test récupération du profil utilisateur avec token valide"""
        auth_headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.get('/v1/auth/me', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'id' in data
        assert 'username' in data
        assert 'email' in data
        assert 'created_date' in data
        
        # test_user est un dict
        assert data['username'] == test_user['username']
        assert data['email'] == test_user['email']
        assert data['id'] == test_user['id']
    
    def test_get_me_without_token(self, client):
        """Test accès sans token retourne 401"""
        response = client.get('/v1/auth/me')
        assert response.status_code == 401
    
    def test_get_me_with_invalid_token(self, client):
        """Test accès avec token invalide retourne 401 ou 422"""
        headers = {'Authorization': 'Bearer invalid_token_here'}
        response = client.get('/v1/auth/me', headers=headers)
        # JWT invalide peut retourner 401 ou 422 selon l'implémentation
        assert response.status_code in [401, 422]
    
    def test_get_me_returns_correct_user(self, client, app):
        """Test que /auth/me retourne le bon utilisateur"""
        from werkzeug.security import generate_password_hash
        from flask_jwt_extended import create_access_token
        
        # Créer deux utilisateurs
        with app.app_context():
            from app.models import User
            from app import db
            
            user1 = User(
                username="user1",
                email="user1@test.com",
                password_hash=generate_password_hash("password123")
            )
            user2 = User(
                username="user2",
                email="user2@test.com",
                password_hash=generate_password_hash("password123")
            )
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            # Créer token pour user1
            token1 = create_access_token(identity=str(user1.id))
            user1_id = user1.id
            
            # Créer token pour user2
            token2 = create_access_token(identity=str(user2.id))
            user2_id = user2.id
        
        # Tester avec token de user1
        headers1 = {'Authorization': f'Bearer {token1}'}
        response1 = client.get('/v1/auth/me', headers=headers1)
        assert response1.status_code == 200
        data1 = response1.get_json()
        assert data1['id'] == user1_id
        assert data1['username'] == "user1"
        
        # Tester avec token de user2
        headers2 = {'Authorization': f'Bearer {token2}'}
        response2 = client.get('/v1/auth/me', headers=headers2)
        assert response2.status_code == 200
        data2 = response2.get_json()
        assert data2['id'] == user2_id
        assert data2['username'] == "user2"
    
    def test_get_me_validates_token(self, client, auth_headers):
        """Test que /auth/me peut être utilisé pour valider un token"""
        # Token valide devrait retourner 200
        response = client.get('/v1/auth/me', headers=auth_headers)
        assert response.status_code == 200
        
        # Token invalide devrait retourner erreur
        bad_headers = {'Authorization': 'Bearer bad_token'}
        response = client.get('/v1/auth/me', headers=bad_headers)
        assert response.status_code in [401, 422]
    
    def test_get_me_structure(self, client, auth_headers):
        """Test la structure de la réponse de /auth/me"""
        response = client.get('/v1/auth/me', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        
        # Vérifier les champs obligatoires
        required_fields = ['id', 'username', 'email', 'created_date']
        for field in required_fields:
            assert field in data, f"Field '{field}' manquant dans la réponse"
        
        # Vérifier les types
        assert isinstance(data['id'], int)
        assert isinstance(data['username'], str)
        assert isinstance(data['email'], str)
        assert isinstance(data['created_date'], str)
        
        # Vérifier que le mot de passe n'est PAS retourné
        assert 'password' not in data
        assert 'password_hash' not in data


class TestSearchAndAuthIntegration:
    """Tests d'intégration entre recherche et authentification"""
    
    def test_search_only_returns_user_notes(self, client, app):
        """Test que la recherche ne retourne que les notes de l'utilisateur connecté"""
        from werkzeug.security import generate_password_hash
        from flask_jwt_extended import create_access_token
        
        with app.app_context():
            from app.models import User, Note
            from app import db
            
            # Créer deux utilisateurs
            user1 = User(
                username="user1",
                email="user1@test.com",
                password_hash=generate_password_hash("password123")
            )
            user2 = User(
                username="user2",
                email="user2@test.com",
                password_hash=generate_password_hash("password123")
            )
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            # Créer des notes pour chaque utilisateur
            note1 = Note(content="Note secrète de user1", creator_id=user1.id)
            note2 = Note(content="Note secrète de user2", creator_id=user2.id)
            db.session.add(note1)
            db.session.add(note2)
            db.session.commit()
            
            # Créer token pour user1
            token1 = create_access_token(identity=str(user1.id))
        
        # User1 recherche "secrète"
        headers1 = {'Authorization': f'Bearer {token1}'}
        response = client.get('/v1/notes?q=secrète', headers=headers1)
        assert response.status_code == 200
        
        data = response.get_json()
        # User1 ne devrait voir que sa propre note
        assert data['total'] == 1
        assert data['notes'][0]['content'] == "Note secrète de user1"
    
    def test_search_requires_authentication(self, client):
        """Test que la recherche nécessite une authentification"""
        response = client.get('/v1/notes?q=test')
        assert response.status_code == 401
