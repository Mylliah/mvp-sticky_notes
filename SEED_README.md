# 🌱 Scripts de Seed - Données de Test

Ces scripts permettent d'alimenter la base de données avec des données de test pour faciliter le développement frontend.

## 📋 Scripts Disponibles

### `reset_and_seed.sh` - Reset complet (recommandé)
**Réinitialise complètement la base et génère les données de test.**

```bash
./reset_and_seed.sh
```

Étapes :
1. ✅ Supprime toutes les tables
2. ✅ Applique toutes les migrations
3. ✅ Génère les données de test

---

### `seed_test_data.sh` - Seed uniquement
**Génère des données de test sans toucher à la structure.**

```bash
# Ajouter des données (sans supprimer les existantes)
./seed_test_data.sh

# Supprimer et régénérer toutes les données
./seed_test_data.sh --reset
```

---

### Commandes manuelles

```bash
# Appliquer les migrations uniquement
docker compose exec backend flask db upgrade

# Générer les données sans reset
docker compose exec backend python seed_data.py

# Générer avec reset des données (garde la structure)
docker compose exec backend python seed_data.py --reset
```

---

## 👥 Comptes de Test Créés

| Username | Email | Mot de passe | Rôle |
|----------|-------|--------------|------|
| **alice_test** | alice@test.com | password123 | **admin** |
| bob_test | bob@test.com | password123 | user |
| charlie_test | charlie@test.com | password123 | user |
| david_test | david@test.com | password123 | user |
| emma_test | emma@test.com | password123 | user |

### 💡 Recommandation
**Utilisez Alice pour le développement :**
- ✅ Elle est admin (accès à toutes les routes)
- ✅ Elle a tous les contacts (peut assigner à tout le monde)
- ✅ Elle a des notes reçues et envoyées

---

## 📝 Données Générées

### Utilisateurs (5)
- Alice, Bob, Charlie, David, Emma
- Tous avec le mot de passe `password123`

### Contacts (11)
- **Contacts mutuels** : Alice ↔ Bob, Alice ↔ Charlie, Alice ↔ David, Alice ↔ Emma, Bob ↔ Charlie
- **Contact non mutuel** : Bob → David (David n'a pas ajouté Bob)

### Notes (12)
- Notes importantes et normales
- Notes de différents créateurs
- Notes avec contenu court et long
- **1 note orpheline** (sans assignation)

### Assignations (12)
- **États variés** : lu/non lu, en cours/terminé
- **Priorités** : certaines marquées prioritaires par le destinataire
- **Multi-assignations** : certaines notes assignées à plusieurs personnes

### Action Logs (3)
- Exemples de logs d'actions pour l'audit

---

## 🎯 Cas d'Usage

### Tester le frontend
```bash
./reset_and_seed.sh
# Puis ouvrir http://localhost:3001
# Se connecter avec alice@test.com / password123
```

### Ajouter plus de données sans tout supprimer
```bash
./seed_test_data.sh
# (sans --reset)
```

### Repartir de zéro rapidement
```bash
./reset_and_seed.sh
```

---

## 🔧 Personnalisation

Pour modifier les données générées, éditez `backend/seed_data.py` :

- `create_users()` : Ajouter/modifier des utilisateurs
- `create_contacts()` : Définir les relations de contacts
- `create_notes()` : Créer des notes avec différents contenus
- `create_assignments()` : Configurer les assignations

Puis relancez :
```bash
./reset_and_seed.sh
```

---

## ⚠️ Attention

- Ces scripts sont **pour le développement uniquement**
- Ne **jamais** exécuter en production
- Les données générées sont **fictives** et réinitialisables

---

## 🐛 Dépannage

### Erreur "relation already exists"
```bash
# Reset complet
./reset_and_seed.sh
```

### Les migrations ne s'appliquent pas
```bash
# Supprimer et recréer
docker compose exec backend python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all()"
docker compose exec backend flask db upgrade
```

### Les données ne s'affichent pas
```bash
# Vérifier que les données existent
docker compose exec backend python -c "from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); print(f'Users: {User.query.count()}')"
```

---

## 📚 Ressources

- **Frontend** : http://localhost:3001
- **Backend API** : http://localhost:5000
- **Adminer (DB)** : http://localhost:8080
- **Documentation API** : Voir `CURL_COMMANDS.md`
