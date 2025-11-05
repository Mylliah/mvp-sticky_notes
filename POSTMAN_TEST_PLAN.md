# 📮 Plan de Tests Postman - MVP Sticky Notes

**Objectif** : Valider tous les endpoints du backend avant de développer le frontend

**Base URL** : `http://localhost:5000/v1`

**Résumé des endpoints** : 48 endpoints au total
- 🔐 Authentification : 2 endpoints
- 📝 Notes : 7 endpoints
- 👥 Contacts : 7 endpoints
- 📌 Assignations : 8 endpoints
- 📋 Action Logs : 3 endpoints
- 👤 Utilisateurs : 5 endpoints
- 🛡️ Admin : 16 endpoints

---

## 🔐 1. Authentification (2 endpoints)

### 1.1 POST /auth/register ✅
```json
POST http://localhost:5000/v1/auth/register
Content-Type: application/json

{
  "username": "testuser1",
  "email": "testuser1@test.com",
  "password": "SecurePass123!"
}
```
**Attendu** : 201, JWT token retourné

### 1.2 POST /auth/login ✅
```json
POST http://localhost:5000/v1/auth/login
Content-Type: application/json

{
  "email": "testuser1@test.com",
  "password": "SecurePass123!"
}
```
**Attendu** : 200, JWT token + username retournés

---

## 📝 2. Notes (7 endpoints) 

### 2.1 POST /notes - Créer une note ✅
```json
POST http://localhost:5000/v1/notes
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "content": "Ma première note de test",
  "important": true
}
```
**Attendu** : 201, note créée

### 2.2 GET /notes - Lister (pagination) ✅
```
GET http://localhost:5000/v1/notes?page=1&per_page=10
Authorization: Bearer {{token}}
```
**Attendu** : 200, { notes: [], total, page, per_page, pages, has_next, has_prev }

### 2.3 GET /notes?filter=important - Filtrer ✅
```
GET http://localhost:5000/v1/notes?filter=important
Authorization: Bearer {{token}}
```
**Attendu** : 200, seulement les notes importantes

### 2.4 GET /notes?sort=date_asc - Trier ✅
```
GET http://localhost:5000/v1/notes?sort=date_asc
Authorization: Bearer {{token}}
```
**Attendu** : 200, notes triées par date croissante

### 2.5 GET /notes/:id - Détails ✅
```
GET http://localhost:5000/v1/notes/1
Authorization: Bearer {{token}}
```
**Attendu** : 200, détails de la note

### 2.6 PUT /notes/:id - Modifier ✅
```json
PUT http://localhost:5000/v1/notes/1
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "content": "Note modifiée",
  "important": false
}
```
**Attendu** : 200, note mise à jour

### 2.7 DELETE /notes/:id - Supprimer (soft delete) ✅
```
DELETE http://localhost:5000/v1/notes/1 
Authorization: Bearer {{token}}
```
**Attendu** : 200 ou 204

### 2.8 GET /notes/:id/details - Détails complets ✅
```
GET http://localhost:5000/v1/notes/1/details
Authorization: Bearer {{token}}
```
**Attendu** : 200, détails note + liste des assignés

### 2.9 GET /notes/:id/assignments - Liste assignations (créateur) ✅
```
GET http://localhost:5000/v1/notes/1/assignments
Authorization: Bearer {{token}}
```
**Attendu** : 200, liste assignations (seulement créateur de la note)

---

## 👥 3. Contacts (7 endpoints)

### 3.1 GET /users - Liste des utilisateurs ✅
```
GET http://localhost:5000/v1/users
Authorization: Bearer {{token}}
```
**Attendu** : 200, liste des utilisateurs

### 3.2 POST /contacts - Ajouter un contact ✅
```json
POST http://localhost:5000/v1/contacts
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "contact_username": "bob_test",
  "nickname": "Mon collègue"
}
```
**Attendu** : 201, contact créé

### 3.3 GET /contacts - Liste contacts ✅
```
GET http://localhost:5000/v1/contacts
Authorization: Bearer {{token}}
```
**Attendu** : 200, liste des contacts + "Moi"

### 3.4 PUT /contacts/:id - Modifier nickname ✅
```json
PUT http://localhost:5000/v1/contacts/1
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "nickname": "Nouveau surnom"
}
```
**Attendu** : 200, contact mis à jour

### 3.5 DELETE /contacts/:id - Supprimer ✅
```
DELETE http://localhost:5000/v1/contacts/1
Authorization: Bearer {{token}}
```
**Attendu** : 200 ou 204

### 3.6 GET /contacts/:id - Détails d'un contact ✅
```
GET http://localhost:5000/v1/contacts/1
Authorization: Bearer {{token}}
```
**Attendu** : 200, détails du contact avec is_mutual

### 3.7 GET /contacts/assignable - Utilisateurs assignables ✅
```
GET http://localhost:5000/v1/contacts/assignable
Authorization: Bearer {{token}}
```
**Attendu** : 200, liste utilisateurs (soi-même + contacts mutuels)

### 3.8 GET /contacts/:id/notes - Notes échangées avec un contact ✅
```
# Toutes les notes échangées
GET http://localhost:5000/v1/contacts/5/notes
Authorization: Bearer {{token}}

# Notes envoyées à ce contact
GET http://localhost:5000/v1/contacts/5/notes?filter=sent
Authorization: Bearer {{token}}

# Notes reçues de ce contact
GET http://localhost:5000/v1/contacts/5/notes?filter=received
Authorization: Bearer {{token}}

# Notes non lues de ce contact
GET http://localhost:5000/v1/contacts/5/notes?filter=unread
Authorization: Bearer {{token}}

# Notes importantes
GET http://localhost:5000/v1/contacts/5/notes?filter=important
Authorization: Bearer {{token}}

# Tri par date croissante
GET http://localhost:5000/v1/contacts/5/notes?sort=date_asc
Authorization: Bearer {{token}}

# Notes importantes en premier
GET http://localhost:5000/v1/contacts/5/notes?sort=important_first
Authorization: Bearer {{token}}

# Avec pagination
GET http://localhost:5000/v1/contacts/5/notes?page=1&per_page=10
Authorization: Bearer {{token}}

# Combinaison filtres + tri + pagination
GET http://localhost:5000/v1/contacts/5/notes?filter=unread&sort=date_asc&page=1&per_page=5
Authorization: Bearer {{token}}
```
**Attendu** : 200, liste des notes échangées avec le contact (envoyées + reçues)

**Filtres disponibles** :
- `filter=sent` : Notes que j'ai envoyées à ce contact
- `filter=received` : Notes que j'ai reçues de ce contact
- `filter=unread` : Notes non lues de ce contact
- `filter=important` : Notes marquées importantes

**Tri disponible** :
- `sort=date_desc` : Par date décroissante (défaut)
- `sort=date_asc` : Par date croissante
- `sort=important_first` : Notes importantes en premier

**Pagination** :
- `page=1` : Numéro de page
- `per_page=20` : Éléments par page (max: 100)

---

## 📌 4. Assignments (8 endpoints)

### 4.1 POST /assignments - Assigner une note ✅
```json
POST http://localhost:5000/v1/assignments
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "note_id": 1,
  "user_id": 5
}
```
**Attendu** : 201, assignation créée

### 4.4 GET /assignments - Lister (avec pagination) ✅
```
GET http://localhost:5000/v1/assignments?page=1&per_page=10
Authorization: Bearer {{token}}
```
**Attendu** : 200, liste paginée + meta

### 4.5 PUT /assignments/:id - Modifier une assignation ✅
```json
PUT http://localhost:5000/v1/assignments/1
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "note_id": 2,
  "assigned_to_id": 3
}
```
**Attendu** : 200, assignation mise à jour

### 4.6 DELETE /assignments/:id - Supprimer une assignation ✅
```
DELETE http://localhost:5000/v1/assignments/1
Authorization: Bearer {{token}}
```
**Attendu** : 200 ou 204

### 4.7 PUT /assignments/:id/status - Changer le statut d'avancement ✅
```json
# Marquer comme terminé
PUT http://localhost:5000/v1/assignments/1/status
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "recipient_status": "terminé"
}

# Remettre en cours
PUT http://localhost:5000/v1/assignments/1/status
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "recipient_status": "en_cours"
}
```
**Attendu** : 200, statut mis à jour ('en_cours' ou 'terminé')
**Note** : Quand passé à 'terminé', `finished_date` est rempli automatiquement

### 4.8 GET /assignments/unread - Assignations non lues ✅
```
GET http://localhost:5000/v1/assignments/unread
Authorization: Bearer {{token}}
```
**Attendu** : 200, liste des assignations avec `is_read=false`
**Note** : Retourne uniquement MES assignations non lues (isolation par utilisateur)

### 4.8 PUT /assignments/:id/priority - Toggle priorité personnelle ✅
```
PUT http://localhost:5000/v1/assignments/1/priority
Authorization: Bearer {{token}}
```
**Attendu** : 200, `recipient_priority` basculé (true ↔ false)
**Note** : Seul le destinataire peut modifier sa propre priorité

---

## 📊 5. Action Logs (3 endpoints)

**⚠️ Note importante** : Les Action Logs sont **immuables** (pas de POST/PUT/DELETE).  
Ils sont créés automatiquement par le système. Seule la consultation est possible (admin uniquement).

### 5.1 GET /action_logs (avec pagination) ✅
```
GET http://localhost:5000/v1/action_logs?page=1&per_page=20
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, liste paginée d'action_logs (admin uniquement)

### 5.2 GET /action_logs/:id - Détails d'un log spécifique ✅
```
GET http://localhost:5000/v1/action_logs/123
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, détails d'un action log spécifique (admin uniquement)

### 5.3 GET /action_logs/stats - Statistiques des logs ✅
```
GET http://localhost:5000/v1/action_logs/stats
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, statistiques d'utilisation (actions par type, etc.) (admin uniquement)

---

## 📌 6. Utilisateurs (5 endpoints)

### 6.1 POST /users - Créer un utilisateur ✅
```json
POST http://localhost:5000/v1/users
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepass123"
}
```
**Attendu** : 201, utilisateur créé

### 6.2 GET /users/:id - Détails d'un utilisateur ✅
```
GET http://localhost:5000/v1/users/1
Authorization: Bearer {{token}}
```
**Attendu** : 200, détails de l'utilisateur

### 6.3 GET /users/me - Profil utilisateur connecté ✅
```
GET http://localhost:5000/v1/users/me
Authorization: Bearer {{token}}
```
**Attendu** : 200, infos du user connecté

### 6.4 PUT /users/:id - Modifier un profil utilisateur ✅
```json
PUT http://localhost:5000/v1/users/1
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "username": "newusername",
  "email": "newemail@example.com"
}
```
**Attendu** : 200, profil mis à jour

### 6.5 DELETE /users/:id - Supprimer un utilisateur ✅
```
DELETE http://localhost:5000/v1/users/1
Authorization: Bearer {{token}}
```
**Attendu** : 200 ou 204 (action logs conservés avec user_id NULL)

---

## 📌 7. Admin (16 endpoints)

### 7.1 Utilisateurs (3 endpoints)

**Liste tous les utilisateurs:**
```
GET http://localhost:5000/v1/admin/users?page=1&per_page=20
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, liste de tous les utilisateurs

**Supprimer un utilisateur:**
```
DELETE http://localhost:5000/v1/admin/users/5
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200 ou 204, utilisateur supprimé

**Modifier le rôle:**
```json
PUT http://localhost:5000/v1/admin/users/5/role
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "role": "admin"
}
```
**Attendu** : 200, rôle mis à jour

### 7.2 Notes (4 endpoints)

**Liste toutes les notes:**
```
GET http://localhost:5000/v1/admin/notes
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, liste de toutes les notes

**Détails d'une note:**
```
GET http://localhost:5000/v1/admin/notes/1
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, détails de la note

**Modifier une note:**
```json
PUT http://localhost:5000/v1/admin/notes/1
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "content": "Note modifiée par admin",
  "important": true
}
```
**Attendu** : 200, note mise à jour

**Supprimer une note:**
```
DELETE http://localhost:5000/v1/admin/notes/1
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200 ou 204, note supprimée

### 7.3 Contacts (4 endpoints)

**Liste tous les contacts:**
```
GET http://localhost:5000/v1/admin/contacts
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, liste de tous les contacts

**Détails d'un contact:**
```
GET http://localhost:5000/v1/admin/contacts/1
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, détails du contact

**Modifier un contact:**
```json
PUT http://localhost:5000/v1/admin/contacts/1
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "nickname": "Nouveau surnom admin"
}
```
**Attendu** : 200, contact mis à jour

**Supprimer un contact:**
```
DELETE http://localhost:5000/v1/admin/contacts/1
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200 ou 204, contact supprimé

### 7.4 Assignments (4 endpoints)

**Liste toutes les assignations:**
```
GET http://localhost:5000/v1/admin/assignments
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, liste de toutes les assignations

**Détails d'une assignation:**
```
GET http://localhost:5000/v1/admin/assignments/1
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, détails de l'assignation

**Modifier une assignation:**
```json
PUT http://localhost:5000/v1/admin/assignments/1
Authorization: Bearer {{admin_token}}
Content-Type: application/json

{
  "is_read": true,
  "recipient_priority": true
}
```
**Attendu** : 200, assignation mise à jour

**Supprimer une assignation:**
```
DELETE http://localhost:5000/v1/admin/assignments/1
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200 ou 204, assignation supprimée

### 7.5 Statistiques (1 endpoint)

**Statistiques globales:**
```
GET http://localhost:5000/v1/admin/stats
Authorization: Bearer {{admin_token}}
```
**Attendu** : 200, statistiques du système

---

## 🔐 8. Tests de Sécurité

### 8.1 Accès sans token (401)
```
GET http://localhost:5000/v1/notes
```
**Attendu** : 401 Unauthorized

### 8.2 Token invalide (401)
```
GET http://localhost:5000/v1/notes
Authorization: Bearer invalid_token_xyz
```
**Attendu** : 401 Invalid token

### 8.3 Accès note d'un autre utilisateur (403)
```
GET http://localhost:5000/v1/notes/999
Authorization: Bearer {{token_user1}}
```
**Attendu** : 403 Forbidden (si note appartient à user2)

---

## 🧪 9. Tests de Validation

### 9.1 Email invalide (400)
```json
POST http://localhost:5000/v1/auth/register
Content-Type: application/json

{
  "username": "test",
  "email": "invalid-email",
  "password": "pass123"
}
```
**Attendu** : 400, erreur validation email

### 9.2 Mot de passe court (400)
```json
POST http://localhost:5000/v1/auth/register
Content-Type: application/json

{
  "username": "test",
  "email": "test@test.com",
  "password": "123"
}
```
**Attendu** : 400, erreur validation password

### 9.3 Note sans contenu (400)
```json
POST http://localhost:5000/v1/notes
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "important": true
}
```
**Attendu** : 400, Missing content

---

## 🚦 10. Tests Rate Limiting

### 10.1 Rate limit register (3/min)
```
POST /auth/register x 4 fois en < 1 minute
```
**Attendu** : 4ème requête → 429 Too Many Requests

### 10.2 Rate limit login (5/min)
```
POST /auth/login x 6 fois en < 1 minute
```
**Attendu** : 6ème requête → 429 Too Many Requests

---

## ✅ Checklist de Validation

- [ ] **Authentification (2 endpoints)** : register, login fonctionnent avec JWT
- [ ] **Notes (7 endpoints)** : CRUD complet + filtres + détails + assignations
- [ ] **Contacts (7 endpoints)** : CRUD complet + notes échangées + assignable + détails
- [ ] **Assignations (8 endpoints)** : CRUD + status + priority + unread
- [ ] **Action Logs (3 endpoints)** : liste + détails + stats (admin uniquement, immuables)
- [ ] **Utilisateurs (5 endpoints)** : CRUD + profil me + update + delete
- [ ] **Admin (16 endpoints)** : CRUD complet sur users/notes/contacts/assignments + stats
- [ ] **Sécurité (3 tests)** : 401 sans token, 401 token invalide, 403 accès interdit
- [ ] **Validation (3 tests)** : email invalide, password court, note sans contenu
- [ ] **Rate Limiting (2 tests)** : register 3/min, login 5/min
- [ ] Pagination fonctionne (page, per_page, total, has_next)
- [ ] Isolation des données (user1 ne voit pas notes de user2)
- [ ] Soft delete fonctionne (delete_date, deleted_by)
- [ ] Action logs conservés après suppression utilisateur (user_id NULL)
- [ ] CORS autorise les origines configurées
- [ ] Tous les endpoints retournent les bons codes HTTP (200, 201, 204, 400, 401, 403, 404, 429)

---

## 📦 Export Collection Postman

Une fois les tests validés, exporter la collection :
1. Postman → Collections → ... → Export
2. Sauvegarder dans `/postman/mvp-sticky-notes.postman_collection.json`
3. Partager avec l'équipe / Frontend dev

---

**Durée estimée** : 30 minutes - 1 heure
**Résultat attendu** : Backend validé à 100% avant développement frontend
