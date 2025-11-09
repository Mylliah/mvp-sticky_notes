# 📋 Référence Rapide des Routes API

**Total : 48 endpoints** (2 auth + 5 users + 7 notes + 8 assignments + 7 contacts + 3 action_logs + 16 admin)  
**Base URL :** `http://localhost:5000/v1`  
**Authentification :** Bearer Token JWT (sauf register et login)
/v1/auth/register      ← Pas d'auth requise
/v1/auth/login         ← Pas d'auth requise
/v1/users              ← Auth requise
/v1/notes              ← Auth requise
/v1/assignments        ← Auth requise
/v1/contacts           ← Auth requise
/v1/action_logs        ← Auth requise
/v1/admin              ← Auth requise + admin

---

## 🔐 1. Authentication (2 endpoints)

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/auth/register` | Crée un nouveau compte utilisateur (email unique, password min 8 chars) |
| POST | `/auth/login` | Authentifie un utilisateur et retourne un token JWT |

---

## 👤 2. Users (5 endpoints)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/users/me` | Récupère le profil de l'utilisateur connecté |
| GET | `/users` | Liste tous les utilisateurs |
| GET | `/users/:id` | Récupère un utilisateur spécifique par ID |
| PUT | `/users/:id` | Met à jour un utilisateur (propriétaire ou admin) |
| DELETE | `/users/:id` | Supprime un utilisateur (propriétaire ou admin) |

**Note :** Créer un utilisateur se fait via `/auth/register` uniquement

---

## 📝 3. Notes (7 endpoints)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/notes` | Liste toutes les notes de l'utilisateur avec filtres/tri/pagination |
| POST | `/notes` | Crée une nouvelle note avec contenu |
| GET | `/notes/:id` | Récupère une note spécifique (créateur ou destinataire) |
| GET | `/notes/:id/details` | Récupère les détails complets d'une note avec assignation |
| GET | `/notes/:id/assignments` | Liste toutes les assignations d'une note (créateur uniquement) |
| PUT | `/notes/:id` | Met à jour une note existante (créateur uniquement) |
| DELETE | `/notes/:id` | Supprime une note (soft delete, créateur ou destinataire) |

**Note :** Marquer comme lu/important se fait via les routes `/assignments/:id` et `/assignments/:id/priority`

---

## 📧 4. Assignments (8 endpoints)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/assignments` | Liste toutes les assignations de l'utilisateur |
| GET | `/assignments/unread` | Liste les assignations non lues de l'utilisateur |
| GET | `/assignments/:id` | Récupère une assignation spécifique |
| POST | `/assignments` | Crée une assignation (note_id + user_id, créateur uniquement) |
| PUT | `/assignments/:id` | Met à jour une assignation (créateur uniquement) |
| DELETE | `/assignments/:id` | Supprime une assignation (créateur uniquement) |
| PUT | `/assignments/:id/priority` | Bascule la priorité personnelle (destinataire uniquement) |
| PUT | `/assignments/:id/status` | Change le statut personnel (destinataire uniquement: en_cours/terminé) |

**Note :** Filtrer notes reçues/envoyées se fait via `/notes?filter=received` ou `/notes?filter=sent`

---

## 👥 5. Contacts (7 endpoints)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/contacts` | Liste tous les contacts de l'utilisateur (incluant soi-même) |
| GET | `/contacts/assignable` | Liste les utilisateurs assignables (contacts + soi-même) |
| GET | `/contacts/:id` | Récupère un contact spécifique |
| GET | `/contacts/:id/notes` | Récupère toutes les notes échangées avec un contact spécifique |
| POST | `/contacts` | Crée un nouveau contact (user_id + contact_user_id + nickname) |
| PUT | `/contacts/:id` | Met à jour un contact existant (nickname) |
| DELETE | `/contacts/:id` | Supprime un contact |

### 📖 Détails GET /contacts/:id/notes

Retourne toutes les notes échangées entre l'utilisateur connecté et un contact spécifique (notes envoyées + notes reçues).

**Filtres supportés :**
- `filter=sent` : Uniquement les notes envoyées à ce contact
- `filter=received` : Uniquement les notes reçues de ce contact
- `filter=unread` : Uniquement les notes non lues de ce contact
- `filter=important` : Uniquement les notes marquées importantes

**Tri supporté :**
- `sort=date_desc` : Par date décroissante (défaut)
- `sort=date_asc` : Par date croissante
- `sort=important_first` : Notes importantes en premier

**Pagination :**
- `page=1` : Numéro de page (défaut: 1)
- `per_page=20` : Éléments par page (défaut: 20, max: 100)

**Exemples :**
```
GET /v1/contacts/5/notes                                    # Toutes les notes avec Bob
GET /v1/contacts/5/notes?filter=sent                        # Mes notes envoyées à Bob
GET /v1/contacts/5/notes?filter=received&sort=date_asc      # Notes de Bob, plus anciennes d'abord
GET /v1/contacts/5/notes?filter=unread&per_page=10          # Notes non lues de Bob, 10 par page
```

---

## 📊 6. Action Logs (3 endpoints - Admin uniquement, LECTURE SEULE)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/action_logs` | Liste tous les logs d'actions avec filtres et pagination (admin) |
| GET | `/action_logs/:id` | Récupère un log d'action spécifique (admin) |
| GET | `/action_logs/stats` | Retourne les statistiques d'activité globales (admin) |

**⚠️ IMPORTANT :** Les logs sont **créés automatiquement** par le système lors des actions utilisateurs.  
Aucune création/modification/suppression manuelle n'est permise (pas de POST/PUT/DELETE) pour garantir l'intégrité de l'audit.

---

## ⚙️ 7. Admin (16 endpoints - Réservé aux administrateurs)

**Vue d'ensemble et statistiques :**
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/admin/users` | Liste tous les utilisateurs |
| GET | `/admin/notes` | Liste toutes les notes (incluant soft deleted) |
| GET | `/admin/contacts` | Liste tous les contacts |
| GET | `/admin/assignments` | Liste toutes les assignations |
| GET | `/admin/stats` | Statistiques globales de la plateforme |

**Gestion des utilisateurs :**
| Méthode | Route | Description |
|---------|-------|-------------|
| DELETE | `/admin/users/:id` | Supprime définitivement un utilisateur (hard delete + cascade) |
| PUT | `/admin/users/:id/role` | Change le rôle d'un utilisateur (user/admin) |

**CRUD Notes (pour support utilisateur) :**
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/admin/notes/:id` | Récupère une note spécifique |
| PUT | `/admin/notes/:id` | Modifie une note (content, important, status) |
| DELETE | `/admin/notes/:id` | Supprime définitivement une note (hard delete) |

**CRUD Contacts (pour support utilisateur) :**
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/admin/contacts/:id` | Récupère un contact spécifique |
| PUT | `/admin/contacts/:id` | Modifie un contact (nickname) |
| DELETE | `/admin/contacts/:id` | Supprime un contact |

**CRUD Assignments (pour support utilisateur) :**
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/admin/assignments/:id` | Récupère une assignation spécifique |
| PUT | `/admin/assignments/:id` | Modifie une assignation (is_read, recipient_priority, recipient_status, user_id) |
| DELETE | `/admin/assignments/:id` | Supprime une assignation |

---

## 📝 Filtres disponibles (GET /notes)

| Paramètre | Valeurs | Description |
|-----------|---------|-------------|
| `filter` | `received` | Notes reçues (incluant auto-assignations) |
| `filter` | `sent` | Notes envoyées avec au moins une assignation |
| `filter` | `unread` | Notes avec is_read=false |
| `filter` | `important` | Notes marquées importantes par le créateur |
| `filter` | `important_by_me` | Notes marquées prioritaires par le destinataire |
| `sort` | `date_asc` | Tri par created_date ascendant (plus anciennes en premier) |
| `sort` | `date_desc` | Tri par created_date descendant (plus récentes en premier) **[DÉFAUT]** |
| `sort` | `important_first` | Notes importantes d'abord, puis par date descendante |
| `page` | nombre | Numéro de page (défaut: 1) |
| `per_page` | nombre | Éléments par page (défaut: 20, max: 100) |

---

## 🔒 Rate Limiting

- **POST /auth/register** : 3 requêtes/minute
- **POST /auth/login** : 5 requêtes/minute
- Autres endpoints : pas de limite spécifique

---

## 📌 Notes importantes

1. **Soft Delete** : Notes utilisent `delete_date` (données préservées pour traçabilité)
2. **Hard Delete** : Suppression définitive via routes admin uniquement
3. **ActionLog** : Réservé aux admins uniquement (@admin_required sur toutes les routes)
4. **Contacts** : Relation NON mutuelle (A→B ≠ B→A automatiquement), vérifier avec `is_mutual()`
5. **Assignments** : 
   - `recipient_status` peut être 'en_cours' ou 'terminé'
   - Une assignation à la fois (drag & drop front), route batch prévue plus tard
6. **Suppression de notes** :
   - Créateur et destinataires peuvent supprimer (soft delete)
   - `deleted_by` enregistre qui a supprimé (traçabilité)
   - Créateur voit toujours qui a supprimé
   - Destinataire voit seulement si le créateur a supprimé (signal de fin)
7. **finished_date** : Rempli automatiquement quand recipient_status='terminé'
8. **Email** : Validation stricte RFC 5322 via email-validator
9. **Password** : Minimum 8 caractères requis

---

**Dernière mise à jour :** 21 octobre 2025  
**Version :** 1.2  
**Coverage :** 98% (341 tests pytest)
