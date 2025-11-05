# 📋 Commandes curl pour tester l'API Sticky Notes

## Variables d'environnement
```bash
export BASE_URL="http://localhost:5000/v1"
export TOKEN="votre_token_ici"
```

## 🔐 1. AUTHENTIFICATION

### 1.1 Register (inscription)
```bash
curl -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser1",
    "email": "testuser1@test.com",
    "password": "SecurePass123!"
  }'
```

### 1.2 Login (connexion)
```bash
curl -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser1@test.com",
    "password": "SecurePass123!"
  }'
```

**Sauvegarder le token:**
```bash
export TOKEN="eyJhbGc..."
```

---

## 📝 2. NOTES

### 2.1 Créer une note
```bash
curl -X POST $BASE_URL/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Ma première note",
    "important": true
  }'
```

### 2.2 Lister les notes (pagination)
```bash
curl -X GET "$BASE_URL/notes?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 2.3 Filtrer notes importantes
```bash
curl -X GET "$BASE_URL/notes?filter=important" \
  -H "Authorization: Bearer $TOKEN"
```

### 2.4 Trier par date croissante
```bash
curl -X GET "$BASE_URL/notes?sort=date_asc" \
  -H "Authorization: Bearer $TOKEN"
```

### 2.5 Détails d'une note
```bash
curl -X GET "$BASE_URL/notes/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 2.6 Modifier une note
```bash
curl -X PUT "$BASE_URL/notes/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Note modifiée",
    "important": false
  }'
```

### 2.7 Supprimer une note (soft delete)
```bash
curl -X DELETE "$BASE_URL/notes/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 2.8 Détails complets d'une note
```bash
curl -X GET "$BASE_URL/notes/1/details" \
  -H "Authorization: Bearer $TOKEN"
```

### 2.9 Liste des assignations d'une note (créateur)
```bash
curl -X GET "$BASE_URL/notes/1/assignments" \
  -H "Authorization: Bearer $TOKEN"
```

### 2.10 Filtres supplémentaires

**Notes avec priorité destinataire:**
```bash
curl -X GET "$BASE_URL/notes?filter=important_by_me" \
  -H "Authorization: Bearer $TOKEN"
```

**Notes non lues:**
```bash
curl -X GET "$BASE_URL/notes?filter=unread" \
  -H "Authorization: Bearer $TOKEN"
```

**Notes reçues (assignées à moi):**
```bash
curl -X GET "$BASE_URL/notes?filter=received" \
  -H "Authorization: Bearer $TOKEN"
```

**Notes envoyées (créées et assignées):**
```bash
curl -X GET "$BASE_URL/notes?filter=sent" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 👥 3. CONTACTS

### 3.1 Liste des utilisateurs
```bash
curl -X GET "$BASE_URL/users" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.2 Ajouter un contact
```bash
curl -X POST $BASE_URL/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_username": "bob_test",
    "nickname": "Mon collègue"
  }'
```

### 3.3 Liste des contacts
```bash
curl -X GET "$BASE_URL/contacts" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.4 Modifier le nickname d'un contact
```bash
curl -X PUT "$BASE_URL/contacts/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Nouveau surnom"
  }'
```

### 3.5 Supprimer un contact
```bash
curl -X DELETE "$BASE_URL/contacts/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.6 Détails d'un contact
```bash
curl -X GET "$BASE_URL/contacts/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.7 Utilisateurs assignables
```bash
curl -X GET "$BASE_URL/contacts/assignable" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.8 Notes échangées avec un contact
```bash
# Toutes les notes échangées avec le contact
curl -X GET "$BASE_URL/contacts/5/notes" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.9 Filtrer les notes par contact

**Notes envoyées à ce contact:**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?filter=sent" \
  -H "Authorization: Bearer $TOKEN"
```

**Notes reçues de ce contact:**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?filter=received" \
  -H "Authorization: Bearer $TOKEN"
```

**Notes non lues de ce contact:**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?filter=unread" \
  -H "Authorization: Bearer $TOKEN"
```

**Notes importantes:**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?filter=important" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.10 Tri et pagination des notes par contact

**Par date décroissante (défaut):**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?sort=date_desc" \
  -H "Authorization: Bearer $TOKEN"
```

**Par date croissante:**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?sort=date_asc" \
  -H "Authorization: Bearer $TOKEN"
```

**Notes importantes en premier:**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?sort=important_first" \
  -H "Authorization: Bearer $TOKEN"
```

**Avec pagination:**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Combinaison filtres + tri + pagination:**
```bash
curl -X GET "$BASE_URL/contacts/5/notes?filter=unread&sort=date_asc&page=1&per_page=5" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📌 4. ASSIGNMENTS

### 4.1 Créer une assignation
```bash
curl -X POST $BASE_URL/assignments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "note_id": 1,
    "user_id": 5
  }'
```

### 4.4 Lister les assignations
```bash
curl -X GET "$BASE_URL/assignments?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 4.5 Modifier une assignation
```bash
curl -X PUT "$BASE_URL/assignments/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "note_id": 2,
    "assigned_to_id": 3
  }'
```

### 4.6 Supprimer une assignation
```bash
curl -X DELETE "$BASE_URL/assignments/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 4.7 Changer le statut d'avancement
```bash
# Marquer comme terminé
curl -X PUT "$BASE_URL/assignments/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_status": "terminé"
  }'

# Remettre en cours
curl -X PUT "$BASE_URL/assignments/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_status": "en_cours"
  }'
```

### 4.8 Assignations non lues
```bash
curl -X GET "$BASE_URL/assignments/unread" \
  -H "Authorization: Bearer $TOKEN"
```

### 4.10 Toggle priorité personnelle
```bash
# Bascule automatiquement entre true/false
curl -X PUT "$BASE_URL/assignments/1/priority" \
  -H "Authorization: Bearer $TOKEN"
```

### 4.9 Filtres avancés
```bash
curl -X GET "$BASE_URL/assignments?status=unread&note_id=5" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📋 5. ACTION LOGS

### 5.3 Liste des action logs (pagination)
```bash
curl -X GET "$BASE_URL/action_logs?page=1&per_page=20" \
  -H "Authorization: Bearer $TOKEN"
```

### 5.4 Détails d'un log spécifique
```bash
curl -X GET "$BASE_URL/action_logs/123" \
  -H "Authorization: Bearer $TOKEN"
```

### 5.5 Statistiques des logs
```bash
curl -X GET "$BASE_URL/action_logs/stats" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 👤 6. UTILISATEURS

### 6.1 Créer un utilisateur
```bash
curl -X POST $BASE_URL/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepass123"
  }'
```

### 6.2 Détails d'un utilisateur
```bash
curl -X GET "$BASE_URL/users/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 6.3 Profil utilisateur connecté
```bash
curl -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

### 6.4 Modifier un profil
```bash
curl -X PUT "$BASE_URL/users/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newusername",
    "email": "newemail@example.com"
  }'
```

### 6.5 Supprimer un utilisateur
```bash
curl -X DELETE "$BASE_URL/users/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🛡️ 7. ADMIN (nécessite token admin)

### 7.1 Utilisateurs

**Liste tous les utilisateurs:**
```bash
curl -X GET "$BASE_URL/admin/users?page=1&per_page=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Supprimer un utilisateur:**
```bash
curl -X DELETE "$BASE_URL/admin/users/5" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Modifier le rôle d'un utilisateur:**
```bash
curl -X PUT "$BASE_URL/admin/users/5/role" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "admin"
  }'
```

### 7.2 Notes

**Liste toutes les notes:**
```bash
curl -X GET "$BASE_URL/admin/notes" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Détails d'une note:**
```bash
curl -X GET "$BASE_URL/admin/notes/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Modifier une note:**
```bash
curl -X PUT "$BASE_URL/admin/notes/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Note modifiée par admin",
    "important": true
  }'
```

**Supprimer une note:**
```bash
curl -X DELETE "$BASE_URL/admin/notes/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 7.3 Contacts

**Liste tous les contacts:**
```bash
curl -X GET "$BASE_URL/admin/contacts" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Détails d'un contact:**
```bash
curl -X GET "$BASE_URL/admin/contacts/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Modifier un contact:**
```bash
curl -X PUT "$BASE_URL/admin/contacts/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Nouveau surnom admin"
  }'
```

**Supprimer un contact:**
```bash
curl -X DELETE "$BASE_URL/admin/contacts/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 7.4 Assignments

**Liste toutes les assignations:**
```bash
curl -X GET "$BASE_URL/admin/assignments" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Détails d'une assignation:**
```bash
curl -X GET "$BASE_URL/admin/assignments/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Modifier une assignation:**
```bash
curl -X PUT "$BASE_URL/admin/assignments/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_read": true,
    "recipient_priority": true
  }'
```

**Supprimer une assignation:**
```bash
curl -X DELETE "$BASE_URL/admin/assignments/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 7.5 Statistiques globales
```bash
curl -X GET "$BASE_URL/admin/stats" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 🔐 8. TESTS DE SÉCURITÉ

### 8.1 Accès sans token (401)
```bash
curl -X GET "$BASE_URL/notes"
```

### 8.2 Token invalide (401)
```bash
curl -X GET "$BASE_URL/notes" \
  -H "Authorization: Bearer invalid_token_xyz"
```

---

## 🧪 9. TESTS DE VALIDATION

### 9.1 Email invalide (400)
```bash
curl -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "invalid-email",
    "password": "pass123"
  }'
```

### 9.2 Mot de passe court (400)
```bash
curl -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@test.com",
    "password": "123"
  }'
```

### 9.3 Note sans contenu (400)
```bash
curl -X POST $BASE_URL/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "important": true
  }'
```

---

## 💡 TIPS

### Formater la sortie JSON avec python
```bash
curl ... | python3 -m json.tool
```

### Formater avec jq (si installé)
```bash
curl ... | jq .
```

### Afficher les headers de réponse
```bash
curl -i ...
```

### Mode verbeux pour debug
```bash
curl -v ...
```

### Sauvegarder la réponse dans un fichier
```bash
curl ... > response.json
```

### Extraire une valeur JSON
```bash
TOKEN=$(curl ... | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```
