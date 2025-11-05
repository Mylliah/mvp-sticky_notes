# 📝 MVP Sticky Notes

> **Application de gestion collaborative de notes** - Backend API REST avec Flask, PostgreSQL et JWT

[![Tests](https://img.shields.io/badge/tests-196%20passed-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-99.8%25-brightgreen)](htmlcov/)
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
├── Bcrypt                 # Hashage de mots de passe
└── pytest + pytest-cov    # Tests et coverage

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
│   │       └── action_logs.py    # Logs actions
│   ├── migrations/               # Migrations Alembic
│   ├── tests/                    # Suite de tests
│   │   ├── models/               # 72 tests unitaires
│   │   ├── routes/               # 113 tests d'intégration
│   │   ├── e2e/                  # 6 tests E2E workflows
│   │   └── test_app.py           # 5 tests base app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
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

---

## 🧪 Tests

### Statistiques de tests

```
✅ 196 tests passent à 100%
📊 Coverage : 99.8% (493/494 lignes)
⏱️  Temps d'exécution : ~52 secondes
```

### Détail par catégorie

| Catégorie | Tests | Coverage | Description |
|-----------|-------|----------|-------------|
| **Tests E2E** | 6 | - | Workflows complets utilisateur |
| **Tests unitaires (models)** | 72 | 100% | Tous les modèles |
| **Tests intégration (routes)** | 113 | 100% | Toutes les routes |
| **Tests base app** | 5 | 98% | Health check, JWT handlers |

### Coverage par module

```
Module                     Coverage
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app/__init__.py            98%  (51/52)
app/models/*               100% (130/130)
app/routes/v1/*            100% (312/312)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL                      99.8% (493/494)
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

1. **Collaboration complète** : Alice crée une note, ajoute Bob en contact, lui assigne la note, Bob la consulte
2. **Lifecycle note** : Création → modification → marquage important → terminé → suppression
3. **Assignations multiples** : Manager assigne la même note à 3 membres
4. **Isolation utilisateur** : User1 et User2 ne voient que leurs propres notes
5. **Isolation contacts** : Contacts privés par utilisateur
6. **Gestion d'erreurs** : Auto-ajout, doublons, opérations invalides

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

### ✅ Bug d'isolation des notes (CRITIQUE)
**Problème** : GET `/v1/notes` retournait TOUTES les notes de tous les utilisateurs  
**Solution** : Ajout d'un filtre par `creator_id` + inclusion des notes assignées avec JOIN  
**Impact** : Sécurité des données utilisateurs

### ✅ Notes assignées non visibles
**Problème** : Un utilisateur ne voyait pas les notes qui lui étaient assignées  
**Solution** : Modification de la requête pour inclure notes créées OU assignées

### ✅ API contacts incompatible
**Problème** : Tests attendaient `user_id`, API utilisait `contact_username`  
**Solution** : Mise à jour de tous les tests pour utiliser `contact_username`

---

## 📝 Changelog

### v1.0.0 (2025-10-16)

#### 🎉 Features
- ✅ API REST complète (6 resources, 30+ endpoints)
- ✅ Authentification JWT
- ✅ Gestion collaborative de notes
- ✅ Système de contacts et assignations
- ✅ Logs d'actions traçables

#### 🧪 Tests
- ✅ 196 tests (unitaires + intégration + E2E)
- ✅ Coverage 99.8%
- ✅ Tests E2E de workflows réels

#### 🔒 Sécurité
- ✅ Isolation complète des données par utilisateur
- ✅ Hashage bcrypt des mots de passe
- ✅ Validation d'inputs
- ✅ Prévention des doublons et auto-ajouts

#### 🏗️ Infrastructure
- ✅ Docker Compose multi-services
- ✅ Migrations Alembic
- ✅ PostgreSQL 15

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
