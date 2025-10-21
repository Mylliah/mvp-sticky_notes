"""
Tests End-to-End (E2E) - Scénarios utilisateur complets.

Ces tests simulent des scénarios utilisateur réels du début à la fin.
"""
import pytest


class TestNoteCollaborationWorkflows:
    """Scénarios de collaboration autour des notes."""

    @pytest.mark.e2e
    def test_complete_note_collaboration_workflow(self, client, app):
        """
        Scénario complet : Collaboration entre 2 utilisateurs sur une note.
        
        Workflow:
        1. Alice s'inscrit et se connecte
        2. Bob s'inscrit
        3. Alice ajoute Bob comme contact
        4. Alice crée une note importante
        5. Alice assigne la note à Bob
        6. Bob se connecte
        7. Bob consulte ses notes assignées
        8. Bob marque la note comme lue
        9. Alice vérifie que Bob a lu
        10. Vérifier les action_logs créés
        """
        with app.app_context():
            # === Phase 1: Inscription et authentification ===
            
            # 1. Alice s'inscrit
            response = client.post('/v1/auth/register', json={
                'username': 'alice',
                'email': 'alice@example.com',
                'password': 'SecurePass123!'
            })
            assert response.status_code == 201
            alice_id = response.get_json()['id']
            
            # Alice se connecte
            response = client.post('/v1/auth/login', json={
                'email': 'alice@example.com',
                'password': 'SecurePass123!'
            })
            assert response.status_code == 200
            token_alice = response.get_json()['access_token']
            
            # 2. Bob s'inscrit
            response = client.post('/v1/auth/register', json={
                'username': 'bob',
                'email': 'bob@example.com',
                'password': 'BobPass456!'
            })
            assert response.status_code == 201
            bob_id = response.get_json()['id']
            
            # === Phase 2: Gestion des contacts ===
            
            # 3. Alice ajoute Bob comme contact
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_alice}'},
                json={
                    'contact_username': 'bob',
                    'nickname': 'Bob le Dev'
                }
            )
            assert response.status_code == 201
            
            # Bob se connecte et ajoute Alice (réciprocité requise)
            response = client.post('/v1/auth/login', json={
                'email': 'bob@example.com',
                'password': 'BobPass456!'
            })
            assert response.status_code == 200
            token_bob_temp = response.get_json()['access_token']
            
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_bob_temp}'},
                json={
                    'contact_username': 'alice',
                    'nickname': 'Alice la PM'
                }
            )
            assert response.status_code == 201
            
            # Vérifier que Bob apparaît dans les contacts d'Alice
            response = client.get('/v1/contacts',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            contacts = response.get_json()
            # Alice voit elle-même + Bob
            assert len(contacts) == 2
            bob_contact = [c for c in contacts if not c.get('is_self')][0]
            assert bob_contact['nickname'] == 'Bob le Dev'
            assert bob_contact['is_mutual'] is True  # Maintenant mutuel
            
            # === Phase 3: Création et assignation de note ===
            
            # 4. Alice crée une note importante
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token_alice}'},
                json={
                    'content': 'Réunion urgente demain à 10h - Présentation du projet MVP',
                    'important': True
                }
            )
            assert response.status_code == 201
            note = response.get_json()
            note_id = note['id']
            assert note['important'] is True
            assert note['creator_id'] == alice_id
            
            # 5. Alice assigne la note à Bob
            response = client.post('/v1/assignments',
                headers={'Authorization': f'Bearer {token_alice}'},
                json={
                    'note_id': note_id,
                    'user_id': bob_id,
                    'is_read': False
                }
            )
            assert response.status_code == 201
            assignment = response.get_json()
            assignment_id = assignment['id']
            assert assignment['is_read'] is False
            
            # === Phase 4: Bob consulte et interagit ===
            
            # 6. Bob se connecte
            response = client.post('/v1/auth/login', json={
                'email': 'bob@example.com',
                'password': 'BobPass456!'
            })
            assert response.status_code == 200
            token_bob = response.get_json()['access_token']
            
            # 7. Bob consulte la liste de ses notes (summary)
            response = client.get('/v1/notes',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            assert response.status_code == 200
            notes_summary = response.get_json()
            # Bob devrait voir la note qui lui est assignée
            assert len(notes_summary) >= 1
            
            # Bob récupère les détails de la note
            response = client.get(f'/v1/notes/{note_id}/details',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            assert response.status_code == 200
            note_details = response.get_json()
            assert note_details['assigned_to'] == bob_id
            
            # 8. Bob marque la note comme lue
            response = client.put(f'/v1/assignments/{assignment_id}',
                headers={'Authorization': f'Bearer {token_bob}'},
                json={'is_read': True}
            )
            assert response.status_code == 200
            updated_assignment = response.get_json()
            assert updated_assignment['is_read'] is True
            
            # === Phase 5: Vérifications finales ===
            
            # 9. Alice vérifie que l'assignation a été mise à jour
            response = client.get(f'/v1/assignments/{assignment_id}',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            assert response.status_code == 200
            assignment_check = response.get_json()
            assert assignment_check['is_read'] is True
            
            # NOTE: Vérification des action_logs supprimée car ces routes sont
            # maintenant réservées aux admins uniquement (@admin_required)

    @pytest.mark.e2e
    def test_note_lifecycle_complete(self, client, app):
        """
        Scénario : Cycle de vie complet d'une note.
        
        Workflow:
        1. User crée une note
        2. User modifie la note plusieurs fois
        3. User marque comme important
        4. User change le statut à "fait"
        5. User supprime la note (soft delete)
        """
        with app.app_context():
            # Setup: Créer et connecter utilisateur
            response = client.post('/v1/auth/register', json={
                'username': 'charlie',
                'email': 'charlie@example.com',
                'password': 'CharliePass!'
            })
            user_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'charlie@example.com',
                'password': 'CharliePass!'
            })
            token = response.get_json()['access_token']
            
            # 1. Créer une note
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token}'},
                json={'content': 'Acheter du lait'}
            )
            assert response.status_code == 201
            note_id = response.get_json()['id']
            
            # 2. Modifier le contenu
            response = client.put(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'content': 'Acheter du lait bio'
                }
            )
            assert response.status_code == 200
            
            # 3. Marquer comme important
            response = client.put(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'content': 'Acheter du lait bio',
                    'important': True
                }
            )
            assert response.status_code == 200
            assert response.get_json()['important'] is True
            
            # 4. Modifier encore le contenu
            response = client.put(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'content': 'Acheter du lait bio et des oeufs'
                }
            )
            assert response.status_code == 200
            
            # 5. Supprimer la note (soft delete)
            response = client.delete(f'/v1/notes/{note_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert response.status_code == 200
            assert response.get_json()['delete_date'] is not None

    @pytest.mark.e2e
    def test_multiple_assignments_workflow(self, client, app):
        """
        Scénario : Une note assignée à plusieurs utilisateurs.
        
        Workflow:
        1. Manager crée une note
        2. Manager ajoute 3 membres d'équipe comme contacts
        3. Manager assigne la note aux 3 membres
        4. Chaque membre marque comme lu indépendamment
        5. Vérifier que chaque assignation est indépendante
        """
        with app.app_context():
            # Setup Manager
            response = client.post('/v1/auth/register', json={
                'username': 'manager',
                'email': 'manager@example.com',
                'password': 'ManagerPass!'
            })
            manager_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'manager@example.com',
                'password': 'ManagerPass!'
            })
            token_manager = response.get_json()['access_token']
            
            # Créer 3 membres d'équipe
            team_members = []
            team_tokens = []
            for i in range(1, 4):
                response = client.post('/v1/auth/register', json={
                    'username': f'member{i}',
                    'email': f'member{i}@example.com',
                    'password': f'Member{i}Pass!'
                })
                member_id = response.get_json()['id']
                team_members.append(member_id)
                
                # Login du membre
                response = client.post('/v1/auth/login', json={
                    'email': f'member{i}@example.com',
                    'password': f'Member{i}Pass!'
                })
                member_token = response.get_json()['access_token']
                team_tokens.append(member_token)
                
                # Manager ajoute chaque membre comme contact
                client.post('/v1/contacts',
                    headers={'Authorization': f'Bearer {token_manager}'},
                    json={
                        'contact_username': f'member{i}',
                        'nickname': f'Member {i}'
                    }
                )
                
                # Chaque membre ajoute le manager (réciprocité)
                client.post('/v1/contacts',
                    headers={'Authorization': f'Bearer {member_token}'},
                    json={
                        'contact_username': 'manager',
                        'nickname': 'Le Manager'
                    }
                )
            
            # Manager crée une note
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token_manager}'},
                json={'content': 'Réunion d\'équipe vendredi 14h'}
            )
            note_id = response.get_json()['id']
            
            # Manager assigne à tous les membres
            assignments = []
            for member_id in team_members:
                response = client.post('/v1/assignments',
                    headers={'Authorization': f'Bearer {token_manager}'},
                    json={
                        'note_id': note_id,
                        'user_id': member_id
                    }
                )
                assert response.status_code == 201
                assignments.append(response.get_json())
            
            # Vérifier qu'il y a bien 3 assignations
            assert len(assignments) == 3
            
            # Member 1 se connecte et marque comme lu
            response = client.post('/v1/auth/login', json={
                'email': 'member1@example.com',
                'password': 'Member1Pass!'
            })
            token_member1 = response.get_json()['access_token']
            
            response = client.put(f'/v1/assignments/{assignments[0]["id"]}',
                headers={'Authorization': f'Bearer {token_member1}'},
                json={'is_read': True}
            )
            assert response.status_code == 200
            
            # Vérifier que seule l'assignation de Member 1 est lue
            for i, assignment in enumerate(assignments):
                response = client.get(f'/v1/assignments/{assignment["id"]}',
                    headers={'Authorization': f'Bearer {token_manager}'}
                )
                data = response.get_json()
                if i == 0:
                    assert data['is_read'] is True
                else:
                    assert data['is_read'] is False


class TestUserIsolationWorkflows:
    """Scénarios vérifiant l'isolation entre utilisateurs."""

    @pytest.mark.e2e
    def test_complete_user_isolation(self, client, app):
        """
        Scénario : Vérifier l'isolation complète entre utilisateurs.
        
        Workflow:
        1. User1 crée des notes et contacts
        2. User2 crée des notes et contacts
        3. User1 ne voit que ses données
        4. User2 ne voit que ses données
        5. Aucune fuite de données entre users
        """
        with app.app_context():
            # === Setup User1 ===
            response = client.post('/v1/auth/register', json={
                'username': 'user1',
                'email': 'user1@example.com',
                'password': 'User1Pass!'
            })
            user1_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'user1@example.com',
                'password': 'User1Pass!'
            })
            token_user1 = response.get_json()['access_token']
            
            # === Setup User2 ===
            response = client.post('/v1/auth/register', json={
                'username': 'user2',
                'email': 'user2@example.com',
                'password': 'User2Pass!'
            })
            user2_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'user2@example.com',
                'password': 'User2Pass!'
            })
            token_user2 = response.get_json()['access_token']
            
            # === User1 crée ses données ===
            
            # User1 crée 2 notes
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token_user1}'},
                json={'content': 'Note privée User1 - 1'}
            )
            assert response.status_code == 201
            user1_note1_id = response.get_json()['id']
            
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token_user1}'},
                json={'content': 'Note privée User1 - 2'}
            )
            assert response.status_code == 201
            
            # === User2 crée ses données ===
            
            # User2 crée 3 notes
            for i in range(3):
                response = client.post('/v1/notes',
                    headers={'Authorization': f'Bearer {token_user2}'},
                    json={'content': f'Note privée User2 - {i+1}'}
                )
                assert response.status_code == 201
            
            # === Vérification isolation ===
            
            # User1 ne voit que ses 2 notes
            response = client.get('/v1/notes',
                headers={'Authorization': f'Bearer {token_user1}'}
            )
            user1_data = response.get_json()
            assert len(user1_data['notes']) == 2
            assert all('User1' in note['content'] for note in user1_data['notes'])
            
            # User2 ne voit que ses 3 notes
            response = client.get('/v1/notes',
                headers={'Authorization': f'Bearer {token_user2}'}
            )
            user2_data = response.get_json()
            assert len(user2_data['notes']) == 3
            assert all('User2' in note['content'] for note in user2_data['notes'])
            
            # User1 voit uniquement lui-même dans ses contacts (pas encore d'ajout)
            response = client.get('/v1/contacts',
                headers={'Authorization': f'Bearer {token_user1}'}
            )
            user1_contacts = response.get_json()
            assert len(user1_contacts) == 1  # Seulement lui-même
            assert user1_contacts[0]['is_self'] is True

    @pytest.mark.e2e
    def test_contact_isolation_workflow(self, client, app):
        """
        Scénario : Les contacts d'un utilisateur sont privés.
        
        Workflow:
        1. Alice ajoute Bob et Charlie comme contacts
        2. Dave ajoute Eve comme contact
        3. Alice ne voit que ses contacts (Bob, Charlie + elle-même)
        4. Dave ne voit que ses contacts (Eve + lui-même)
        """
        with app.app_context():
            # Créer 5 utilisateurs
            users = {}
            for name in ['alice', 'bob', 'charlie', 'dave', 'eve']:
                response = client.post('/v1/auth/register', json={
                    'username': name,
                    'email': f'{name}@example.com',
                    'password': f'{name.capitalize()}Pass!'
                })
                users[name] = {
                    'id': response.get_json()['id'],
                    'token': None
                }
                
                # Login
                response = client.post('/v1/auth/login', json={
                    'email': f'{name}@example.com',
                    'password': f'{name.capitalize()}Pass!'
                })
                users[name]['token'] = response.get_json()['access_token']
            
            # Alice ajoute Bob et Charlie
            client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {users["alice"]["token"]}'},
                json={'contact_username': 'bob', 'nickname': 'Bob'}
            )
            client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {users["alice"]["token"]}'},
                json={'contact_username': 'charlie', 'nickname': 'Charlie'}
            )
            
            # Dave ajoute Eve
            client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {users["dave"]["token"]}'},
                json={'contact_username': 'eve', 'nickname': 'Eve'}
            )
            
            # Vérifier les contacts d'Alice
            response = client.get('/v1/contacts',
                headers={'Authorization': f'Bearer {users["alice"]["token"]}'}
            )
            alice_contacts = response.get_json()
            assert len(alice_contacts) == 3  # Alice + Bob + Charlie
            
            # Vérifier les contacts de Dave
            response = client.get('/v1/contacts',
                headers={'Authorization': f'Bearer {users["dave"]["token"]}'}
            )
            dave_contacts = response.get_json()
            assert len(dave_contacts) == 2  # Dave + Eve
            
            # Bob ne voit que lui-même (n'a ajouté personne)
            response = client.get('/v1/contacts',
                headers={'Authorization': f'Bearer {users["bob"]["token"]}'}
            )
            bob_contacts = response.get_json()
            assert len(bob_contacts) == 1  # Seulement lui-même


class TestErrorHandlingWorkflows:
    """Scénarios testant la gestion d'erreurs dans des workflows complets."""

    @pytest.mark.e2e
    def test_workflow_with_invalid_operations(self, client, app):
        """
        Scénario : Tester que les opérations invalides sont bien bloquées.
        
        Workflow:
        1. User essaie de s'ajouter lui-même comme contact (doit échouer)
        2. User essaie d'assigner une note inexistante (doit échouer)
        3. User essaie de créer un doublon de contact (doit échouer)
        4. User essaie de créer un doublon d'assignation (doit échouer)
        """
        with app.app_context():
            # Setup
            response = client.post('/v1/auth/register', json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'TestPass!'
            })
            user_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'test@example.com',
                'password': 'TestPass!'
            })
            token = response.get_json()['access_token']
            
            # 1. Essayer de s'ajouter soi-même comme contact
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'testuser', 'nickname': 'Moi'}
            )
            assert response.status_code == 400
            error_msg = response.get_json().get('description', '') or response.get_json().get('message', '')
            assert 'yourself' in error_msg.lower()
            
            # 2. Essayer d'assigner une note inexistante
            response = client.post('/v1/assignments',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'note_id': 99999,
                    'user_id': user_id
                }
            )
            assert response.status_code == 400
            
            # 3. Créer un contact, puis essayer de créer un doublon
            # D'abord créer un autre user
            response = client.post('/v1/auth/register', json={
                'username': 'contact1',
                'email': 'contact1@example.com',
                'password': 'Contact1Pass!'
            })
            contact_id = response.get_json()['id']
            
            # Login contact1
            response = client.post('/v1/auth/login', json={
                'email': 'contact1@example.com',
                'password': 'Contact1Pass!'
            })
            token_contact1 = response.get_json()['access_token']
            
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'contact1', 'nickname': 'Contact'}
            )
            assert response.status_code == 201
            
            # contact1 ajoute testuser (réciprocité)
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_contact1}'},
                json={'contact_username': 'testuser', 'nickname': 'TestUser'}
            )
            assert response.status_code == 201
            
            # Essayer de re-ajouter le même contact
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token}'},
                json={'contact_username': 'contact1', 'nickname': 'Contact Duplicate'}
            )
            assert response.status_code == 400
            error_msg = response.get_json().get('description', '') or response.get_json().get('message', '')
            assert 'already' in error_msg.lower()
            
            # 4. Créer une note et assignation, puis essayer un doublon d'assignation
            response = client.post('/v1/notes',
                headers={'Authorization': f'Bearer {token}'},
                json={'content': 'Test note'}
            )
            note_id = response.get_json()['id']
            
            response = client.post('/v1/assignments',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'note_id': note_id,
                    'user_id': contact_id
                }
            )
            assert response.status_code == 201
            
            # Essayer de re-créer la même assignation
            response = client.post('/v1/assignments',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'note_id': note_id,
                    'user_id': contact_id
                }
            )
            assert response.status_code == 400
            error_msg = response.get_json().get('description', '') or response.get_json().get('message', '')
            assert 'already' in error_msg.lower()


class TestContactNotesWorkflows:
    """Scénarios E2E pour les notes échangées avec un contact."""

    @pytest.mark.e2e
    def test_contact_notes_exchange_workflow(self, client, app):
        """
        Scénario complet : Échange de notes entre deux contacts.
        
        Workflow:
        1. Alice et Bob s'inscrivent
        2. Alice ajoute Bob comme contact
        3. Alice envoie 2 notes à Bob
        4. Bob envoie 3 notes à Alice
        5. Alice consulte toutes les notes échangées avec Bob
        6. Alice filtre pour voir uniquement les notes envoyées
        7. Alice filtre pour voir uniquement les notes reçues
        8. Bob ne peut pas voir les notes d'un contact d'Alice
        """
        with app.app_context():
            # === Phase 1: Setup utilisateurs ===
            
            # Alice s'inscrit et se connecte
            response = client.post('/v1/auth/register', json={
                'username': 'alice_exchange',
                'email': 'alice_exchange@example.com',
                'password': 'AlicePass123!'
            })
            assert response.status_code == 201
            alice_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'alice_exchange@example.com',
                'password': 'AlicePass123!'
            })
            token_alice = response.get_json()['access_token']
            
            # Bob s'inscrit et se connecte
            response = client.post('/v1/auth/register', json={
                'username': 'bob_exchange',
                'email': 'bob_exchange@example.com',
                'password': 'BobPass456!'
            })
            assert response.status_code == 201
            bob_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'bob_exchange@example.com',
                'password': 'BobPass456!'
            })
            token_bob = response.get_json()['access_token']
            
            # === Phase 2: Alice ajoute Bob comme contact ===
            
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_alice}'},
                json={
                    'contact_username': 'bob_exchange',
                    'nickname': 'Bob'
                }
            )
            assert response.status_code == 201
            contact_id = response.get_json()['id']
            
            # Bob ajoute Alice comme contact (réciprocité nécessaire pour les assignations)
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_bob}'},
                json={
                    'contact_username': 'alice_exchange',
                    'nickname': 'Alice'
                }
            )
            assert response.status_code == 201
            
            # === Phase 3: Alice envoie 2 notes à Bob ===
            
            alice_notes = []
            for i in range(1, 3):
                response = client.post('/v1/notes',
                    headers={'Authorization': f'Bearer {token_alice}'},
                    json={'content': f'Message d\'Alice à Bob #{i}'}
                )
                assert response.status_code == 201
                note_id = response.get_json()['id']
                alice_notes.append(note_id)
                
                # Assigner à Bob
                response = client.post('/v1/assignments',
                    headers={'Authorization': f'Bearer {token_alice}'},
                    json={'note_id': note_id, 'user_id': bob_id}
                )
                assert response.status_code == 201
            
            # === Phase 4: Bob envoie 3 notes à Alice ===
            
            bob_notes = []
            for i in range(1, 4):
                response = client.post('/v1/notes',
                    headers={'Authorization': f'Bearer {token_bob}'},
                    json={'content': f'Réponse de Bob à Alice #{i}'}
                )
                assert response.status_code == 201
                note_id = response.get_json()['id']
                bob_notes.append(note_id)
                
                # Assigner à Alice
                response = client.post('/v1/assignments',
                    headers={'Authorization': f'Bearer {token_bob}'},
                    json={'note_id': note_id, 'user_id': alice_id}
                )
                assert response.status_code == 201
            
            # === Phase 5: Alice consulte TOUTES les notes avec Bob ===
            
            response = client.get(f'/v1/contacts/{contact_id}/notes',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            assert response.status_code == 200
            data = response.get_json()
            
            # Vérifier la structure de la réponse
            assert 'contact' in data
            assert 'notes' in data
            assert 'total' in data
            assert 'page' in data
            assert 'per_page' in data
            
            # Vérifier les infos du contact
            assert data['contact']['nickname'] == 'Bob'
            assert data['contact']['contact_user_id'] == bob_id
            
            # Vérifier qu'on a bien 5 notes (2 d'Alice + 3 de Bob)
            assert data['total'] == 5
            assert len(data['notes']) == 5
            
            # Vérifier qu'on a les deux types de notes
            note_contents = [n['content'] for n in data['notes']]
            assert any('Alice à Bob' in content for content in note_contents)
            assert any('Bob à Alice' in content for content in note_contents)
            
            # === Phase 6: Filtre "sent" - Alice voit uniquement ses notes envoyées ===
            
            response = client.get(f'/v1/contacts/{contact_id}/notes?filter=sent',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['total'] == 2  # Seulement les 2 notes d'Alice
            assert len(data['notes']) == 2
            
            for note in data['notes']:
                assert note['creator_id'] == alice_id
                assert 'Alice à Bob' in note['content']
            
            # === Phase 7: Filtre "received" - Alice voit uniquement les notes reçues ===
            
            response = client.get(f'/v1/contacts/{contact_id}/notes?filter=received',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['total'] == 3  # Les 3 notes de Bob
            assert len(data['notes']) == 3
            
            for note in data['notes']:
                assert note['creator_id'] == bob_id
                assert 'Bob à Alice' in note['content']
            
            # === Phase 8: Isolation - Bob ne peut pas voir le contact d'Alice ===
            
            response = client.get(f'/v1/contacts/{contact_id}/notes',
                headers={'Authorization': f'Bearer {token_bob}'}
            )
            assert response.status_code == 403  # Forbidden

    @pytest.mark.e2e
    def test_contact_notes_pagination_workflow(self, client, app):
        """
        Scénario : Pagination des notes d'un contact.
        
        Workflow:
        1. Alice et Bob s'inscrivent
        2. Alice ajoute Bob comme contact
        3. Alice envoie 10 notes à Bob
        4. Alice consulte avec pagination (3 par page)
        5. Vérifier la navigation entre les pages
        """
        with app.app_context():
            # Setup
            response = client.post('/v1/auth/register', json={
                'username': 'alice_pagination',
                'email': 'alice_pagination@example.com',
                'password': 'AlicePass!'
            })
            alice_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'alice_pagination@example.com',
                'password': 'AlicePass!'
            })
            token_alice = response.get_json()['access_token']
            
            response = client.post('/v1/auth/register', json={
                'username': 'bob_pagination',
                'email': 'bob_pagination@example.com',
                'password': 'BobPass!'
            })
            bob_id = response.get_json()['id']
            
            # Alice ajoute Bob
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_alice}'},
                json={'contact_username': 'bob_pagination', 'nickname': 'Bob'}
            )
            contact_id = response.get_json()['id']
            
            # Bob ajoute Alice (réciprocité)
            response = client.post('/v1/auth/login', json={
                'email': 'bob_pagination@example.com',
                'password': 'BobPass!'
            })
            token_bob = response.get_json()['access_token']
            
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_bob}'},
                json={'contact_username': 'alice_pagination', 'nickname': 'Alice'}
            )
            assert response.status_code == 201
            
            # Alice crée 10 notes pour Bob
            for i in range(10):
                response = client.post('/v1/notes',
                    headers={'Authorization': f'Bearer {token_alice}'},
                    json={'content': f'Note {i+1}'}
                )
                note_id = response.get_json()['id']
                
                client.post('/v1/assignments',
                    headers={'Authorization': f'Bearer {token_alice}'},
                    json={'note_id': note_id, 'user_id': bob_id}
                )
            
            # Page 1 : 3 notes par page
            response = client.get(f'/v1/contacts/{contact_id}/notes?per_page=3&page=1',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['total'] == 10
            assert len(data['notes']) == 3
            assert data['page'] == 1
            assert data['per_page'] == 3
            assert data['pages'] == 4  # 10 notes / 3 per page = 4 pages
            assert data['has_next'] is True
            assert data['has_prev'] is False
            
            # Page 2
            response = client.get(f'/v1/contacts/{contact_id}/notes?per_page=3&page=2',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            data = response.get_json()
            
            assert len(data['notes']) == 3
            assert data['page'] == 2
            assert data['has_next'] is True
            assert data['has_prev'] is True
            
            # Dernière page (page 4)
            response = client.get(f'/v1/contacts/{contact_id}/notes?per_page=3&page=4',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            data = response.get_json()
            
            assert len(data['notes']) == 1  # Seulement 1 note sur la dernière page
            assert data['page'] == 4
            assert data['has_next'] is False
            assert data['has_prev'] is True

    @pytest.mark.e2e
    def test_contact_notes_unread_filter_workflow(self, client, app):
        """
        Scénario : Filtrer les notes non lues d'un contact.
        
        Workflow:
        1. Bob envoie 5 notes à Alice
        2. Alice marque 2 notes comme lues
        3. Alice filtre pour voir uniquement les non lues (doit voir 3)
        """
        with app.app_context():
            # Setup
            response = client.post('/v1/auth/register', json={
                'username': 'alice_unread',
                'email': 'alice_unread@example.com',
                'password': 'AlicePass!'
            })
            alice_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'alice_unread@example.com',
                'password': 'AlicePass!'
            })
            token_alice = response.get_json()['access_token']
            
            response = client.post('/v1/auth/register', json={
                'username': 'bob_unread',
                'email': 'bob_unread@example.com',
                'password': 'BobPass!'
            })
            bob_id = response.get_json()['id']
            
            response = client.post('/v1/auth/login', json={
                'email': 'bob_unread@example.com',
                'password': 'BobPass!'
            })
            token_bob = response.get_json()['access_token']
            
            # Alice ajoute Bob
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_alice}'},
                json={'contact_username': 'bob_unread', 'nickname': 'Bob'}
            )
            contact_id = response.get_json()['id']
            
            # Bob ajoute Alice (réciprocité)
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_bob}'},
                json={'contact_username': 'alice_unread', 'nickname': 'Alice'}
            )
            assert response.status_code == 201
            
            # Bob crée 5 notes pour Alice
            assignments = []
            for i in range(5):
                response = client.post('/v1/notes',
                    headers={'Authorization': f'Bearer {token_bob}'},
                    json={'content': f'Note {i+1} from Bob'}
                )
                note_id = response.get_json()['id']
                
                response = client.post('/v1/assignments',
                    headers={'Authorization': f'Bearer {token_bob}'},
                    json={'note_id': note_id, 'user_id': alice_id}
                )
                assignments.append(response.get_json())
            
            # Alice marque 2 notes comme lues
            for i in range(2):
                client.put(f'/v1/assignments/{assignments[i]["id"]}',
                    headers={'Authorization': f'Bearer {token_alice}'},
                    json={'is_read': True}
                )
            
            # Alice filtre pour voir uniquement les notes non lues de Bob
            response = client.get(f'/v1/contacts/{contact_id}/notes?filter=unread',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            assert response.status_code == 200
            data = response.get_json()
            
            # Doit avoir 3 notes non lues
            assert data['total'] == 3
            assert len(data['notes']) == 3
            
            # Vérifier que ce sont bien les bonnes notes
            for note in data['notes']:
                assert note['creator_id'] == bob_id

    @pytest.mark.e2e
    def test_contact_notes_empty_exchange_workflow(self, client, app):
        """
        Scénario : Contact sans échange de notes.
        
        Workflow:
        1. Alice ajoute Bob comme contact
        2. Aucune note n'est échangée
        3. La liste doit être vide
        """
        with app.app_context():
            # Setup
            response = client.post('/v1/auth/register', json={
                'username': 'alice_empty',
                'email': 'alice_empty@example.com',
                'password': 'AlicePass!'
            })
            
            response = client.post('/v1/auth/login', json={
                'email': 'alice_empty@example.com',
                'password': 'AlicePass!'
            })
            token_alice = response.get_json()['access_token']
            
            response = client.post('/v1/auth/register', json={
                'username': 'bob_empty',
                'email': 'bob_empty@example.com',
                'password': 'BobPass!'
            })
            
            # Alice ajoute Bob
            response = client.post('/v1/contacts',
                headers={'Authorization': f'Bearer {token_alice}'},
                json={'contact_username': 'bob_empty', 'nickname': 'Bob'}
            )
            contact_id = response.get_json()['id']
            
            # Consulter les notes (doit être vide)
            response = client.get(f'/v1/contacts/{contact_id}/notes',
                headers={'Authorization': f'Bearer {token_alice}'}
            )
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['total'] == 0
            assert len(data['notes']) == 0
            assert data['contact']['nickname'] == 'Bob'

