# 📝 MVP Sticky Notes - Collaborative Note Management

> **Application web moderne de gestion collaborative de notes** avec **Backend Flask REST API** + **Frontend React TypeScript**

[![Tests](https://img.shields.io/badge/tests-398%20passed-success)](backend/tests/)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](backend/htmlcov/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/react-18-61dafb)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0-3178c6)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)](https://www.postgresql.org/)

---

## 🎯 Objectif du projet

Ce **MVP Sticky Notes** est un projet de portfolio développé dans le cadre du programme Holberton School. Il démontre la capacité à :
- Construire une **API REST complète** avec Flask et SQLAlchemy
- Développer un **frontend moderne** avec React et TypeScript
- Implémenter une **authentification JWT sécurisée**
- Gérer une **architecture Docker multi-conteneurs**
- Appliquer la **méthodologie Agile** sur 4 sprints hebdomadaires
- Atteindre **98% de couverture de tests** (398 tests automatisés)

L'application permet aux utilisateurs de :
- ✅ **Créer et gérer des notes** collaboratives
- ✅ **Assigner des notes** à d'autres utilisateurs (contacts)
- ✅ **Filtrer et rechercher** dans leurs notes
- ✅ **Collaborer** via un système de contacts mutuels
- ✅ **Suivre l'activité** avec un système de logs et badges

---

## ✨ Fonctionnalités principales

### 🔐 Authentification
- Système de connexion sécurisé par **JWT**
- Enregistrement de nouveaux utilisateurs
- Hashage des mots de passe avec **bcrypt**
- Gestion de session avec **localStorage**
- Auto-déconnexion sur expiration du token

### 📌 Gestion des Notes
- **CRUD complet** : Créer, lire, modifier, supprimer
- **Affichage en vignettes** (cards) responsives
- **Badges visuels** :
  - 🔴 Important (étoile)
  - 🔵 NOUVEAU (notes < 24h non lues)
  - 📊 Statut (En cours, Terminé)
  - 👤 Créateur/Destinataires
- **Auto-save** des brouillons (localStorage, 3 secondes)
- **Soft delete** (suppression traçable)

### 👥 Contacts & Collaboration
- Recherche d'utilisateurs par **username**
- Ajout de contacts avec **nicknames personnalisés**
- Badge **"Mutuel"** si contact réciproque
- Liste des **utilisateurs assignables**
- Filtrage par contact (clic sur badge)

### 📤 Assignations
- **Drag & Drop** pour assigner rapidement
- **Mode sélection multiple** (batch assignment)
- Toast de confirmation avec **bouton Undo** (5 secondes)
- Prévention des **doublons**
- Notifications visuelles **"NOUVEAU"**

### 🔍 Filtres & Recherche
- **Barre de recherche** avec debouncing (300ms)
- **5 filtres cliquables** :
  - ❗ Important
  - 📥 Reçus
  - 📤 Émis
  - ⏳ En cours
  - ✅ Terminé
- **Tri par date** (ascendant/descendant)
- **Tri par importance**

### 🎁 Fonctionnalités Bonus
- 📦 **Archives** (notes orphelines)
- 📊 **Panel détails** avec historique
- 🔄 **Scroll infini** (pagination automatique)
- 👨‍💼 **Module admin** complet (`/admin/*`)
- 📝 **Traçabilité** via ActionLog
- ⚡ **Skeleton loaders** pendant chargement

---

## 🏗️ Architecture

### Stack Technologique

| Couche | Technologies | Version |
|--------|-------------|---------|
| **Backend** | Flask + SQLAlchemy + Flask-RESTx | 3.0.x |
| **Database** | PostgreSQL | 15 |
| **Frontend** | React + TypeScript + Vite | 18.x / 5.x |
| **Auth** | Flask-JWT-Extended + bcrypt | 4.x |
| **Tests** | pytest + pytest-cov | 8.0.x |
| **DevOps** | Docker + Docker Compose | 24.x |

### Architecture Multi-Conteneurs

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐   ┌──────────────┐   │
│  │   Frontend   │   │   Backend    │   │
│  │  React:3000  │◄──┤  Flask:5000  │   │
│  │  TypeScript  │   │  REST API    │   │
│  └──────────────┘   └──────┬───────┘   │
│                            │           │
│                            ▼           │
│                     ┌──────────────┐   │
│                     │  PostgreSQL  │   │
│                     │   Port:5432  │   │
│                     └──────────────┘   │
│                                         │
│                     ┌──────────────┐   │
│                     │   Adminer    │   │
│                     │  Port:8080   │   │
│                     └──────────────┘   │
└─────────────────────────────────────────┘
```

### Structure du Projet

```
mvp-sticky_notes/
├── 📁 backend/                   # API Flask
│   ├── 📁 app/
│   │   ├── __init__.py          # Factory pattern
│   │   ├── decorators.py        # @jwt_required custom
│   │   ├── 📁 models/           # 5 modèles SQLAlchemy
│   │   │   ├── user.py          # 100% coverage
│   │   │   ├── note.py          # 100% coverage
│   │   │   ├── contact.py       # 100% coverage
│   │   │   ├── assignment.py    # 100% coverage
│   │   │   └── action_log.py    # 100% coverage
│   │   └── 📁 routes/v1/        # 7 modules de routes
│   │       ├── auth.py          # Authentification
│   │       ├── notes.py         # CRUD notes (50 endpoints)
│   │       ├── contacts.py      # Gestion contacts
│   │       ├── assignments.py   # Assignations
│   │       ├── users.py         # Gestion utilisateurs
│   │       ├── admin.py         # Module admin
│   │       └── action_logs.py   # Logs traçabilité
│   ├── 📁 migrations/           # Alembic
│   ├── 📁 tests/                # 398 tests pytest
│   │   ├── 📁 e2e/              # 10 tests E2E
│   │   ├── 📁 models/           # 70 tests modèles
│   │   └── 📁 routes/           # 313 tests routes
│   ├── 📁 htmlcov/              # Coverage report
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wsgi.py
│
├── 📁 frontend/                  # Application React
│   ├── 📁 src/
│   │   ├── App.tsx              # Composant racine
│   │   ├── 📁 components/       # 13 composants React
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── NotesPage.tsx    # Dashboard principal
│   │   │   ├── NoteCard.tsx     # Carte de note
│   │   │   ├── ContactTabs.tsx  # Panel contacts
│   │   │   ├── NoteDetailPanel.tsx
│   │   │   ├── CreateNoteModal.tsx
│   │   │   └── ...
│   │   ├── 📁 services/         # 5 services API
│   │   │   ├── api.ts           # Axios config
│   │   │   ├── authService.ts
│   │   │   ├── notesService.ts
│   │   │   ├── contactsService.ts
│   │   │   └── assignmentsService.ts
│   │   └── 📁 types/            # TypeScript interfaces
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── docker-compose.yml            # Orchestration
├── README.md                     # Ce fichier
└── 📁 screenshots/               # Captures d'écran
```

---

## 🚀 Installation & Lancement

### Prérequis

- **Docker** 24.x+ (avec Docker Compose V2)
- **Git** 2.x+
- **Ports libres** : 3000 (frontend), 5000 (backend), 5432 (postgres), 8080 (adminer)

> **Note** : Aucune installation Python/Node.js requise, tout fonctionne via Docker ! 🐳

### 1️⃣ Cloner le Repository

```bash
git clone https://github.com/Mylliah/mvp-sticky_notes.git
cd mvp-sticky_notes
```

### 2️⃣ Lancer l'Application

```bash
# Démarrer tous les conteneurs en arrière-plan
docker compose up -d

# Vérifier que les conteneurs sont bien lancés
docker compose ps
```

**Résultat attendu** :
```
NAME                          STATUS      PORTS
mvp-sticky_notes-backend-1    Up          0.0.0.0:5000->5000/tcp
mvp-sticky_notes-frontend-1   Up          0.0.0.0:3000->3000/tcp
mvp-sticky_notes-db-1         Up (healthy) 0.0.0.0:5432->5432/tcp
mvp-sticky_notes-adminer-1    Up          0.0.0.0:8080->8080/tcp
```

### 3️⃣ Initialiser la Base de Données

```bash
# Appliquer les migrations
docker compose exec backend flask db upgrade

# (Optionnel) Charger des données de test (accessible sur branche Test)
./reset_and_seed.sh
```

> **Note** : Les scripts de seed créent des utilisateurs et notes de test. Ces données ne sont **pas** incluses dans le repository Git.

### 4️⃣ Accéder à l'Application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3001 | Interface web React |
| **Backend API** | http://localhost:5000/v1 | API REST (Swagger) |
| **Swagger UI** | http://localhost:5000/api/docs | Documentation interactive |
| **Adminer** | http://localhost:8080 | Interface PostgreSQL |

---

## 🔑 Comptes de Test

⚠️ **IMPORTANT : Comptes de développement uniquement**  
Ces comptes sont fournis pour faciliter les tests en local. **NE JAMAIS utiliser ces credentials en production !**

### 👤 Utilisateurs Standard

| Email | Mot de passe | Rôle | Description |
|-------|--------------|------|-------------|
| `testuser1@test.com` | `SecurePass123!` | User | Utilisateur avec données de test |
| `saido@test.com` | `azeqsdwxc` | User | Utilisateur "Saido" |

> **💡 Note** : Tous les comptes sont des utilisateurs standards. Aucun compte admin n'est configuré pour l'instant.  
> **🔒 Sécurité** : Ces comptes existent uniquement dans votre base de données locale. Lors du clonage du repo, la base de données sera vide.

---

## 📖 Utilisation de l'Application

### Connexion via le formulaire (`/login`)

1. Aller sur http://localhost:3001
2. Utiliser l'un des comptes de test ci-dessus
3. Le token JWT est stocké automatiquement dans `localStorage`
4. Redirection vers le **Dashboard**

> 💡 **Astuce** : Les comptes de test sont affichés directement sur la page de connexion pour faciliter vos tests !

### Navigation dans le Dashboard (`/notes`)

#### Fonctionnalités disponibles :

**🗂️ Sidebar gauche**
- ➕ **Nouveau** : Créer une nouvelle note
- 📄 **Documents** : Toutes les notes
- 📦 **Archives** : Notes orphelines (sans assignation)
- 👥 **Contacts** : Gérer les contacts
- 👤 **Profil** : Modifier le profil
- ⚙️ **Paramètres** : Configuration

**🔍 Barre de recherche**
- Recherche en temps réel avec **debouncing 300ms**
- Bouton **clear** (✕) pour réinitialiser
- Recherche par contenu de note

**🏷️ Filtres cliquables**
- **Important** : Notes marquées importantes
- **En cours** : Notes avec statut `en_cours`
- **Terminé** : Notes avec statut `termine`
- **Reçus** : Notes où je suis destinataire
- **Émis** : Notes que j'ai créées

**📊 Tri**
- **Toggle date** : ↑ Ascendant / ↓ Descendant
- **Par importance** : Notes importantes en premier

**📌 Panel Contacts (droite)**
- **Notes à moi-même** : Auto-assignations
- **Liste des contacts** avec nicknames
- **Clic sur contact** → Filtre les notes liées

### Créer une Note

1. Cliquer sur **"+ Nouveau"** (sidebar)
2. Remplir le formulaire :
   - **Contenu** (obligatoire)
   - **Marquer comme important** (optionnel)
   - **Statut** : En cours / Terminé
3. **Auto-save** après 3 secondes d'inactivité
4. **Brouillon sauvegardé** dans localStorage
5. Cliquer **"Créer"** ou **✕ Fermer**

### Assigner une Note

#### Méthode 1 : Drag & Drop
1. **Glisser** une note depuis le dashboard
2. **Déposer** sur un contact dans le panel droit
3. **Toast de confirmation** avec bouton **"Annuler"** (5s)

#### Méthode 2 : Menu contextuel
1. Cliquer sur **"⋮"** dans la NoteCard
2. Sélectionner **"Assigner à..."**
3. Choisir un contact dans la liste

#### Méthode 3 : Mode sélection multiple
1. Activer le **mode sélection** (bouton en haut)
2. **Cocher** 2+ notes
3. Cliquer **"Assigner"**
4. Choisir le contact cible
5. **Assignation batch** en une seule requête

### Voir les Détails d'une Note

1. Cliquer sur une **NoteCard**
2. **Panel détails** s'ouvre à droite
3. Affiche :
   - 📅 Dates (création, modification, lecture)
   - 👥 Liste des assignations
   - 📝 Historique des actions
   - 🗑️ Info suppression (si applicable)

### Gérer les Contacts

1. Aller dans **Contacts** (sidebar)
2. **Rechercher** un utilisateur par username
3. **Ajouter** avec un nickname personnalisé
4. Badge **"Mutuel"** si contact réciproque
5. **Modifier** le nickname
6. **Supprimer** (avec confirmation)

### Filtrer par Contact

1. Dans le **dashboard**, cliquer sur un **badge contact** (ex: "de MaoMao")
2. Seules les notes liées à ce contact s'affichent
3. **Clic à nouveau** pour désélectionner

---

## 📡 API Documentation

### Base URL
```
http://localhost:5000/v1
```

### Documentation Interactive (Swagger)
```
http://localhost:5000/api/docs
```

### Endpoints Principaux

#### 🔐 Authentification (`/auth`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/register` | Créer un compte |
| POST | `/auth/login` | Se connecter (retourne JWT) |
| GET | `/auth/me` | Obtenir l'utilisateur connecté |
| POST | `/auth/logout` | Se déconnecter |

**Exemple : Login**
```bash
curl -X POST http://localhost:5000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser1@test.com",
    "password": "SecurePass123!"
  }'
```

**Réponse** :
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "testuser1",
    "email": "testuser1@test.com"
  }
}
```

#### 📌 Notes (`/notes`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/notes` | Lister mes notes (+ filtres) |
| POST | `/notes` | Créer une note |
| GET | `/notes/:id` | Détails d'une note |
| PATCH | `/notes/:id` | Modifier une note |
| DELETE | `/notes/:id` | Supprimer une note (soft delete) |
| GET | `/notes/search?q=...` | Rechercher dans les notes |

**Paramètres de filtrage** :
- `?important=true` : Notes importantes
- `?status=en_cours` : Par statut
- `?filter=received` : Notes reçues
- `?filter=sent` : Notes émises
- `?sort=date_asc` : Tri par date
- `?page=1&per_page=20` : Pagination

#### 👥 Contacts (`/contacts`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/contacts` | Mes contacts |
| POST | `/contacts` | Ajouter un contact |
| PATCH | `/contacts/:id` | Modifier nickname |
| DELETE | `/contacts/:id` | Supprimer un contact |
| GET | `/contacts/:id/notes` | Notes liées au contact |

#### 📤 Assignations (`/assignments`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/assignments` | Mes assignations |
| POST | `/assignments` | Assigner une note |
| PATCH | `/assignments/:id` | Modifier assignation |
| DELETE | `/assignments/:id` | Supprimer assignation |
| PATCH | `/assignments/:id/priority` | Toggle priorité ⭐ |
| PATCH | `/assignments/:id/status` | Changer statut |

### Authentication JWT

Toutes les routes (sauf `/auth/login` et `/auth/register`) nécessitent un **token JWT**.

**Header requis** :
```
Authorization: Bearer <votre_token_jwt>
```

**Exemple avec cURL** :
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X GET http://localhost:5000/v1/notes \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🧪 Tests

### Exécuter Tous les Tests

```bash
# Lancer les 398 tests pytest
docker compose exec backend pytest

# Avec coverage détaillé
docker compose exec backend pytest --cov=app --cov-report=term-missing
```

**Résultat attendu** :
```
================ 398 passed in 130.82s (0:02:10) =================

---------- coverage: platform linux, python 3.11.14-final-0 ----------
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
app/__init__.py                   58      1    98%   111
app/decorators.py                 18      0   100%
app/models/__init__.py             6      0   100%
app/models/action_log.py          15      0   100%
app/models/assignment.py          20      0   100%
app/models/contact.py             20      0   100%
app/models/note.py                34      0   100%
app/models/user.py                51      1    98%   57
app/routes/v1/__init__.py          6      0   100%
app/routes/v1/action_logs.py      35      0   100%
app/routes/v1/admin.py           144      0   100%
app/routes/v1/assignments.py     154      1    99%   129
app/routes/v1/auth.py             61      1    98%   31
app/routes/v1/contacts.py        131      2    98%   294, 296
app/routes/v1/notes.py           205      6    97%   158, 173, 208...
app/routes/v1/users.py            78     12    85%   19-21, 73-93
------------------------------------------------------------
TOTAL                           1036     24    98%
```

### Tests par Catégorie

```bash
# Tests E2E uniquement (10 tests)
docker compose exec backend pytest tests/e2e/

# Tests des modèles (70 tests)
docker compose exec backend pytest tests/models/

# Tests des routes (313 tests)
docker compose exec backend pytest tests/routes/

# Test spécifique
docker compose exec backend pytest tests/routes/test_notes.py -v
```

### Générer le Rapport HTML de Coverage

```bash
docker compose exec backend pytest --cov=app --cov-report=html

# Ouvrir le rapport
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
```

### Métriques de Tests

| Métrique | Valeur | Détail |
|----------|--------|--------|
| **Tests automatisés** | 398 | 100% passed |
| **Coverage backend** | 98% | 1036 statements, 24 missed |
| **Tests E2E** | 10 | Workflows complets |
| **Tests modèles** | 70 | 100% coverage |
| **Tests routes** | 313 | 97-100% coverage |
| **Durée totale** | 130.82s | ~2min 10s |

---

## 🛠️ Développement

### Structure des Branches Git

```
main            → Version stable (production)
dev             → Intégration continue
backend         → Développement backend
frontend        → Développement frontend
test            → Tests et QA
```

### Workflow de Développement

```bash
# 1. Créer une branche feature
git checkout -b feature/ma-nouvelle-fonctionnalite

# 2. Développer et tester
docker compose up -d
# ... faire vos modifications ...

# 3. Tester localement
docker compose exec backend pytest

# 4. Commit et push
git add .
git commit -m "feat: ajouter nouvelle fonctionnalité"
git push origin feature/ma-nouvelle-fonctionnalite

# 5. Créer une Pull Request sur GitHub
```

### Commandes Utiles

#### Docker Compose

```bash
# Démarrer les services
docker compose up -d

# Arrêter les services
docker compose down

# Voir les logs
docker compose logs -f backend
docker compose logs -f frontend

# Rebuild après modification
docker compose up -d --build

# Accéder au shell d'un conteneur
docker compose exec backend bash
docker compose exec frontend sh

# Réinitialiser complètement
docker compose down -v  # ⚠️ Supprime les volumes (données perdues)
docker compose up -d --build
```

#### Base de Données

```bash
# Créer une migration
docker compose exec backend flask db migrate -m "Description"

# Appliquer les migrations
docker compose exec backend flask db upgrade

# Revenir en arrière
docker compose exec backend flask db downgrade

# Réinitialiser la DB
docker compose exec backend python reset_db.sh

# Charger des données de test
docker compose exec backend python seed_data.py
```

#### Backend

```bash
# Shell Python interactif
docker compose exec backend python

# Exécuter un script
docker compose exec backend python mon_script.py

# Installer une nouvelle dépendance
docker compose exec backend pip install nouvelle-lib
# Puis mettre à jour requirements.txt
docker compose exec backend pip freeze > requirements.txt
```

#### Frontend

```bash
# Installer une nouvelle dépendance
docker compose exec frontend npm install nouvelle-lib

# Builder pour production
docker compose exec frontend npm run build

# Linter
docker compose exec frontend npm run lint
```

---

## 🐛 Dépannage (Troubleshooting)

### Problème : Port déjà utilisé

**Erreur** :
```
Error starting userland proxy: listen tcp4 0.0.0.0:5000: bind: address already in use
```

**Solution** :
```bash
# Trouver le processus utilisant le port
sudo lsof -i :5000

# Tuer le processus
kill -9 <PID>

# Ou changer le port dans docker-compose.yml
```

### Problème : Base de données non initialisée

**Erreur** :
```
sqlalchemy.exc.ProgrammingError: relation "user" does not exist
```

**Solution** :
```bash
# Appliquer les migrations
docker compose exec backend flask db upgrade

# Si ça ne fonctionne pas, reset complet
docker compose down -v
docker compose up -d
docker compose exec backend flask db upgrade
```

### Problème : Frontend ne se connecte pas au backend

**Erreur console** :
```
Access to XMLHttpRequest at 'http://localhost:5000' from origin 'http://localhost:3001' 
has been blocked by CORS policy
```

**Solution** :
- Vérifier que CORS est configuré dans `backend/app/__init__.py`
- Redémarrer les conteneurs : `docker compose restart`

### Problème : Erreur TypeScript dans le Frontend

**Erreur console** :
```
Uncaught TypeError: Cannot read properties of undefined (reading 'username')
at ContactTabs.tsx:88:33
```

**Solution** :
- Vérifier que l'objet existe avant d'accéder à ses propriétés
- Ajouter des vérifications null-safe : `contact?.username`
- Voir les logs backend pour vérifier que l'API retourne les bonnes données

### Logs et Debugging

```bash
# Logs backend en temps réel
docker compose logs -f backend --tail=50

# Logs frontend
docker compose logs -f frontend --tail=50

# Logs PostgreSQL
docker compose logs -f db --tail=50

# Tous les logs
docker compose logs -f
```

---

## 🚀 Déploiement (Production)

### Variables d'Environnement

⚠️ **Important** : Ne jamais commit de vraies clés secrètes dans Git !

Créer un fichier `.env` à la racine (voir `.env.example` pour référence) :

```env
# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=CHANGEZ_CETTE_CLE_SECRETE_PRODUCTION
JWT_SECRET_KEY=CHANGEZ_CETTE_CLE_JWT_PRODUCTION

# Database PostgreSQL
DATABASE_URL=postgresql://user:password@db:5432/sticky_notes_prod
POSTGRES_USER=votre_utilisateur_db
POSTGRES_PASSWORD=CHANGEZ_CE_MOT_DE_PASSE
POSTGRES_DB=sticky_notes_prod

# Frontend
VITE_API_URL=https://api.votre-domaine.com/v1
```

**🔐 Générer des secrets sécurisés** :
```bash
# Générer une clé aléatoire forte (32 bytes = 64 caractères hex)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Build Production

```bash
# Backend
docker compose -f docker-compose.prod.yml build backend

# Frontend
docker compose -f docker-compose.prod.yml build frontend

# Démarrer en production
docker compose -f docker-compose.prod.yml up -d
```

### Checklist Sécurité

- [ ] **Générer** de nouvelles clés aléatoires pour `FLASK_SECRET_KEY` et `JWT_SECRET_KEY`
- [ ] **Changer** le mot de passe PostgreSQL par défaut (`POSTGRES_PASSWORD`)
- [ ] **Créer** un fichier `.env` (jamais commité dans Git, déjà dans `.gitignore`)
- [ ] Activer **HTTPS** (certificat SSL/TLS)
- [ ] Désactiver **Swagger** en production (`FLASK_ENV=production`)
- [ ] Configurer un **reverse proxy** (nginx)
- [ ] Limiter les **requêtes** (rate limiting)
- [ ] Activer les **logs de sécurité**
- [ ] **Backup** automatique de la base de données
- [ ] Utiliser des **variables d'environnement** sur la plateforme d'hébergement (pas de `.env` en production)

---

## 📊 Métriques du Projet

| Métrique | Valeur | Détail |
|----------|--------|--------|
| **Durée développement** | 4 semaines | Sprints Agile |
| **Lignes de code** | ~8000 lignes | Backend 5000 + Frontend 3000 |
| **Commits Git** | 150+ commits | GitHub |
| **Endpoints API** | 50 routes | REST documentées |
| **Tests automatisés** | 398 tests | 98% coverage |
| **Bugs résolus** | 12 bugs critiques | Dont 3 failles sécurité |
| **Performance API** | < 150ms | Temps de réponse moyen |
| **Compatibilité** | Chrome, Firefox, Safari, Edge | 118+ |

---

## 📸 Captures d'écran

> **Note** : Les screenshots illustrent les fonctionnalités principales de l'application

### 1. Page de Connexion
![Page de connexion avec comptes de test](screenshots/01_login_page_comptes_test.png)

**Fonctionnalités visibles** :
- ✅ Interface moderne et épurée
- ✅ Formulaire email/mot de passe
- ✅ Comptes de test affichés directement (💡 pratique pour démo)
- ✅ Lien vers inscription
- ✅ Design responsive

### 2. Dashboard "Notes à moi-même"
![Dashboard filtré sur notes à moi-même](screenshots/02_dashboard_notes_a_moi_meme.png)

**Fonctionnalités visibles** :
- ✅ Badge "NOUVEAU" bleu sur note non lue < 24h
- ✅ Badge rouge "1" indiquant notes non lues
- ✅ Grille de notes responsive
- ✅ Badges de statut ("de Moi", "à Moi")
- ✅ Filtres cliquables (Important, En cours, Terminé, Reçus, Émis)
- ✅ Tri par date avec toggle
- ✅ Barre de recherche
- ✅ Panel contacts à droite (Notes à moi-même, MaoMao, testuser1_updated)
- ✅ Sidebar gauche avec navigation

### 3. Vue "Toutes mes notes"
![Dashboard complet avec toutes les notes](screenshots/03_toutes_mes_notes_vue_complete.png)

**Fonctionnalités visibles** :
- ✅ Affichage multi-contact (notes de/à différents utilisateurs)
- ✅ Code couleur des notes (bleu clair, jaune crème)
- ✅ Badges multiples :
  - ❗ Important (trait rouge à gauche)
  - ✅ Terminé (icône checkmark vert)
  - 👥 Assignations multiples ("à Moi, testuser1_updated et MaoMao")
- ✅ Boutons d'action (Sélection, Dark mode, Déconnexion)
- ✅ Indicateur de notes non lues ("1" dans le titre)

### 4. Modal Détails de Note
![Détails complets d'une note avec informations](screenshots/04_modal_details_note_informations.png)

**Fonctionnalités visibles** :
- ✅ Toast de confirmation "Note sauvegardée !"
- ✅ Boutons d'action rapide (Important, Calendrier, Info, Supprimer)
- ✅ Éditeur de contenu (27/5000 caractères)
- ✅ Section "Informations de la note" :
  - 📅 Date de création
  - 📅 Date de modification
  - 👤 Créateur
  - 👥 Assignations (1)
- ✅ Auto-save fonctionnel
- ✅ Bouton fermer (×)


---

## 🤝 Contribution

Ce projet est un portfolio personnel développé dans le cadre du programme Holberton School.

Les contributions ne sont pas acceptées actuellement, mais les suggestions sont les bienvenues.

---

## 📝 Licence

Ce projet est développé dans un cadre pédagogique (Holberton School Portfolio Project).

Tous droits réservés © 2025 Mylliah

---

## 👨‍💻 Auteur

**Mylliah**
- GitHub : [@Mylliah](https://github.com/Mylliah)
- Repository : [mvp-sticky_notes](https://github.com/Mylliah/mvp-sticky_notes)

---

**Projet développé avec ❤️ en 4 semaines - Octobre 2025**
