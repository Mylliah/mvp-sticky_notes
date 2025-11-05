# 🎭 Rétrospective par rôle Agile

**Projet** : MVP Sticky Notes  
**Durée** : 4 semaines (Octobre 2025)  
**Contexte** : Développement individuel avec rôles Agile simulés

---

> **Note méthodologique** : Bien que le projet ait été mené individuellement, cette rétrospective est structurée selon les rôles Agile classiques pour illustrer la compréhension des responsabilités de chaque fonction dans un contexte d'équipe. Cette approche démontre une vision complète du cycle de développement logiciel.

---

## 👔 **Project Manager (PM)**

### Responsabilités assumées
- Planification des 4 sprints hebdomadaires
- Définition des priorités MoSCoW (Must/Should/Could/Won't)
- Suivi de l'avancement via Trello
- Gestion des risques et ajustements de planning
- Communication avec les "stakeholders" (auto-évaluation)

### ✅ Réussites
- **Planification claire** : User stories bien définies dès le Stage 3, backlog structuré
- **Adaptation Agile** : Ajustement du Sprint 1 après difficultés Docker sans compromettre le MVP
- **Priorisation efficace** : Décision de prioriser backend robuste avant frontend → choix validé par les résultats (98% coverage)
- **Documentation continue** : README, ROUTES_REFERENCE, rapports de stage tenus à jour en parallèle du développement
- **Métriques de suivi** : Utilisation de Trello avec colonnes (To Do, In Progress, QA, Done) et labels par rôle

### ❌ Difficultés rencontrées
- **Sous-estimation Docker** : Planification initiale ne prévoyait pas 1 semaine d'apprentissage environnement
- **Manque de buffer** : Peu de marge pour les imprévus (conflits Git, bugs critiques)
- **Frontend tardif** : Intégration front reportée au Sprint 4 → peu de temps pour UI/UX avancée

### 📚 Apprentissages clés
- Toujours prévoir **20-30% de buffer** pour les imprévus techniques
- Commencer **frontend minimal dès Sprint 1** pour valider l'intégration continue
- Utiliser des **burn-down charts** pour visualiser la vélocité réelle
- **Rétrospectives hebdomadaires** essentielles pour ajuster le tir rapidement

### 🔮 Améliorations pour prochain projet
- Créer un **MVP walking skeleton** dès J1 (backend + frontend + DB connectés, même vide)
- Prévoir des **sprints de 2 semaines** (au lieu de 1) pour plus de stabilité
- Implémenter un **daily stand-up** (même solo) pour structurer les journées
- Utiliser **GitHub Projects** en complément de Trello pour lier issues et code

---

## 🌳 **Source Control Manager (SCM)**

### Responsabilités assumées
- Gestion de la stratégie Git (branches, merges, tags)
- Maintien de l'intégrité du repository GitHub
- Résolution des conflits de merge
- Revue de code (auto-revue avant merge sur `main`)
- Documentation du workflow Git

### ✅ Réussites
- **Architecture de branches claire** : `main`, `dev`, `backend`, `frontend`, `test`
- **150+ commits** bien structurés avec messages descriptifs (feat, fix, docs, refactor)
- **Protection de la branche main** : Aucun push direct, toujours merge après validation
- **Sauvegarde automatique** : Scripts de backup réguliers avant merges risqués
- **Tags sémantiques** : Utilisation de tags pour marquer les fins de sprint (v0.1.0-sprint1, etc.)

### ❌ Difficultés rencontrées
- **Conflits Git fréquents** : Travail simultané sur `backend` et `frontend` → merges complexes
- **Perte de commits** : 2 incidents de conflits mal résolus → perte de travail (récupéré via reflog)
- **Stratégie feature branching abandonnée** : Trop complexe en solo → retour à branches longues (backend, frontend)
- **Manque de CI/CD** : Tests non lancés automatiquement → risque de régressions non détectées

### 📚 Apprentissages clés
- Utiliser `git stash` et `git worktree` pour basculer entre branches sans commit
- Toujours faire `git pull --rebase` avant un merge pour historique linéaire
- `git reflog` est un **sauveur** en cas de perte accidentelle
- Créer des **scripts de merge** pour automatiser les tâches répétitives
- GitHub Actions pour **CI/CD gratuit** (tests automatiques à chaque push)

### 🔮 Améliorations pour prochain projet
- **Feature branching systématique** : `feature/auth-jwt`, `fix/notes-isolation`
- **Pull Requests obligatoires** (même solo) pour forcer la revue de code
- **GitHub Actions CI/CD** :
  ```yaml
  name: Tests automatiques
  on: [push, pull_request]
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - run: docker compose up -d
        - run: docker compose exec backend pytest --cov=app
  ```
- **Pre-commit hooks** : Linter automatique avant chaque commit (black, flake8, eslint)
- **Conventional Commits** : Format strict des messages (feat:, fix:, docs:, etc.)

---

## 🔍 **Quality Assurance (QA)**

### Responsabilités assumées
- Définition des critères d'acceptation (Definition of Done)
- Rédaction des plans de test
- Exécution des tests manuels (E2E, UI/UX)
- Rédaction et suivi des rapports de bugs
- Validation des corrections avant merge

### ✅ Réussites
- **398 tests automatisés** : Unitaires (70), intégration (318), E2E (10)
- **98% de coverage backend** : Seulement 24 lignes non testées sur 1036
- **12 bugs critiques détectés et corrigés** : Dont 3 failles de sécurité majeures (BUG-001, BUG-003, BUG-012)
- **Tests de régression** : Chaque bug corrigé → test ajouté pour éviter réapparition
- **Documentation QA complète** : GUIDE_TEST_ASSIGNATION.md, TEST_RESULTS.md

### ❌ Difficultés rencontrées
- **Charge QA sous-estimée** : Tests manuels UI/UX très chronophages (32 scénarios × 2h = 64h)
- **Environnement de test instable** : Docker parfois lent → tests flaky
- **Manque d'automatisation UI** : Pas de Selenium/Cypress → tests manuels uniquement
- **Dette technique tests front** : Backend très testé (98%) vs frontend peu testé

### 📚 Apprentissages clés
- **Tests = confiance** : 98% coverage permet de refactorer sans peur
- **TDD (Test-Driven Development)** : Écrire le test AVANT le code → gagne du temps
- **Tests E2E critiques** : Détectent les bugs d'intégration que les tests unitaires ratent
- **Fixtures pytest** : Réutilisation de données de test → gain de temps énorme
- **Postman collections** : Sauvegarde des requêtes → rejouables en 1 clic

### 🔮 Améliorations pour prochain projet
- **Intégrer Cypress** pour tests E2E automatisés frontend (drag & drop, formulaires)
- **Prévoir 30% du temps pour QA** (actuellement ~20% seulement)
- **Environnement de staging** séparé pour tests sans polluer la DB de dev
- **Tests de charge** : Locust ou JMeter pour valider performance (100+ utilisateurs simultanés)
- **Tests d'accessibilité** : Lighthouse CI, axe-core pour WCAG compliance
- **Mutation testing** : Vérifier la qualité des tests (ex: mutmut, Stryker)

---

## 💻 **Développeur/DBA (Dev/DBA)**

### Responsabilités assumées
- Conception et implémentation du schéma de base de données
- Développement backend (Flask, SQLAlchemy, JWT)
- Développement frontend (React, TypeScript)
- Gestion des migrations Alembic
- Optimisation des requêtes SQL
- Sécurité (authentification, autorisation, validation)

### ✅ Réussites Backend
- **Architecture 2 couches** : Models (données) + Routes (controller + logique métier) bien organisés
- **5 modèles SQLAlchemy** : User, Note, Contact, Assignment, ActionLog avec relations complexes
- **50 endpoints API REST** : Tous documentés avec Swagger/OpenAPI
- **Sécurité robuste** : JWT + rate limiting + CORS + validation des entrées + isolation des données
- **Performance** : Temps de réponse < 150ms grâce à requêtes SQL optimisées (JOINs, eager loading)
- **Migrations propres** : 15 migrations Alembic sans rollback nécessaire

### ✅ Réussites Frontend
- **13 composants React TypeScript** : Architecture modulaire et réutilisable
- **Gestion d'état propre** : useState/useEffect sans bibliothèque externe (Redux non nécessaire)
- **UX soignée** : Drag & drop, undo, brouillon auto-save, debouncing, toasts
- **Types TypeScript** : Interfaces bien définies → autocomplétion IDE + détection erreurs compile-time
- **Services API** : Couche d'abstraction propre (authService, notesService, etc.)

### ❌ Difficultés rencontrées
- **Courbe d'apprentissage Docker** : 1 semaine perdue pour maîtriser images, volumes, networks
- **Conflits ORM** : Sessions SQLAlchemy mal gérées → erreurs "DetachedInstanceError"
- **CORS bloquant** : Erreurs "Failed to fetch" → ajout tardif de flask-cors
- **Gestion des relations N-N** : Table `assignments` avec colonnes supplémentaires (priority, status) → complexité accrue
- **TypeScript strictNullChecks** : Beaucoup d'erreurs "Object is possibly 'null'" → ajout de guards partout

### 📚 Apprentissages clés Backend
- **SQLAlchemy relationships** : `lazy='joined'` vs `lazy='select'` → impact performance majeur
- **Flask-RESTx namespaces** : Organisation des routes par ressource → code plus maintenable
- **JWT best practices** : Expiration 1h, refresh tokens, blacklist pour logout
- **Soft delete** : `deleted_at` + `deleted_by` au lieu de DELETE SQL → traçabilité complète
- **ActionLog pattern** : Log AVANT modification → permet audit et rollback

### 📚 Apprentissages clés Frontend
- **React Hooks** : useEffect avec dépendances bien gérées → évite boucles infinies
- **TypeScript generics** : Type-safe services API (`fetchData<T>(url): Promise<T>`)
- **Debouncing custom hook** : `useDebounce(value, delay)` réutilisable
- **localStorage avec expiration** : Brouillon auto-save avec TTL 24h
- **Drag & Drop HTML5** : `onDragStart`, `onDragOver`, `onDrop` + feedback visuel

### 📚 Apprentissages clés DBA
- **Indexes PostgreSQL** : Ajout index sur `notes.creator_id` et `assignments.user_id` → requêtes 3x plus rapides
- **Contraintes d'intégrité** : UNIQUE, NOT NULL, CHECK, FOREIGN KEY → données cohérentes
- **Migrations versionnées** : Alembic permet rollback propre en cas de problème
- **Backups automatiques** : Script cron pour dump PostgreSQL quotidien

### 🔮 Améliorations pour prochain projet

**Backend** :
- **Flask Blueprints** au lieu de namespaces pour mieux organiser
- **Celery** pour tâches asynchrones (envoi emails, génération PDF)
- **Redis** pour cache (requêtes fréquentes) et sessions
- **PostgreSQL full-text search** pour recherche avancée
- **Sentry** pour monitoring d'erreurs en production

**Frontend** :
- **React Query** pour gestion cache API + synchronisation
- **Zustand** ou **Jotai** pour state management global léger
- **Vite PWA plugin** pour application installable offline
- **Storybook** pour développer composants en isolation
- **Vitest** pour tests unitaires frontend (actuellement 0%)

**DBA** :
- **Partitioning PostgreSQL** : Table `notes` trop grosse → partition par année
- **Read replicas** : Séparer lectures/écritures pour scalabilité
- **Connection pooling** : PgBouncer pour gérer connexions DB
- **Monitoring** : Prometheus + Grafana pour métriques temps réel

---

## 📊 Tableau récapitulatif par rôle

| Rôle | Charge réelle | Réussites principales | Difficultés majeures | Note/10 |
|------|---------------|----------------------|----------------------|---------|
| **PM** | 15% (24h) | Planification, adaptation Agile, documentation | Sous-estimation Docker, manque de buffer | 8/10 |
| **SCM** | 10% (16h) | 150+ commits propres, branches organisées | Conflits Git, CI/CD manquant | 7/10 |
| **QA** | 25% (40h) | 398 tests (98% coverage), 12 bugs corrigés | Charge sous-estimée, tests UI manuels | 9/10 |
| **Dev/DBA** | 50% (80h) | Backend robuste, frontend fonctionnel, DB optimisée | Docker, CORS, TypeScript null checks | 9/10 |

**Total temps projet** : 4 semaines (160h)

---

## 🎯 Conclusion de la rétrospective

### Ce qui a bien fonctionné ✅
1. **Priorisation MoSCoW** : Focus sur MUST HAVE → MVP complet malgré retards
2. **Tests automatisés** : 98% coverage → confiance pour refactorer
3. **Documentation continue** : README + rapports + commentaires code
4. **Flexibilité Agile** : Ajustements rapides face aux imprévus

### Ce qui peut être amélioré ❌
1. **Estimation initiale** : Prévoir +30% de temps pour imprévus techniques
2. **CI/CD** : GitHub Actions pour tests automatiques à chaque push
3. **Frontend plus tôt** : Intégration dès Sprint 1 pour validation continue
4. **Tests UI automatisés** : Cypress pour réduire charge QA manuelle

### Compétences développées 📈

| Domaine | Niveau avant | Niveau après | Progression |
|---------|--------------|--------------|-------------|
| **Docker** | Débutant | Intermédiaire | +80% |
| **Flask/SQLAlchemy** | Basique | Avancé | +70% |
| **React/TypeScript** | Débutant | Intermédiaire | +75% |
| **Tests automatisés** | Aucun | Avancé | +100% |
| **Architecture logicielle** | Basique | Avancé | +85% |
| **Méthodologie Agile** | Théorique | Pratique | +90% |
| **Git (branches, merges)** | Basique | Intermédiaire | +60% |

---

## 📝 Glossaire des termes utilisés

### **MVC (Model-View-Controller)**
Pattern d'architecture logicielle qui sépare :
- **Model** = Base de données et logique métier (modèles SQLAlchemy)
- **View** = Interface utilisateur (composants React)
- **Controller** = Logique de traitement (routes Flask)

### **API REST vs RESTx**
- **REST** = Architecture d'API utilisant HTTP (GET, POST, PUT, DELETE)
- **Flask-RESTx** = Bibliothèque Flask ajoutant documentation Swagger + validation

### **CI/CD (Continuous Integration / Continuous Deployment)**
Automatisation du cycle de développement :
- **CI** = Tests automatiques à chaque commit
- **CD** = Déploiement automatique en production
- **Exemple** : GitHub Actions lance pytest à chaque `git push`

### **Charge de QA (Quality Assurance)**
Temps/effort consacré aux tests :
- Tests manuels (UI/UX)
- Tests automatisés (pytest, Cypress)
- Rédaction de rapports de bugs
- Validation des corrections

### **Pipeline CI/CD automatisé**
Fichier `.github/workflows/tests.yml` qui lance automatiquement :
```yaml
on: [push, pull_request]
jobs:
  test:
    - run: docker compose up -d
    - run: docker compose exec backend pytest --cov=app
```

### **Tests manuels UI**
Tests effectués par un humain (pas automatisés) :
- Tester le drag & drop
- Vérifier l'affichage sur différents navigateurs
- Tester les animations, toasts, modals
- Vérifier l'accessibilité (clavier, lecteur d'écran)

---

## ✅ Utilisation réelle des concepts dans votre projet

| Concept | Utilisé ? | Preuve |
|---------|-----------|--------|
| **MVC** | ✅ OUI | `models/`, `routes/`, `components/` |
| **API REST** | ✅ OUI | 50 endpoints GET/POST/PUT/DELETE |
| **Flask-RESTx** | ✅ OUI | Swagger UI sur `/api/docs` |
| **Tests automatisés** | ✅ OUI | 398 tests pytest (98% coverage) |
| **CI/CD** | ❌ NON | Mais planifié (GitHub Actions) |
| **QA** | ✅ OUI | 12 bugs détectés, 32 scénarios E2E |
| **Agile (PM)** | ✅ OUI | 4 sprints, Trello, rétrospectives |
| **Git (SCM)** | ✅ OUI | 150+ commits, 5 branches |
| **Docker** | ✅ OUI | docker-compose.yml multi-conteneurs |

---

**✅ Conclusion : Le MVP utilise la majorité des concepts Agile/DevOps standards, avec CI/CD comme amélioration future identifiée.**

**Date** : 3 novembre 2025  
**Auteur** : Mylliah  
**Repository** : [github.com/Mylliah/mvp-sticky_notes](https://github.com/Mylliah/mvp-sticky_notes)
