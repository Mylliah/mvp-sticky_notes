# 📝 MVP Sticky Notes

> **Application de gestion collaborative de notes** - Backend API REST avec Flask, PostgreSQL et JWT

[![Tests](https://img.shields.io/badge/tests-398%20passed-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)](https://www.postgresql.org/)

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API Documentation](#-api-documentation)
- [Tests](#-tests)
- [Développement](#-développement)
- [Déploiement](#-déploiement)

---

## ✨ Fonctionnalités

### 🔐 Authentification & Utilisateurs
- ✅ Inscription et connexion avec JWT
- ✅ Gestion des mots de passe hashés (bcrypt)
- ✅ Gestion de profil utilisateur
- ✅ Isolation complète des données par utilisateur

### 📌 Gestion de Notes
- ✅ CRUD complet sur les notes
- ✅ Statut personnalisable (défaut : `en_cours`)
- ✅ Marquage de notes importantes
- ✅ Dates de création, modification, lecture, suppression
- ✅ **Isolation des données** : chaque utilisateur ne voit que ses notes et celles assignées

### 👥 Contacts & Collaboration
- ✅ Ajout de contacts avec pseudonymes personnalisés
- ✅ Liste des utilisateurs assignables
- ✅ Contact "self" automatique pour chaque utilisateur
- ✅ Prévention d'auto-ajout et de doublons

### 📤 Assignations
- ✅ Assignation de notes à des utilisateurs
- ✅ Tracking du statut de lecture (`is_read`)
- ✅ Prévention de doublons d'assignation
- ✅ Suppression en cascade

### 📊 Logs d'Actions
- ✅ Traçabilité de toutes les actions
- ✅ Filtrage par utilisateur et type d'action
- ✅ Pagination et statistiques

### 🔧 Administration
- ✅ Routes `/admin/*` pour gestion globale
- ✅ Consultation de toutes les données
- ✅ Hard delete et supervision complète
- ✅ Logs d'actions administratives

---

## 🏗️ Architecture

### Stack Technique

```
Backend:
├── Flask 3.0              # Framework web
├── SQLAlchemy 2.0         # ORM
├── PostgreSQL 15          # Base de données
├── Flask-JWT-Extended     # Authentification JWT
├── Flask-Migrate          # Migrations Alembic
├── Flask-Limiter          # Rate limiting
├── Flask-CORS             # Cross-Origin Resource Sharing
├── Bcrypt                 # Hashage de mots de passe
└── pytest + pytest-cov    # Tests et coverage

Frontend:
├── HTML5/CSS3/JavaScript  # Interface utilisateur
├── Fetch API              # Communication avec backend
└── LocalStorage           # Persistance locale

Infrastructure:
├── Docker & Docker Compose
├── Gunicorn (WSGI server)
└── Adminer (interface DB)
```

### Structure du Projet

```
mvp-sticky_notes/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Factory app Flask
│   │   ├── decorators.py         # Décorateurs personnalisés
│   │   ├── models/               # Modèles SQLAlchemy
│   │   │   ├── user.py           # 44 lignes, 100% couvert
│   │   │   ├── note.py           # 34 lignes, 100% couvert
│   │   │   ├── contact.py        # 16 lignes, 100% couvert
│   │   │   ├── assignment.py     # 15 lignes, 100% couvert
│   │   │   └── action_log.py     # 15 lignes, 100% couvert
│   │   └── routes/v1/            # Routes API v1
│   │       ├── auth.py           # Authentification
│   │       ├── notes.py          # CRUD notes
│   │       ├── contacts.py       # Gestion contacts
│   │       ├── assignments.py    # Assignations
│   │       ├── users.py          # Gestion users
│   │       ├── action_logs.py    # Logs actions
│   │       └── admin.py          # Administration
│   ├── migrations/               # Migrations Alembic
│   ├── tests/                    # Suite de tests (398 tests)
│   │   ├── models/               # Tests unitaires modèles
│   │   ├── routes/               # Tests d'intégration routes
│   │   ├── e2e/                  # Tests E2E workflows
│   │   └── test_app.py           # Tests base app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── index.html                # Page de connexion
│   ├── dashboard.html            # Interface principale
│   ├── styles.css                # Styles CSS
│   └── app.js                    # Logique JavaScript
├── docker-compose.yml
└── README.md
```

### Modèle de Données

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    User     │         │     Note     │         │   Contact   │
├─────────────┤         ├──────────────┤         ├─────────────┤
│ id          │────┐    │ id           │    ┌────│ user_id     │
│ username    │    │    │ content      │    │    │ contact_id  │
│ email       │    └───→│ creator_id   │    │    │ nickname    │
│ password    │         │ status       │    │    └─────────────┘
│ created_date│         │ important    │    │
└─────────────┘         │ created_date │    │    ┌─────────────┐
                        └──────────────┘    │    │ Assignment  │
                               │            │    ├─────────────┤
                               └────────────┼───→│ note_id     │
                                            └───→│ user_id     │
                                                 │ is_read     │
                                                 └─────────────┘
```

---

## 🚀 Installation

### Prérequis

- Docker & Docker Compose
- Git

### Cloner le projet

```bash
git clone https://github.com/Mylliah/mvp-sticky_notes.git
cd mvp-sticky_notes
```

### Lancer l'application

```bash
# Démarrer tous les services
docker compose up -d --build

# Vérifier que tout fonctionne
curl http://localhost:5000/health
# → {"status": "ok"}
```

### Services disponibles

| Service | URL | Description |
|---------|-----|-------------|
| **API Backend** | http://localhost:5000 | API REST Flask |
| **Adminer** | http://localhost:8080 | Interface web PostgreSQL |
| **PostgreSQL** | localhost:5432 | Base de données |

**Connexion Adminer :**
- Système : `PostgreSQL`
- Serveur : `db`
- Utilisateur : `app`
- Mot de passe : `app`
- Base de données : `appdb`

---

## 🎯 Utilisation

### Exemple de workflow complet

```bash
# 1. Inscription d'un utilisateur
curl -X POST http://localhost:5000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePass123!"
  }'

# 2. Connexion
curl -X POST http://localhost:5000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "SecurePass123!"
  }'
# → Récupérer le access_token

# 3. Créer une note
curl -X POST http://localhost:5000/v1/notes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Ma première note",
    "important": true
  }'

# 4. Lister mes notes
curl http://localhost:5000/v1/notes \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. Ajouter un contact
curl -X POST http://localhost:5000/v1/contacts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_username": "bob",
    "nickname": "Bob le dev"
  }'

# 6. Assigner une note
curl -X POST http://localhost:5000/v1/assignments \
  -H "Content-Type: application/json" \
  -d '{
    "note_id": 1,
    "user_id": 2
  }'
```

---

## 📚 API Documentation

### Authentification

#### `POST /v1/auth/register`
**Inscription d'un nouvel utilisateur**

```json
Request:
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "SecurePass123!"
}

Response: 201 Created
{
  "msg": "User created successfully",
  "id": 1,
  "username": "alice",
  "email": "alice@example.com"
}
```

#### `POST /v1/auth/login`
**Connexion et obtention du JWT**

```json
Request:
{
  "username": "alice",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com"
  }
}
```

### Notes

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/v1/notes` | GET | ✅ | Liste des notes (créées + assignées) |
| `/v1/notes` | POST | ✅ | Créer une note |
| `/v1/notes/:id` | GET | ✅ | Détails d'une note |
| `/v1/notes/:id` | PUT | ✅ | Modifier une note |
| `/v1/notes/:id` | DELETE | ✅ | Supprimer une note |
| `/v1/notes/:id/details` | GET | ✅ | Détails + assignations |

### Contacts

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/v1/contacts` | GET | ✅ | Liste des contacts |
| `/v1/contacts` | POST | ✅ | Ajouter un contact |
| `/v1/contacts/:id` | GET | ✅ | Détails d'un contact |
| `/v1/contacts/:id` | PUT | ✅ | Modifier un contact |
| `/v1/contacts/:id` | DELETE | ✅ | Supprimer un contact |
| `/v1/contacts/assignable` | GET | ✅ | Utilisateurs assignables |

### Assignations

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/v1/assignments` | GET | ❌ | Liste des assignations |
| `/v1/assignments` | POST | ❌ | Créer une assignation |
| `/v1/assignments/:id` | GET | ❌ | Détails assignation |
| `/v1/assignments/:id` | PUT | ❌ | Modifier assignation |
| `/v1/assignments/:id` | DELETE | ❌ | Supprimer assignation |

### Utilisateurs

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/v1/users` | GET | ❌ | Liste des utilisateurs |
| `/v1/users/:id` | GET | ❌ | Profil utilisateur |
| `/v1/users/:id` | PUT | ❌ | Modifier utilisateur |
| `/v1/users/:id` | DELETE | ❌ | Supprimer utilisateur |

### Action Logs

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/v1/action-logs` | GET | ❌ | Liste des logs (filtres: user_id, action_type) |
| `/v1/action-logs` | POST | ❌ | Créer un log |
| `/v1/action-logs/:id` | GET | ❌ | Détails d'un log |
| `/v1/action-logs/:id` | DELETE | ❌ | Supprimer un log |
| `/v1/action-logs/stats` | GET | ❌ | Statistiques des actions |

### Administration

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/v1/admin/users` | GET | ✅ | Liste globale utilisateurs |
| `/v1/admin/notes` | GET | ✅ | Liste globale notes |
| `/v1/admin/assignments` | GET | ✅ | Liste globale assignations |
| `/v1/admin/contacts` | GET | ✅ | Liste globale contacts |
| `/v1/admin/action-logs` | GET | ✅ | Logs d'administration |
| `/v1/admin/*/:id` | DELETE | ✅ | Hard delete (admin only) |

---

## 🧪 Tests

### Statistiques de tests

```
✅ 398 tests passent à 100%
📊 Coverage : 98% (493/502 lignes)
⏱️  Temps d'exécution : ~65 secondes
```

### Détail par catégorie

| Catégorie | Tests | Coverage | Description |
|-----------|-------|----------|-------------|
| **Tests E2E** | 32 | - | Scénarios complets utilisateur |
| **Tests unitaires (models)** | ~100 | 100% | Tous les modèles |
| **Tests intégration (routes)** | ~260 | 98% | Toutes les routes + admin |
| **Tests base app** | ~6 | 98% | Health check, JWT handlers |

### Coverage par module

```
Module                     Coverage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app/__init__.py            98%  (51/52)
app/decorators.py          100% (15/15)
app/models/*               100% (130/130)
app/routes/v1/*            98%  (312/319)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL                      98%  (493/502)
```

### Lancer les tests

```bash
# Tous les tests avec coverage
docker compose exec backend pytest tests/ --cov=app --cov-report=html

# Tests par catégorie
docker compose exec backend pytest tests/models/ -v        # Unitaires
docker compose exec backend pytest tests/routes/ -v        # Intégration
docker compose exec backend pytest tests/e2e/ -v -m e2e    # E2E

# Tests d'un fichier spécifique
docker compose exec backend pytest tests/routes/test_notes.py -v

# Rapport HTML de coverage
# → Ouvrir backend/htmlcov/index.html dans un navigateur
```

### Tests E2E - Scénarios couverts

**32 scénarios testés manuellement et automatiquement** :

#### Authentification & Sécurité (6 scénarios)
1. Login avec credentials valides → Token JWT reçu
2. Login avec credentials invalides → Erreur 401
3. Register avec email valide → Compte créé
4. Register avec email existant → Erreur 409
5. Accès route protégée sans token → Redirection login
6. Token expiré → Erreur 401 et rafraîchissement

#### CRUD Notes (8 scénarios)
7. Création note vide → Erreur 422 "Content required"
8. Création note valide → Note créée et affichée
9. Modification note existante → Mise à jour réussie
10. Suppression note (créateur) → Soft delete appliqué
11. Suppression note (non-créateur) → Erreur 403
12. Marquage note importante → Flag `important=true`
13. Consultation détails note → Informations complètes
14. Tri et filtrage des notes → Ordre correct

#### Assignations (8 scénarios)
15. Assignation note à contact → Création assignment
16. Assignation en doublon → Erreur 409
17. Assignation à contact inexistant → Erreur 404
18. Consultation notes assignées → Visibilité correcte
19. Marquage note lue → `is_read=true`
20. Suppression assignation → Note retirée de la vue
21. Mode sélection multiple → Assignation batch
22. Annulation assignation (Undo) → Suppression dans les 5s

#### Contacts & Collaboration (6 scénarios)
23. Ajout contact avec nickname → Contact créé
24. Recherche utilisateur par username → Résultats filtrés
25. Modification nickname → Mise à jour sauvegardée
26. Suppression contact → Confirmation requise
27. Badge "Mutuel" affiché → Contact réciproque identifié
28. Isolation des contacts → Chaque user voit ses contacts

#### Fonctionnalités avancées (4 scénarios)
29. Brouillon auto-save → Sauvegarde localStorage
30. Restauration brouillon → Message de confirmation
31. Badge "NOUVEAU" sur note non lue → Affichage < 24h
32. Archives (notes orphelines) → Bouton 📦 affiche notes sans assignation

---

## 🛠️ Développement

### Migrations de base de données

```bash
# Créer une migration après modification des modèles
docker compose exec backend flask db migrate -m "Description des changements"

# Appliquer les migrations
docker compose exec backend flask db upgrade

# Revenir en arrière
docker compose exec backend flask db downgrade
```

### Commandes utiles

```bash
# Logs en temps réel
docker compose logs backend -f

# Shell Python interactif dans le conteneur
docker compose exec backend python

# Accès PostgreSQL
docker compose exec db psql -U app -d appdb

# Arrêter les services
docker compose down

# Arrêter et supprimer les volumes (reset complet)
docker compose down -v

# Rebuild complet
docker compose up -d --build --force-recreate
```

### Ajouter une dépendance Python

```bash
# 1. Ajouter la dépendance dans requirements.txt
echo "nouvelle-lib==1.0.0" >> backend/requirements.txt

# 2. Rebuild le conteneur
docker compose up -d --build backend
```

### Variables d'environnement

Créer un fichier `.env` à la racine :

```env
# Flask
FLASK_SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# PostgreSQL
POSTGRES_USER=app
POSTGRES_PASSWORD=app
POSTGRES_DB=appdb
DATABASE_URL=postgresql+psycopg2://app:app@db:5432/appdb
```

---

## 🚢 Déploiement

### Production avec Docker

```bash
# 1. Cloner sur le serveur
git clone https://github.com/Mylliah/mvp-sticky_notes.git
cd mvp-sticky_notes

# 2. Configurer les variables d'environnement
cp .env.example .env
nano .env  # Modifier avec des valeurs de production

# 3. Lancer en production
docker compose -f docker-compose.prod.yml up -d

# 4. Appliquer les migrations
docker compose exec backend flask db upgrade
```

### Checklist avant déploiement

- [ ] Changer `FLASK_SECRET_KEY` et `JWT_SECRET_KEY`
- [ ] Utiliser un mot de passe PostgreSQL fort
- [ ] Configurer CORS si frontend sur un autre domaine
- [ ] Activer HTTPS (reverse proxy Nginx/Traefik)
- [ ] Configurer les backups de base de données
- [ ] Activer le logging en production
- [ ] Configurer un monitoring (Sentry, Datadog, etc.)

---

## 🐛 Bugs connus corrigés

### ✅ Bug d'isolation des notes (CRITIQUE - BUG-001)
**Problème** : GET `/v1/notes` retournait TOUTES les notes de tous les utilisateurs  
**Solution** : Ajout d'un filtre par `creator_id` + inclusion des notes assignées avec JOIN  
**Impact** : Sécurité des données utilisateurs restaurée

### ✅ Assignations en doublon (BUG-002)
**Problème** : Possibilité d'assigner la même note au même contact plusieurs fois  
**Solution** : Contrainte `UNIQUE(note_id, contact_id)` en base + catch erreur 409  
**Impact** : Intégrité des données garantie

### ✅ Notes assignées non visibles (BUG-003)
**Problème** : Un utilisateur ne voyait pas les notes qui lui étaient assignées  
**Solution** : Modification de la requête pour inclure notes créées OU assignées  
**Impact** : Fonctionnalité de collaboration restaurée

### ✅ Fuite d'informations dans panel Info (BUG-003)
**Problème** : Le panel Info affichait toutes les assignations d'une note, même pour les non-concernés  
**Solution** : Filtrage des assignations visibles (créateur ou destinataire uniquement)  
**Impact** : Confidentialité des assignations préservée

### ✅ Tri incorrect des notes reçues (BUG-004)
**Problème** : Nouvelles notes reçues triées par `created_date` au lieu de `assigned_date`  
**Solution** : Tri multi-critères `assigned_date DESC, created_date DESC`  
**Impact** : UX améliorée, nouvelles assignations visibles immédiatement

### ✅ Suppression impossible avec contraintes FK (BUG-006)
**Problème** : Erreur 500 "Foreign key constraint failed" lors de la suppression  
**Solution** : Soft delete uniquement + `ON DELETE SET NULL` sur `action_logs.target_id`  
**Impact** : Fonctionnalité de suppression stabilisée

### ✅ Affichage user_id au lieu du nickname (BUG-008)
**Problème** : Cartes de notes affichaient "de 3" au lieu de "de Laura"  
**Solution** : Appel asynchrone `userService.getUser()` pour récupérer le username  
**Impact** : Interface utilisateur lisible et professionnelle

### ✅ API contacts incompatible avec tests
**Problème** : Tests attendaient `user_id`, API utilisait `contact_username`  
**Solution** : Mise à jour de tous les tests pour utiliser `contact_username`  
**Impact** : Cohérence API/tests assurée

---

## 📝 Changelog

### v1.0.0 (2025-01-27)

#### 🎉 Features
- ✅ API REST complète (7 resources, 40+ endpoints)
- ✅ Authentification JWT avec refresh tokens
- ✅ Gestion collaborative de notes
- ✅ Système de contacts et assignations
- ✅ Logs d'actions traçables
- ✅ Module d'administration complet
- ✅ Frontend HTML/CSS/JS fonctionnel
- ✅ Rate limiting et CORS configurés

#### 🧪 Tests
- ✅ 398 tests (unitaires + intégration + E2E)
- ✅ Coverage 98%
- ✅ 32 scénarios E2E validés manuellement
- ✅ Tests Postman automatisés

#### 🔒 Sécurité
- ✅ Isolation complète des données par utilisateur
- ✅ Hashage bcrypt des mots de passe
- ✅ Validation d'inputs stricte
- ✅ Prévention des doublons et auto-ajouts
- ✅ Protection CSRF et rate limiting
- ✅ Soft delete pour l'intégrité des logs

#### 🏗️ Infrastructure
- ✅ Docker Compose multi-services
- ✅ Migrations Alembic
- ✅ PostgreSQL 15
- ✅ Gunicorn WSGI server
- ✅ Environnement de développement reproductible

---

## 👥 Contributeurs

- **Mylliah** - Développement initial

---

## 📄 Licence

Ce projet est un MVP éducatif.

---

## 🤝 Support

Pour toute question ou problème :
1. Vérifier les [Issues GitHub](https://github.com/Mylliah/mvp-sticky_notes/issues)
2. Consulter les logs : `docker compose logs backend -f`
3. Lancer les tests : `docker compose exec backend pytest tests/ -v`

---

**Made with ❤️ using Flask, PostgreSQL & Docker**
